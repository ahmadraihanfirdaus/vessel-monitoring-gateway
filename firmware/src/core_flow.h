#ifndef VG_CORE_FLOW_H
#define VG_CORE_FLOW_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "core_alarm.h"
#include "core_diagnostics.h"
#include "core_event_journal.h"
#include "core_scheduler.h"

/* Development-only orchestrator for caller-injected SIMULATION/BENCH_TEST samples.
 * Single channel, single writer, single boot; NOT an acquisition loop.
 * There are no GPIO operations, network calls, delays, NVS, or marine controls.
 * Alarm priority/reason are opaque caller-specified demo codes, not approved policy.
 * All times use the same caller-provided monotonic millisecond clock.
 * Event journal is volatile and rejects inserts at capacity; failed transitions
 * roll back the scheduler, diagnostic state, alarm, allocator and journal.
 */
typedef enum {
    VG_FLOW_REJECTED = 0,
    VG_FLOW_WAIT,
    VG_FLOW_PROCESSED,
    VG_FLOW_TIME_REGRESSION,
    VG_FLOW_EXHAUSTED,
    VG_FLOW_JOURNAL_FULL
} vg_flow_result_t;

typedef struct {
    bool initialized;
    uint32_t source_id;
    vg_source_mode_t source_mode;
    uint32_t demo_priority_code;
    uint32_t demo_reason_code;
    vg_scheduler_t scheduler;
    vg_diagnostic_t diagnostic;
    vg_alarm_id_allocator_t alarm_ids;
    bool has_alarm;
    vg_alarm_t last_alarm;
    vg_event_journal_t journal;
} vg_core_flow_t;

static inline bool vg_flow_init(vg_core_flow_t *flow,
                                uint32_t source_id,
                                vg_source_mode_t source_mode,
                                uint32_t demo_priority_code,
                                uint32_t demo_reason_code,
                                uint64_t interval_ms,
                                uint64_t first_due_ms)
{
    if (flow == NULL || source_id == 0 || demo_priority_code == 0 ||
        demo_reason_code == 0 ||
        (source_mode != VG_SOURCE_SIMULATION &&
         source_mode != VG_SOURCE_BENCH_TEST)) return false;

    vg_core_flow_t fresh = {0};
    if (!vg_scheduler_init(&fresh.scheduler, interval_ms, first_due_ms) ||
        !vg_journal_init(&fresh.journal)) return false;
    vg_alarm_id_allocator_init(&fresh.alarm_ids);
    fresh.initialized = true;
    fresh.source_id = source_id;
    fresh.source_mode = source_mode;
    fresh.demo_priority_code = demo_priority_code;
    fresh.demo_reason_code = demo_reason_code;
    *flow = fresh;
    return true;
}

/* Due-time processing; diagnostics and alarm transitions are transactional with
 * their journal events. On rejection, caller output and flow state are unchanged.
 * WAIT commits only the scheduler's monotonic observation (no diagnostics).
 * Event types record the alarm transition, not every observed sample.
 */
