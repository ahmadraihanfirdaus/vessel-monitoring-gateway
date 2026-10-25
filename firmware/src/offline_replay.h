#ifndef VG_OFFLINE_REPLAY_H
#define VG_OFFLINE_REPLAY_H

#include "offline_state.h"

/* Immutable successful-recovery view. No latest telemetry, credential, IO,
 * delivery receipt, storage mutation or authorization to delete is included. */
typedef struct {
    char device[VG_TELEMETRY_MAX_ID_LEN + 1u];
    uint64_t generation;
    bool degraded;
    size_t event_count;
    vg_offline_event events[VG_OFFLINE_EVENT_CAP];
} vg_recovered_events;

typedef enum {
    VG_REPLAY_INVALID = 0, VG_REPLAY_ENCODED,
    VG_REPLAY_UNSUPPORTED_TYPE, VG_REPLAY_BUFFER_REFUSED
} vg_replay_encode_result;

static inline bool vg_recovered_events_valid(const vg_recovered_events *view)
{
    if (!view || !memchr(view->device, 0, sizeof(view->device)) ||
        !vg_tel_safe_token(view->device, VG_TELEMETRY_MAX_ID_LEN) ||
        view->event_count > VG_OFFLINE_EVENT_CAP ||
        (view->generation == 0u && (view->event_count != 0u || view->degraded))) return false;
    for (size_t i = 0u; i < view->event_count; ++i) {
        const vg_offline_event *record = &view->events[i];
        if (!vg_offline_record_valid(record)) return false;
        for (size_t j = 0u; j < i; ++j)
            if (!strcmp(record->boot, view->events[j].boot) &&
                record->event.event_id == view->events[j].event.event_id) return false;
    }
    return true;
}

static inline bool vg_recovered_events_capture(const vg_offline_state *state,
    bool degraded, vg_recovered_events *out)
{
    if (!out || !vg_offline_valid(state, true) || (degraded && state->generation == 0u) ||
        !vg_offline_disjoint(state, sizeof(*state), out, sizeof(*out))) return false;
    memset(out, 0, sizeof(*out));
    memcpy(out->device, state->device, strlen(state->device) + 1u);
    out->generation = state->generation;
    out->degraded = degraded;
    out->event_count = state->event_count;
    for (size_t i = 0u; i < state->event_count; ++i) out->events[i] = state->events[i];
    return true;
}

/* On BUFFER_REFUSED output is unusable; no state/view is ever mutated. A
 * supported legacy fact uses the original nine fields without invented alarm
 * metadata. A recovery type outside that contract remains explicitly retained. */
static inline vg_replay_encode_result vg_offline_event_json(
    const vg_offline_event *record, const char *device, char *out, size_t capacity)
{
    if (!vg_offline_record_valid(record) || !vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !out || capacity == 0u)
        return VG_REPLAY_INVALID;
    if (capacity > VG_TELEMETRY_JSON_MAX + 1u) capacity = VG_TELEMETRY_JSON_MAX + 1u;
    if (!vg_offline_disjoint(record, sizeof(*record), out, capacity) ||
        !vg_offline_disjoint(device, strlen(device) + 1u, out, capacity)) return VG_REPLAY_INVALID;
    if (record->has_alarm) {
        vg_alarm_transition_t transition = {record->event, record->alarm};
        return vg_alarm_transition_json(&transition, device, record->boot, out, capacity)
            ? VG_REPLAY_ENCODED : VG_REPLAY_BUFFER_REFUSED;
    }
    const vg_journal_event_t *event = &record->event;
    const char *type;
    switch (event->type) {
        case VG_EVENT_ALARM_RAISED: type = "alarm_raised"; break;
        case VG_EVENT_ALARM_ACK: type = "alarm_ack"; break;
        case VG_EVENT_ALARM_CLEARED: type = "alarm_cleared"; break;
        case VG_EVENT_FAULT: type = "fault"; break;
        default: return VG_REPLAY_UNSUPPORTED_TYPE;
    }
    size_t used = 0u;
    return vg_tel_append(out, capacity, &used,
        "{\"schema_version\":\"1.0\",\"device_id\":\"%s\",\"boot_id\":\"%s\","
        "\"event_id\":%" PRIu64 ",\"linked_alarm_id\":%" PRIu64 ",\"source_id\":%" PRIu32 ","
        "\"source_mode\":\"%s\",\"event_type\":\"%s\",\"occurred_at_ms\":%" PRIu64 "}",
        device, record->boot, event->event_id, event->linked_alarm_id, event->source_id,
        vg_source_mode_to_string(event->source_mode), type, event->occurred_at_ms)
        ? VG_REPLAY_ENCODED : VG_REPLAY_BUFFER_REFUSED;
}

static inline vg_replay_encode_result vg_recovered_event_json(
    const vg_recovered_events *view, size_t index, char *out, size_t capacity)
{
    if (!vg_recovered_events_valid(view) || index >= view->event_count || !out || capacity == 0u)
        return VG_REPLAY_INVALID;
    if (capacity > VG_TELEMETRY_JSON_MAX + 1u) capacity = VG_TELEMETRY_JSON_MAX + 1u;
    if (!vg_offline_disjoint(view, sizeof(*view), out, capacity)) return VG_REPLAY_INVALID;
    return vg_offline_event_json(&view->events[index], view->device, out, capacity);
}

typedef enum {
    VG_REPLAY_CHOICE_INVALID = -1, VG_REPLAY_NONE = 0,
    VG_REPLAY_RECOVERED, VG_REPLAY_CURRENT
} vg_replay_choice;

typedef struct {
    size_t recovered_visited;
    size_t current_queued;
    size_t recovered_unpublishable;
    bool prefer_recovered;
} vg_replay_progress;

static inline vg_replay_choice vg_replay_choose(const vg_replay_progress *progress,
    size_t recovered_count, size_t current_count)
{
    if (!progress || recovered_count > VG_OFFLINE_EVENT_CAP || current_count > VG_JOURNAL_CAPACITY ||
        progress->recovered_visited > recovered_count || progress->current_queued > current_count ||
        progress->recovered_unpublishable > progress->recovered_visited) return VG_REPLAY_CHOICE_INVALID;
    bool recovered = progress->recovered_visited < recovered_count;
    bool current = progress->current_queued < current_count;
    if (recovered && (progress->prefer_recovered || !current)) return VG_REPLAY_RECOVERED;
    return current ? VG_REPLAY_CURRENT : VG_REPLAY_NONE;
}

/* Call only after successful transport queue copy, or an explicit unsupported
 * legacy-type report. Queue refusal must not advance. Neither outcome is a
 * delivery ACK or storage-retirement permission. */
static inline bool vg_replay_mark(vg_replay_progress *progress,
    size_t recovered_count, size_t current_count, vg_replay_choice choice, bool unsupported)
{
    if (choice <= VG_REPLAY_NONE || choice != vg_replay_choose(progress, recovered_count, current_count) ||
        (unsupported && choice != VG_REPLAY_RECOVERED)) return false;
    if (choice == VG_REPLAY_RECOVERED) {
        ++progress->recovered_visited;
        if (unsupported) ++progress->recovered_unpublishable;
        progress->prefer_recovered = false;
    } else {
        ++progress->current_queued;
        progress->prefer_recovered = true;
    }
    return true;
}

#endif
