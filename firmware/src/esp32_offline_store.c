#ifdef ESP_PLATFORM

#include "esp32_offline_store.h"
#ifdef VG_CONTINUOUS_SIMULATION
#include "esp32_network_client.h"
#endif
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
#ifdef VG_CONTINUOUS_SIMULATION
typedef struct {
    uint64_t tag;
    vg_offline_event record;
    int status;
    uint8_t receipt[VG_EVENT_RECEIPT_LENGTH];
} receipt_job;
#endif
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
    bool recovered_once, boot_owner_refused;
    QueueHandle_t jobs, results, recovered;
    SemaphoreHandle_t lock;
    EventGroupHandle_t status;
    TaskHandle_t task;
    storage_job active, staging;
    vg_recovered_events recovered_view;
#ifdef VG_CONTINUOUS_SIMULATION
    QueueHandle_t receipts, retirements;
    receipt_job receipt_active, receipt_staging;
    vg_event_journal_t receipt_prefix;
    vg_alarm_journal_t receipt_metadata;
    bool receipt_has_metadata;
    uint64_t confirmed_floor;
    vg_offline_event prefix_working;
    char retirement_wire[1024];
#endif
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
    if (!vg_offline_recover(&ctx->transaction, io, ctx->device)) return false;
    ctx->boot_owner_refused = !vg_offline_recovery_owner_valid(&ctx->transaction.current, ctx->boot, ctx->recovered_once);
    if (ctx->boot_owner_refused) return false;
#ifdef VG_CONTINUOUS_SIMULATION
    if (xSemaphoreTake(ctx->lock, portMAX_DELAY) != pdTRUE) return false;
    if (!strcmp(ctx->transaction.current.latest_boot, ctx->boot) &&
        ctx->transaction.current.confirmed_event_id > ctx->confirmed_floor)
        ctx->confirmed_floor = ctx->transaction.current.confirmed_event_id;
    bool reconciled = vg_offline_strip_confirmed_prefix(&ctx->accepted_journal,
        ctx->accepted_has_metadata ? &ctx->accepted_metadata : NULL,
        ctx->boot, ctx->confirmed_floor, &ctx->prefix_working);
    (void)xSemaphoreGive(ctx->lock);
    if (!reconciled) return false;
#endif
    if (!vg_recovered_events_capture(&ctx->transaction.current,
        ctx->transaction.degraded, &ctx->recovered_view) ||
        xQueueOverwrite(ctx->recovered, &ctx->recovered_view) != pdTRUE) return false;
    ctx->recovered_once = true;
    return true;
}
static void emit(storage_client *ctx, vg_storage_status status, uint64_t sequence)
{
    vg_storage_completion result = {status, sequence, ctx->transaction.current.generation,
        ctx->transaction.current.event_count, ctx->transaction.degraded, ctx->boot_owner_refused};
    /* Only this worker may wait; acquisition uses zero-wait APIs. */
    (void)xQueueSend(ctx->results, &result, portMAX_DELAY);
}
#ifdef VG_CONTINUOUS_SIMULATION
static bool verify_receipt(void *context, const void *body, size_t length, int status,
    const void *receipt, size_t receipt_length, uint8_t digest[32])
{
    (void)context;
    return vg_net_verify_event_receipt(body, length, status, receipt, receipt_length, digest);
}

