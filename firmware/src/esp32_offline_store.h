#ifndef VG_ESP32_OFFLINE_STORE_H
#define VG_ESP32_OFFLINE_STORE_H

#include "offline_transaction.h"
#include "offline_replay.h"
#include "offline_retirement.h"

typedef enum {
    VG_STORAGE_RECOVERED = 1, VG_STORAGE_COMMITTED, VG_STORAGE_CRITICAL_FULL,
    VG_STORAGE_UNCHANGED, VG_STORAGE_REJECTED, VG_STORAGE_IO_HALTED
} vg_storage_status;
typedef struct {
    vg_storage_status status;
    uint64_t submitted_sequence;
    uint64_t generation;
    size_t retained_events;
    bool degraded_recovery;
    bool boot_owner_refused;
} vg_storage_completion;

typedef struct {
    uint64_t tag;
    vg_offline_retire_result result;
    uint64_t generation;
    uint64_t confirmed_event_id;
    bool degraded_recovery;
} vg_storage_retirement_completion;

#ifdef ESP_PLATFORM
/* Single startup owner; actual writes happen only on the dedicated worker.
 * No erase/provisioning, no secret data and no network-dependent operation. */
bool vg_storage_start(const char *device, const char *boot);
/* One current boot only. A newer sequence may replace a queued job only when
 * its cumulative journal preserves the entire previously accepted prefix.
 * True means queued, not committed. Failure leaves caller data untouched. */
bool vg_storage_submit(const char *boot, uint64_t sequence, const void *wire,
    size_t length, const vg_event_journal_t *journal);
/* Full metadata is immutable and cumulative within a boot. Once admitted,
 * subsequent jobs cannot revert to the legacy metadata-unavailable interface. */
bool vg_storage_submit_with_alarms(const char *boot, uint64_t sequence, const void *wire,
    size_t length, const vg_event_journal_t *journal, const vg_alarm_journal_t *metadata);
bool vg_storage_take_completion(vg_storage_completion *out);
/* Successful recovery only: zero-wait bounded copy, no NVS IO in caller.
 * Repeated explicit recovery can yield duplicates; never a deletion receipt. */
bool vg_storage_take_recovered_events(vg_recovered_events *out);
bool vg_storage_request_recovery(void);
/* Continuous candidate only; retained selftest returns false. Receipt copied
 * with zero wait; actual authentication and durable IO happen in the worker. */
bool vg_storage_submit_receipt(uint64_t tag, const vg_offline_event *record,
    int status, const void *receipt, size_t receipt_length);
bool vg_storage_take_retirement(vg_storage_retirement_completion *out);
#endif

#endif
