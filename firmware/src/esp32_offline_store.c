#ifdef ESP_PLATFORM

#include "esp32_offline_store.h"
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "nvs.h"
#include "nvs_flash.h"

#define STORAGE_READY BIT0
#define STORAGE_HALTED BIT1
#define STORAGE_STACK 4096u

typedef struct {
    char boot[VG_TELEMETRY_MAX_ID_LEN + 1u];
    uint64_t sequence;
    size_t length;
    uint8_t wire[VG_OFFLINE_WIRE_MAX];
    vg_event_journal_t journal;
    bool has_metadata;
    vg_alarm_journal_t metadata;
} storage_job;
typedef struct {
    char device[VG_TELEMETRY_MAX_ID_LEN + 1u];
    char boot[VG_TELEMETRY_MAX_ID_LEN + 1u];
    bool has_sequence;
    uint64_t last_sequence;
    vg_event_journal_t accepted_journal;
    bool accepted_has_metadata;
    vg_alarm_journal_t accepted_metadata;
    nvs_handle_t handle;
    bool opened;
    QueueHandle_t jobs, results, recovered;
    SemaphoreHandle_t lock;
    EventGroupHandle_t status;
    TaskHandle_t task;
    storage_job active, staging;
    vg_recovered_events recovered_view;
    vg_offline_transaction transaction;
} storage_client;

static storage_client *storage;
static const char *slot_key(unsigned index) { return index == 0u ? "state0" : "state1"; }

static vg_offline_read_result read_slot(void *context, unsigned index,
    uint8_t *out, size_t capacity, size_t *length)
{
    storage_client *ctx = context;
    size_t needed = 0u;
    esp_err_t result = nvs_get_blob(ctx->handle, slot_key(index), NULL, &needed);
    if (result == ESP_ERR_NVS_NOT_FOUND) return VG_OFFLINE_READ_ABSENT;
    if (result == ESP_ERR_NVS_TYPE_MISMATCH) return VG_OFFLINE_READ_INVALID;
    if (result != ESP_OK) return VG_OFFLINE_READ_ERROR;
    if (needed == 0u || needed > capacity) return VG_OFFLINE_READ_INVALID;
    result = nvs_get_blob(ctx->handle, slot_key(index), out, &needed);
    if (result != ESP_OK || needed > capacity) return VG_OFFLINE_READ_ERROR;
    *length = needed;
    return VG_OFFLINE_READ_READY;
}
static bool write_slot(void *context, unsigned index, const uint8_t *raw, size_t length)
{
    storage_client *ctx = context;
    return nvs_set_blob(ctx->handle, slot_key(index), raw, length) == ESP_OK;
}
static bool commit_slots(void *context)
{
    storage_client *ctx = context;
    return nvs_commit(ctx->handle) == ESP_OK;
}
static bool recover(storage_client *ctx)
{
    /* No erase-on-error and no read/write handle reused after uncertain IO. */
    if (ctx->opened) { nvs_close(ctx->handle); ctx->opened = false; }
    if (nvs_flash_init() != ESP_OK || nvs_open("vgw_state", NVS_READWRITE, &ctx->handle) != ESP_OK) return false;
    ctx->opened = true;
    vg_offline_io io = {ctx, read_slot, write_slot, commit_slots};
    if (!vg_offline_recover(&ctx->transaction, io, ctx->device) ||
        !vg_recovered_events_capture(&ctx->transaction.current,
            ctx->transaction.degraded, &ctx->recovered_view)) return false;
    return xQueueOverwrite(ctx->recovered, &ctx->recovered_view) == pdTRUE;
}
static void emit(storage_client *ctx, vg_storage_status status, uint64_t sequence)
{
    vg_storage_completion result = {status, sequence, ctx->transaction.current.generation,
        ctx->transaction.current.event_count, ctx->transaction.degraded};
    /* Only this worker may wait; acquisition uses zero-wait APIs. */
    (void)xQueueSend(ctx->results, &result, portMAX_DELAY);
}
static void storage_worker(void *context)
{
    storage_client *ctx = context;
    bool ready = recover(ctx);
    if (ready) xEventGroupSetBits(ctx->status, STORAGE_READY);
    else xEventGroupSetBits(ctx->status, STORAGE_HALTED);
    emit(ctx, ready ? VG_STORAGE_RECOVERED : VG_STORAGE_IO_HALTED, 0u);
    bool retry_active = false;
    for (;;) {
        if (ulTaskNotifyTake(pdTRUE, 0) != 0u) {
            xEventGroupClearBits(ctx->status, STORAGE_READY);
            ready = recover(ctx);
            if (ready) {
                xEventGroupClearBits(ctx->status, STORAGE_HALTED);
                xEventGroupSetBits(ctx->status, STORAGE_READY);
            } else xEventGroupSetBits(ctx->status, STORAGE_HALTED);
            emit(ctx, ready ? VG_STORAGE_RECOVERED : VG_STORAGE_IO_HALTED, 0u);
        }
        if (!ready) { vTaskDelay(1u); continue; }
        /* A queued newer cumulative journal safely supersedes the failed job.
         * Otherwise explicit recovery retries the retained uncertain write. */
        if (xQueueReceive(ctx->jobs, &ctx->active, retry_active ? 0u : 1u) != pdTRUE && !retry_active) continue;
        retry_active = false;
        vg_offline_merge_result result = ctx->active.has_metadata
            ? vg_offline_merge_with_alarms(&ctx->transaction.current, ctx->active.boot, ctx->active.sequence,
                ctx->active.wire, ctx->active.length, &ctx->active.journal, &ctx->active.metadata, &ctx->transaction.candidate)
            : vg_offline_merge(&ctx->transaction.current, ctx->active.boot, ctx->active.sequence,
                ctx->active.wire, ctx->active.length, &ctx->active.journal, &ctx->transaction.candidate);
        vg_storage_status status = VG_STORAGE_REJECTED;
        if (result == VG_OFFLINE_UNCHANGED) status = VG_STORAGE_UNCHANGED;
        else if (result == VG_OFFLINE_READY || result == VG_OFFLINE_CRITICAL_FULL) {
            if (vg_offline_publish(&ctx->transaction)) {
                status = result == VG_OFFLINE_CRITICAL_FULL ? VG_STORAGE_CRITICAL_FULL : VG_STORAGE_COMMITTED;
            } else {
                ready = false;
                xEventGroupClearBits(ctx->status, STORAGE_READY);
                xEventGroupSetBits(ctx->status, STORAGE_HALTED);
                retry_active = true;
                status = VG_STORAGE_IO_HALTED;
            }
        }
        emit(ctx, status, ctx->active.sequence);
        if (!retry_active) memset(&ctx->active, 0, sizeof(ctx->active));
    }
}

