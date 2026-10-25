#ifndef VG_ALARM_TRANSITION_H
#define VG_ALARM_TRANSITION_H

#include "core_alarm.h"
#include "core_event_journal.h"
#include "telemetry_contract.h"

/* Immutable event-time snapshot, never reconstructed from the current alarm. */
typedef struct {
    vg_journal_event_t event;
    vg_alarm_t alarm;
} vg_alarm_transition_t;

typedef struct {
    size_t count;
    vg_alarm_transition_t entries[VG_JOURNAL_CAPACITY];
} vg_alarm_journal_t;

static inline bool vg_alarm_regions_disjoint(const void *a, size_t an, const void *b, size_t bn)
{
    uintptr_t x = (uintptr_t)a, y = (uintptr_t)b;
    return x <= y ? an <= y - x : bn <= x - y;
}

static inline bool vg_alarm_transition_valid(const vg_alarm_transition_t *transition)
{
    if (!transition || !vg_alarm_is_consistent(&transition->alarm)) return false;
    const vg_alarm_t *alarm = &transition->alarm;
    const vg_journal_event_t *event = &transition->event;
    if (event->event_id == 0u || event->linked_alarm_id != alarm->id ||
        event->source_id != alarm->source_id || event->source_mode != alarm->source_mode) return false;
    switch (event->type) {
        case VG_EVENT_ALARM_RAISED:
            return alarm->state == VG_ALARM_STATE_ACTIVE_UNACK && event->occurred_at_ms == alarm->raised_at;
        case VG_EVENT_ALARM_ACK:
            return alarm->state == VG_ALARM_STATE_ACTIVE_ACK && event->occurred_at_ms == alarm->acknowledged_at;
        case VG_EVENT_ALARM_CLEARED:
            return alarm->state == VG_ALARM_STATE_CLEARED && event->occurred_at_ms == alarm->cleared_at;
        default:
            return false;
    }
}

static inline bool vg_alarm_transition_event_equal(const vg_journal_event_t *a,
    const vg_journal_event_t *b)
{
    return a && b && a->event_id == b->event_id && a->linked_alarm_id == b->linked_alarm_id &&
        a->source_id == b->source_id && a->source_mode == b->source_mode &&
        a->type == b->type && a->occurred_at_ms == b->occurred_at_ms;
}

static inline bool vg_alarm_metadata_equal(const vg_alarm_t *x, const vg_alarm_t *y)
{
    if (!vg_alarm_is_consistent(x) || !vg_alarm_is_consistent(y)) return false;
    return x->id == y->id && x->source_id == y->source_id && x->source_mode == y->source_mode &&
        x->priority_code == y->priority_code && x->reason_code == y->reason_code &&
        x->state == y->state && x->condition_active == y->condition_active &&
        x->acknowledged == y->acknowledged && x->raised_at == y->raised_at &&
        x->has_acknowledged_at == y->has_acknowledged_at && x->has_cleared_at == y->has_cleared_at &&
        (!x->has_acknowledged_at || x->acknowledged_at == y->acknowledged_at) &&
        (!x->has_cleared_at || x->cleared_at == y->cleared_at);
}

static inline bool vg_alarm_transition_equal(const vg_alarm_transition_t *a,
    const vg_alarm_transition_t *b)
{
    return vg_alarm_transition_valid(a) && vg_alarm_transition_valid(b) &&
        vg_alarm_transition_event_equal(&a->event, &b->event) && vg_alarm_metadata_equal(&a->alarm, &b->alarm);
}

static inline bool vg_alarm_journal_matches(const vg_alarm_journal_t *metadata,
    const vg_event_journal_t *journal)
{
    if (!metadata || !journal || !journal->initialized || journal->count > VG_JOURNAL_CAPACITY ||
        metadata->count != journal->count) return false;
    for (size_t i = 0u; i < metadata->count; ++i)
        if (!vg_alarm_transition_valid(&metadata->entries[i]) ||
            !vg_alarm_transition_event_equal(&metadata->entries[i].event, &journal->events[i]) ||
            (i != 0u && (journal->events[i].event_id <= journal->events[i - 1u].event_id ||
                journal->events[i].occurred_at_ms < journal->events[i - 1u].occurred_at_ms))) return false;
    if (metadata->count != 0u) {
        const vg_journal_event_t *last = &journal->events[metadata->count - 1u];
        if (!journal->has_last_time || journal->last_event_ms != last->occurred_at_ms ||
            last->event_id == UINT64_MAX || journal->next_id != last->event_id + 1u) return false;
    }
    return true;
}

static inline bool vg_alarm_journal_follows(const vg_alarm_journal_t *old,
    const vg_alarm_journal_t *next)
{
    if (!old || !next || old->count > VG_JOURNAL_CAPACITY || next->count > VG_JOURNAL_CAPACITY ||
        next->count < old->count) return false;
    for (size_t i = 0u; i < next->count; ++i)
        if (!vg_alarm_transition_valid(&next->entries[i]) ||
            (i < old->count && !vg_alarm_transition_equal(&old->entries[i], &next->entries[i]))) return false;
    return true;
}