static inline vg_flow_result_t vg_flow_sample(
    vg_core_flow_t *flow, const vg_measurement_t *measurement,
    uint64_t now_ms, uint64_t *out_skipped, vg_diag_result_t *out_diagnostic)
{
    if (flow == NULL || !flow->initialized || measurement == NULL ||
        out_skipped == NULL || out_diagnostic == NULL ||
        measurement->source_mode != flow->source_mode ||
        flow->source_id == 0 || flow->demo_priority_code == 0 ||
        flow->demo_reason_code == 0 ||
        !flow->journal.initialized ||
        (flow->has_alarm &&
         (!vg_alarm_is_consistent(&flow->last_alarm) ||
          flow->last_alarm.source_id != flow->source_id ||
          flow->last_alarm.source_mode != flow->source_mode))) {
        return VG_FLOW_REJECTED;
    }
    if (flow->journal.has_last_time && now_ms < flow->journal.last_event_ms)
        return VG_FLOW_TIME_REGRESSION;

    vg_core_flow_t next = *flow;
    uint64_t skipped = 0;
    vg_schedule_result_t schedule = vg_scheduler_poll(&next.scheduler, now_ms, &skipped);
    if (schedule == VG_SCHED_INVALID) return VG_FLOW_REJECTED;
    if (schedule == VG_SCHED_TIME_REGRESSION) return VG_FLOW_TIME_REGRESSION;
    if (schedule == VG_SCHED_EXHAUSTED) return VG_FLOW_EXHAUSTED;
    if (schedule == VG_SCHED_WAIT) {
        *flow = next;
        *out_skipped = 0;
        *out_diagnostic = VG_DIAG_REJECTED; /* no sample was processed */
        return VG_FLOW_WAIT;
    }

    vg_diag_result_t diagnostic = vg_diagnostic_observe(
        &next.diagnostic, measurement, now_ms);
    if (diagnostic == VG_DIAG_REJECTED) return VG_FLOW_REJECTED;

    vg_event_type_t event_type = VG_EVENT_UNKNOWN;
    if (diagnostic == VG_DIAG_FAULT_STARTED) {
        if (next.has_alarm && next.last_alarm.condition_active)
            return VG_FLOW_REJECTED;
        /* A cleared prior alarm is replaced; the event journal records its
         * transition, but no long-term alarm-history store is provided. */
        next.last_alarm = (vg_alarm_t){0};
        if (!vg_alarm_try_raise(&next.alarm_ids, &next.last_alarm,
                next.source_id, next.source_mode,
                next.demo_priority_code, next.demo_reason_code, now_ms))
            return VG_FLOW_REJECTED;
        next.has_alarm = true;
        event_type = VG_EVENT_ALARM_RAISED;
    } else if (diagnostic == VG_DIAG_RECOVERED) {
        if (!next.has_alarm || !next.last_alarm.condition_active ||
            !vg_alarm_try_clear_condition(&next.last_alarm, now_ms))
            return VG_FLOW_REJECTED;
        event_type = VG_EVENT_ALARM_CLEARED;
    } else if (diagnostic == VG_DIAG_FAULT_CONTINUING) {
        if (!next.has_alarm || !next.last_alarm.condition_active)
            return VG_FLOW_REJECTED;
    } else if (next.has_alarm && next.last_alarm.condition_active) {
        return VG_FLOW_REJECTED;
    }

    if (event_type != VG_EVENT_UNKNOWN) {
        uint64_t event_id = 0;
        if (!vg_journal_append(&next.journal, next.last_alarm.id,
                next.source_id, next.source_mode, event_type,
                now_ms, &event_id)) {
            if (flow->journal.count == VG_JOURNAL_CAPACITY)
                return VG_FLOW_JOURNAL_FULL;
            return VG_FLOW_REJECTED;
        }
    }
    *flow = next;
    *out_skipped = skipped;
    *out_diagnostic = diagnostic;
    return VG_FLOW_PROCESSED;
}

/* Explicit operator-ack simulation, separate from fault recovery and clearing.
 * Refuse acknowledgement if the corresponding journal event cannot be recorded.
 */
static inline bool vg_flow_acknowledge(vg_core_flow_t *flow, uint64_t now_ms)
{
    if (flow == NULL || !flow->initialized || !flow->has_alarm ||
        !vg_alarm_is_consistent(&flow->last_alarm) ||
        (flow->diagnostic.has_observation &&
         now_ms < flow->diagnostic.last_observed_ms) ||
        (flow->journal.has_last_time && now_ms < flow->journal.last_event_ms))
        return false;
    vg_core_flow_t next = *flow;
    if (!vg_alarm_try_acknowledge(&next.last_alarm, now_ms)) return false;
    uint64_t event_id = 0;
    if (!vg_journal_append(&next.journal, next.last_alarm.id,
            next.source_id, next.source_mode, VG_EVENT_ALARM_ACK,
            now_ms, &event_id)) return false;
    *flow = next;
    return true;
}

#endif /* VG_CORE_FLOW_H */
