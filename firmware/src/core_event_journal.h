#ifndef VG_CORE_EVENT_JOURNAL_H
#define VG_CORE_EVENT_JOURNAL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "core_source_mode.h"

/* Volatile and bounded journal foundation. No NVS/flash persistence,
 * power-loss recovery, network replay, guaranteed critical retention,
 * backend event contract or full NET-002 implementation.
 * Reject new events when full: never silently overwrite stored events.
 */
#define VG_JOURNAL_CAPACITY 8u

typedef enum {
    VG_EVENT_UNKNOWN = 0,
    VG_EVENT_ALARM_RAISED,
    VG_EVENT_ALARM_ACK,
    VG_EVENT_ALARM_CLEARED,
    VG_EVENT_FAULT,
    VG_EVENT_RECOVERY
} vg_event_type_t;

typedef struct {
    uint64_t event_id; /* per-journal / per-boot ONLY */
    uint64_t linked_alarm_id; /* zero if no alarm association */
    uint32_t source_id;
    vg_source_mode_t source_mode;
    vg_event_type_t type;
    uint64_t occurred_at_ms; /* monotonic, caller provided */
} vg_journal_event_t;

typedef struct {
    bool initialized;
    bool has_last_time;
    uint64_t next_id;
    uint64_t last_event_ms;
    uint64_t rejected_full;
    size_t count;
    vg_journal_event_t events[VG_JOURNAL_CAPACITY];
} vg_event_journal_t;

static inline bool vg_journal_init(vg_event_journal_t *j)
{
    if (j == NULL) return false;
    *j = (vg_event_journal_t){0};
    j->initialized = true;
    j->next_id = 1;
    return true;
}

static inline bool vg_journal_append(vg_event_journal_t *j,
    uint64_t linked_alarm_id, uint32_t source_id,
    vg_source_mode_t source_mode, vg_event_type_t type,
    uint64_t occurred_at_ms, uint64_t *out_event_id)
{
    if (j == NULL || out_event_id == NULL || !j->initialized ||
        j->next_id == 0 || j->next_id == UINT64_MAX ||
        source_id == 0 ||
        (source_mode != VG_SOURCE_SIMULATION &&
         source_mode != VG_SOURCE_BENCH_TEST) ||
        type < VG_EVENT_ALARM_RAISED || type > VG_EVENT_RECOVERY ||
        (j->has_last_time && occurred_at_ms < j->last_event_ms) ||
        j->count > VG_JOURNAL_CAPACITY) return false;

    if (j->count == VG_JOURNAL_CAPACITY) {
        if (j->rejected_full != UINT64_MAX) ++j->rejected_full;
        return false;
    }
    vg_journal_event_t event = {0};
    event.event_id = j->next_id;
    event.linked_alarm_id = linked_alarm_id;
    event.source_id = source_id;
    event.source_mode = source_mode;
    event.type = type;
    event.occurred_at_ms = occurred_at_ms;
    j->events[j->count++] = event;
    j->next_id++;
    j->last_event_ms = occurred_at_ms;
    j->has_last_time = true;
    *out_event_id = event.event_id;
    return true;
}

static inline bool vg_journal_read(const vg_event_journal_t *j,
                                   size_t index, vg_journal_event_t *out)
{
    if (j == NULL || out == NULL || !j->initialized ||
        j->count > VG_JOURNAL_CAPACITY || index >= j->count)
        return false;
    *out = j->events[index];
    return true;
}

#endif /* VG_CORE_EVENT_JOURNAL_H */