/* Single owner. Validate before appending so metadata and event publish together.
 * Full journal still increments its existing explicit refusal counter. */
static inline bool vg_alarm_journal_append(vg_event_journal_t *journal,
    vg_alarm_journal_t *metadata, const vg_alarm_t *alarm, vg_event_type_t type,
    uint64_t now, uint64_t *event_id)
{
    if (!event_id || !alarm || !vg_alarm_journal_matches(metadata, journal)) return false;
    if (!vg_alarm_regions_disjoint(metadata, sizeof(*metadata), journal, sizeof(*journal)) ||
        !vg_alarm_regions_disjoint(event_id, sizeof(*event_id), journal, sizeof(*journal)) ||
        !vg_alarm_regions_disjoint(event_id, sizeof(*event_id), metadata, sizeof(*metadata)) ||
        !vg_alarm_regions_disjoint(event_id, sizeof(*event_id), alarm, sizeof(*alarm))) return false;
    vg_alarm_transition_t next = {0};
    next.alarm = *alarm;
    if (!next.alarm.has_acknowledged_at) next.alarm.acknowledged_at = 0u;
    if (!next.alarm.has_cleared_at) next.alarm.cleared_at = 0u;
    next.event = (vg_journal_event_t){journal->next_id, alarm->id, alarm->source_id,
        alarm->source_mode, type, now};
    if (!vg_alarm_transition_valid(&next)) return false;
    uint64_t appended;
    if (!vg_journal_append(journal, alarm->id, alarm->source_id, alarm->source_mode, type, now, &appended)) return false;
    metadata->entries[metadata->count++] = next;
    *event_id = appended;
    return true;
}

static inline const char *vg_alarm_transition_state_name(vg_alarm_state_t state)
{
    switch (state) {
        case VG_ALARM_STATE_ACTIVE_UNACK: return "active_unack";
        case VG_ALARM_STATE_ACTIVE_ACK: return "active_ack";
        case VG_ALARM_STATE_CLEARED: return "cleared";
        default: return NULL;
    }
}

/* False means output is unusable; caller supplies a separate working buffer. */
static inline bool vg_alarm_transition_json(const vg_alarm_transition_t *transition,
    const char *device, const char *boot, char *out, size_t capacity)
{
    if (!vg_alarm_transition_valid(transition) || !vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN) || !out || capacity == 0u) return false;
    if (capacity > VG_TELEMETRY_JSON_MAX + 1u) capacity = VG_TELEMETRY_JSON_MAX + 1u;
    if (!vg_alarm_regions_disjoint(out, capacity, transition, sizeof(*transition)) ||
        !vg_alarm_regions_disjoint(out, capacity, device, strlen(device) + 1u) ||
        !vg_alarm_regions_disjoint(out, capacity, boot, strlen(boot) + 1u)) return false;
    const vg_alarm_t *a = &transition->alarm;
    const vg_journal_event_t *e = &transition->event;
    const char *type = e->type == VG_EVENT_ALARM_RAISED ? "alarm_raised" :
        (e->type == VG_EVENT_ALARM_ACK ? "alarm_ack" : "alarm_cleared");
    size_t used = 0u;
    if (!vg_tel_append(out, capacity, &used,
        "{\"schema_version\":\"1.1\",\"device_id\":\"%s\",\"boot_id\":\"%s\","
        "\"event_id\":%" PRIu64 ",\"linked_alarm_id\":%" PRIu64 ",\"source_id\":%" PRIu32 ","
        "\"source_mode\":\"%s\",\"event_type\":\"%s\",\"occurred_at_ms\":%" PRIu64 ","
        "\"alarm\":{\"priority_code\":%" PRIu32 ",\"reason_code\":%" PRIu32 ",\"state\":\"%s\","
        "\"raised_at_ms\":%" PRIu64 ",\"acknowledged_at_ms\":",
        device, boot, e->event_id, e->linked_alarm_id, e->source_id,
        vg_source_mode_to_string(e->source_mode), type, e->occurred_at_ms,
        a->priority_code, a->reason_code, vg_alarm_transition_state_name(a->state), a->raised_at)) return false;
    if (a->has_acknowledged_at) {
        if (!vg_tel_append(out, capacity, &used, "%" PRIu64, a->acknowledged_at)) return false;
    } else if (!vg_tel_append(out, capacity, &used, "null")) return false;
    if (!vg_tel_append(out, capacity, &used, ",\"cleared_at_ms\":")) return false;
    if (a->has_cleared_at) {
        if (!vg_tel_append(out, capacity, &used, "%" PRIu64, a->cleared_at)) return false;
    } else if (!vg_tel_append(out, capacity, &used, "null")) return false;
    return vg_tel_append(out, capacity, &used, "}}");
}

#endif
