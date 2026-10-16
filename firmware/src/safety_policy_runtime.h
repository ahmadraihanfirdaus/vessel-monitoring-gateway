#ifndef VG_SAFETY_POLICY_RUNTIME_H
#define VG_SAFETY_POLICY_RUNTIME_H

#include <stdbool.h>
#include <stdint.h>

#include "core_alarm.h"
#include "core_event_journal.h"
#include "safety_local_alarm.h"
#include "safety_policy.h"

/*
 * Development-only transaction that converts a local safety-policy condition
 * into a boot-scoped alarm, bounded volatile event, and logical local output.
 * No network/dashboard dependency, persistence, GPIO, physical interlock, or
 * certified priority taxonomy is provided.
 */
typedef struct {
    bool initialized;
    vg_alarm_id_allocator_t alarm_ids;
    vg_event_journal_t journal;
    bool has_alarm;
    vg_alarm_t alarm;
    vg_local_alarm_output_t local_output;
} vg_safety_policy_runtime_t;

static inline bool vg_safety_policy_runtime_init(
    vg_safety_policy_runtime_t *runtime)
{
    if (runtime == NULL) return false;
    vg_safety_policy_runtime_t fresh = {0};
    vg_alarm_id_allocator_init(&fresh.alarm_ids);
    if (!vg_journal_init(&fresh.journal)) return false;
    fresh.initialized = true;
    *runtime = fresh;
    return true;
}

static inline bool vg_safety_policy_runtime_raise(
    vg_safety_policy_runtime_t *runtime,
    const vg_prestart_decision_t *decision,
    uint32_t source_id,
    uint32_t demo_priority_code,
    uint64_t now_ms)
{
    if (runtime == NULL || decision == NULL || !runtime->initialized ||
        runtime->has_alarm || !vg_prestart_decision_is_consistent(decision) ||
        !decision->condition_present || decision->reason_code == VG_SAFETY_REASON_NONE ||
        source_id == 0u || demo_priority_code == 0u) {
        return false;
    }

    vg_safety_policy_runtime_t next = *runtime;
    vg_alarm_t alarm = {0};
    if (!vg_alarm_try_raise(&next.alarm_ids, &alarm,
            source_id, decision->source_mode, demo_priority_code,
            (uint32_t)decision->reason_code, now_ms)) {
        return false;
    }

    uint64_t event_id = 0u;
    if (!vg_journal_append(&next.journal, alarm.id, source_id,
            decision->source_mode, VG_EVENT_ALARM_RAISED,
            now_ms, &event_id)) {
        return false;
    }

    vg_local_alarm_output_t local = {0};
    if (!vg_local_alarm_from_alarm(&alarm, &local)) {
        return false;
    }

    next.alarm = alarm;
    next.has_alarm = true;
    next.local_output = local;
    *runtime = next;
    return event_id != 0u;
}

static inline bool vg_safety_policy_runtime_acknowledge(
    vg_safety_policy_runtime_t *runtime,
    uint64_t now_ms)
{
    if (runtime == NULL || !runtime->initialized || !runtime->has_alarm) {
        return false;
    }

    vg_safety_policy_runtime_t next = *runtime;
    if (!vg_alarm_try_acknowledge(&next.alarm, now_ms)) {
        return false;
    }
    uint64_t event_id = 0u;
    if (!vg_journal_append(&next.journal, next.alarm.id,
            next.alarm.source_id, next.alarm.source_mode,
            VG_EVENT_ALARM_ACK, now_ms, &event_id)) {
        return false;
    }
    if (!vg_local_alarm_from_alarm(&next.alarm, &next.local_output)) {
        return false;
    }
    *runtime = next;
    return event_id != 0u;
}

#endif /* VG_SAFETY_POLICY_RUNTIME_H */