static bool process_receipt(storage_client *ctx)
{
    if (strcmp(ctx->transaction.current.latest_boot, ctx->boot) ||
        xQueueReceive(ctx->receipts, &ctx->receipt_active, 0) != pdTRUE) return false;
    vg_offline_retire_result result = VG_RETIRE_IO_HALTED;
    if (xSemaphoreTake(ctx->lock, portMAX_DELAY) == pdTRUE) {
        ctx->receipt_prefix = ctx->accepted_journal;
        ctx->receipt_metadata = ctx->accepted_metadata;
        ctx->receipt_has_metadata = ctx->accepted_has_metadata;
        (void)xSemaphoreGive(ctx->lock);
        const vg_event_receipt_verifier verifier = {NULL, verify_receipt};
        result = vg_offline_retire(&ctx->transaction, ctx->boot,
            &ctx->receipt_active.record, &ctx->receipt_prefix,
            ctx->receipt_has_metadata ? &ctx->receipt_metadata : NULL, &verifier,
            ctx->receipt_active.status, ctx->receipt_active.receipt, sizeof(ctx->receipt_active.receipt),
            ctx->retirement_wire, sizeof(ctx->retirement_wire));
    }
    if (result == VG_RETIRE_COMMITTED || result == VG_RETIRE_ALREADY_CONFIRMED) {
        if (xSemaphoreTake(ctx->lock, portMAX_DELAY) != pdTRUE) result = VG_RETIRE_IO_HALTED;
        else {
            if (ctx->transaction.current.confirmed_event_id > ctx->confirmed_floor)
                ctx->confirmed_floor = ctx->transaction.current.confirmed_event_id;
            if (!vg_offline_strip_confirmed_prefix(&ctx->accepted_journal,
                ctx->accepted_has_metadata ? &ctx->accepted_metadata : NULL,
                ctx->boot, ctx->confirmed_floor, &ctx->prefix_working)) result = VG_RETIRE_IO_HALTED;
            (void)xSemaphoreGive(ctx->lock);
        }
    }
    if (result == VG_RETIRE_IO_HALTED) {
        ctx->transaction.halted = true;
        xEventGroupClearBits(ctx->status, STORAGE_READY);
        xEventGroupSetBits(ctx->status, STORAGE_HALTED);
    }
    vg_storage_retirement_completion completion = {ctx->receipt_active.tag, result,
        ctx->transaction.current.generation, ctx->transaction.current.confirmed_event_id, ctx->transaction.degraded};
    (void)xQueueSend(ctx->retirements, &completion, portMAX_DELAY);
    memset(&ctx->receipt_active, 0, sizeof(ctx->receipt_active));
    memset(ctx->retirement_wire, 0, sizeof(ctx->retirement_wire));
    return true;
}
#endif
static void storage_worker(void *context)
{
    storage_client *ctx = context;
    bool ready = recover(ctx);
    if (ready) xEventGroupSetBits(ctx->status, STORAGE_READY);
    else xEventGroupSetBits(ctx->status, STORAGE_HALTED);
    emit(ctx, ready ? VG_STORAGE_RECOVERED : VG_STORAGE_IO_HALTED, 0u);
    bool retry_active = false;
#ifdef VG_CONTINUOUS_SIMULATION
    bool prefer_receipt = true;
#endif
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
#ifdef VG_CONTINUOUS_SIMULATION
        if (prefer_receipt && process_receipt(ctx)) {
            prefer_receipt = false;
            if (ctx->transaction.halted) ready = false;
            continue;
        }
#endif
        /* A queued newer cumulative journal safely supersedes the failed job.
         * Otherwise explicit recovery retries the retained uncertain write. */
        if (xQueueReceive(ctx->jobs, &ctx->active, retry_active ? 0u : 1u) != pdTRUE && !retry_active) {
#ifdef VG_CONTINUOUS_SIMULATION
            prefer_receipt = true;
#endif
            continue;
        }
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
#ifdef VG_CONTINUOUS_SIMULATION
        prefer_receipt = true;
#endif
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
#ifdef VG_CONTINUOUS_SIMULATION
    ctx->receipts = xQueueCreate(1u, sizeof(receipt_job));
    ctx->retirements = xQueueCreate(1u, sizeof(vg_storage_retirement_completion));
#endif
    ctx->lock = xSemaphoreCreateMutex();
    ctx->status = xEventGroupCreate();
    if (!ctx->jobs || !ctx->results || !ctx->recovered || !ctx->lock || !ctx->status ||
#ifdef VG_CONTINUOUS_SIMULATION
        !ctx->receipts || !ctx->retirements ||
#endif
        xTaskCreate(storage_worker, "vgw_storage", STORAGE_STACK, ctx, 1u, &ctx->task) != pdPASS) {
        if (ctx->jobs) vQueueDelete(ctx->jobs);
        if (ctx->results) vQueueDelete(ctx->results);
        if (ctx->recovered) vQueueDelete(ctx->recovered);
#ifdef VG_CONTINUOUS_SIMULATION
        if (ctx->receipts) vQueueDelete(ctx->receipts);
        if (ctx->retirements) vQueueDelete(ctx->retirements);
#endif
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
        !vg_offline_journal_follows(journal, journal) ||
        (metadata && !vg_alarm_journal_matches(metadata, journal)) ||
        (storage->accepted_has_metadata && !metadata) ||
        (metadata && !storage->accepted_has_metadata && storage->accepted_journal.count != 0u)) {
        (void)xSemaphoreGive(storage->lock);
        return false;
    }
    memset(&storage->staging, 0, sizeof(storage->staging));
    storage->staging.journal = *journal;
    storage->staging.has_metadata = metadata != NULL;
    if (metadata) storage->staging.metadata = *metadata;
    bool normalized = true;
#ifdef VG_CONTINUOUS_SIMULATION
    normalized = vg_offline_strip_confirmed_prefix(&storage->staging.journal,
        metadata ? &storage->staging.metadata : NULL, boot, storage->confirmed_floor, &storage->prefix_working);
#endif
    if (!normalized || !vg_offline_journal_follows(&storage->accepted_journal, &storage->staging.journal) ||
        (storage->accepted_has_metadata && !vg_alarm_journal_follows(&storage->accepted_metadata, &storage->staging.metadata))) {
        memset(&storage->staging, 0, sizeof(storage->staging));
        (void)xSemaphoreGive(storage->lock);
        return false;
    }
    memcpy(storage->staging.boot, boot, strlen(boot) + 1u);
    storage->staging.sequence = sequence;
    storage->staging.length = length;
    memcpy(storage->staging.wire, wire, length);
    /* The one-item queue keeps newest state, never dropping a critical prefix. */
    bool submitted = xQueueOverwrite(storage->jobs, &storage->staging) == pdTRUE;
    if (submitted) {
        storage->has_sequence = true;
        storage->last_sequence = sequence;
        storage->accepted_journal = storage->staging.journal;
        storage->accepted_has_metadata = metadata != NULL;
        if (metadata) storage->accepted_metadata = storage->staging.metadata;
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

bool vg_storage_submit_receipt(uint64_t tag, const vg_offline_event *record,
    int status, const void *receipt, size_t receipt_length)
{
#ifdef VG_CONTINUOUS_SIMULATION
    if (!storage || !tag || (xEventGroupGetBits(storage->status) & STORAGE_HALTED) ||
        !vg_offline_record_valid(record) || !receipt || receipt_length != VG_EVENT_RECEIPT_LENGTH ||
        (status != 200 && status != 201) || xSemaphoreTake(storage->lock, 0) != pdTRUE) return false;
    bool admissible = vg_offline_receipt_queue_admissible(&storage->accepted_journal,
        storage->accepted_has_metadata ? &storage->accepted_metadata : NULL,
        storage->boot, storage->confirmed_floor, record);
    bool queued = false;
    if (admissible) {
        memset(&storage->receipt_staging, 0, sizeof(storage->receipt_staging));
        storage->receipt_staging.tag = tag;
        storage->receipt_staging.record = *record;
        storage->receipt_staging.status = status;
        memcpy(storage->receipt_staging.receipt, receipt, receipt_length);
        queued = xQueueSend(storage->receipts, &storage->receipt_staging, 0) == pdTRUE;
        memset(&storage->receipt_staging, 0, sizeof(storage->receipt_staging));
    }
    (void)xSemaphoreGive(storage->lock);
    return queued;
#else
    (void)tag; (void)record; (void)status; (void)receipt; (void)receipt_length;
    return false; /* Retained selftest never enables automatic retirement. */
#endif
}

bool vg_storage_take_retirement(vg_storage_retirement_completion *out)
{
#ifdef VG_CONTINUOUS_SIMULATION
    return storage && out && xQueueReceive(storage->retirements, out, 0) == pdTRUE;
#else
    (void)out;
    return false;
#endif
}

#endif