bool vg_storage_start(const char *device, const char *boot)
{
    if (storage || !vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN)) return false;
    storage_client *ctx = calloc(1u, sizeof(*ctx));
    if (!ctx) return false;
    memcpy(ctx->device, device, strlen(device) + 1u);
    memcpy(ctx->boot, boot, strlen(boot) + 1u);
    (void)vg_journal_init(&ctx->accepted_journal);
    ctx->jobs = xQueueCreate(1u, sizeof(storage_job));
    ctx->results = xQueueCreate(2u, sizeof(vg_storage_completion));
    ctx->recovered = xQueueCreate(1u, sizeof(vg_recovered_events));
    ctx->lock = xSemaphoreCreateMutex();
    ctx->status = xEventGroupCreate();
    if (!ctx->jobs || !ctx->results || !ctx->recovered || !ctx->lock || !ctx->status ||
        xTaskCreate(storage_worker, "vgw_storage", STORAGE_STACK, ctx, 1u, &ctx->task) != pdPASS) {
        if (ctx->jobs) vQueueDelete(ctx->jobs);
        if (ctx->results) vQueueDelete(ctx->results);
        if (ctx->recovered) vQueueDelete(ctx->recovered);
        if (ctx->lock) vSemaphoreDelete(ctx->lock);
        if (ctx->status) vEventGroupDelete(ctx->status);
        free(ctx);
        return false;
    }
    storage = ctx;
    return true;
}

static bool submit_job(const char *boot, uint64_t sequence, const void *wire,
    size_t length, const vg_event_journal_t *journal, const vg_alarm_journal_t *metadata)
{
    if (!storage || (xEventGroupGetBits(storage->status) & STORAGE_HALTED) ||
        !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN) || !wire || length == 0u ||
        strcmp(storage->boot, boot) || length > VG_OFFLINE_WIRE_MAX || !journal ||
        xSemaphoreTake(storage->lock, 0) != pdTRUE) return false;
    if ((storage->has_sequence && sequence <= storage->last_sequence) ||
        !vg_offline_journal_follows(&storage->accepted_journal, journal) ||
        (metadata && !vg_alarm_journal_matches(metadata, journal)) ||
        (storage->accepted_has_metadata && (!metadata ||
            !vg_alarm_journal_follows(&storage->accepted_metadata, metadata))) ||
        (metadata && !storage->accepted_has_metadata && storage->accepted_journal.count != 0u)) {
        (void)xSemaphoreGive(storage->lock);
        return false;
    }
    memset(&storage->staging, 0, sizeof(storage->staging));
    memcpy(storage->staging.boot, boot, strlen(boot) + 1u);
    storage->staging.sequence = sequence;
    storage->staging.length = length;
    memcpy(storage->staging.wire, wire, length);
    storage->staging.journal = *journal;
    storage->staging.has_metadata = metadata != NULL;
    if (metadata) storage->staging.metadata = *metadata;
    /* The one-item queue keeps newest state, never dropping a critical prefix. */
    bool submitted = xQueueOverwrite(storage->jobs, &storage->staging) == pdTRUE;
    if (submitted) {
        storage->has_sequence = true;
        storage->last_sequence = sequence;
        storage->accepted_journal = *journal;
        storage->accepted_has_metadata = metadata != NULL;
        if (metadata) storage->accepted_metadata = *metadata;
    }
    memset(&storage->staging, 0, sizeof(storage->staging));
    (void)xSemaphoreGive(storage->lock);
    return submitted;
}
bool vg_storage_submit(const char *boot, uint64_t sequence, const void *wire,
    size_t length, const vg_event_journal_t *journal)
{
    return submit_job(boot, sequence, wire, length, journal, NULL);
}
bool vg_storage_submit_with_alarms(const char *boot, uint64_t sequence, const void *wire,
    size_t length, const vg_event_journal_t *journal, const vg_alarm_journal_t *metadata)
{
    return metadata && submit_job(boot, sequence, wire, length, journal, metadata);
}
bool vg_storage_take_completion(vg_storage_completion *out)
{
    return storage && out && xQueueReceive(storage->results, out, 0) == pdTRUE;
}
bool vg_storage_take_recovered_events(vg_recovered_events *out)
{
    return storage && out && xQueueReceive(storage->recovered, out, 0) == pdTRUE;
}
bool vg_storage_request_recovery(void)
{
    return storage && xTaskNotifyGive(storage->task) == pdPASS;
}

#endif
