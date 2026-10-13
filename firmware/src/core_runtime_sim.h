#ifndef VG_CORE_RUNTIME_SIM_H
#define VG_CORE_RUNTIME_SIM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "core_flow.h"

/* A finite, six-sample SIMULATION-only source. No hardware acquisition,
 * communications, RTC, persistence, or safety-critical output. Caller supplies
 * monotonic timestamps; an ESP-IDF-only driver may poll with a real clock.
 * Advancing the scripted cursor occurs ONLY after a successful flow commit.
 */
#define VG_RUNTIME_SIM_STEPS 6u

typedef enum {
    VG_RUNTIME_SIM_REJECTED = 0,
    VG_RUNTIME_SIM_WAIT,
    VG_RUNTIME_SIM_PROCESSED,
    VG_RUNTIME_SIM_COMPLETE,
    VG_RUNTIME_SIM_TIME_REGRESSION,
    VG_RUNTIME_SIM_EXHAUSTED,
    VG_RUNTIME_SIM_JOURNAL_FULL
} vg_runtime_sim_result_t;

typedef struct {
    bool initialized;
    size_t next_step;
    vg_core_flow_t flow;
} vg_runtime_sim_t;

static inline bool vg_runtime_sim_measurement(size_t step, vg_measurement_t *out)
{
    if (out == NULL || step >= VG_RUNTIME_SIM_STEPS) return false;
    /* Two independent fault/recovery transitions, with a repeated fault.
     * Fault quality is never silently coerced to a numeric zero.
     */
    static const vg_data_quality_t quality[VG_RUNTIME_SIM_STEPS] = {
        VG_QUALITY_VALID, VG_QUALITY_MISSING, VG_QUALITY_INVALID,
        VG_QUALITY_VALID, VG_QUALITY_STALE, VG_QUALITY_VALID
    };
    vg_measurement_t sample = {0};
    sample.source_mode = VG_SOURCE_SIMULATION;
    sample.quality = quality[step];
    sample.has_value = (quality[step] != VG_QUALITY_MISSING);
    sample.value = 42.0f; /* arbitrary synthetic test data, not a threshold */
    *out = sample;
    return true;
}

static inline bool vg_runtime_sim_init(vg_runtime_sim_t *runtime,
                                      uint32_t source_id,
                                      uint64_t interval_ms,
                                      uint64_t first_due_ms)
{
    if (runtime == NULL || source_id == 0 || interval_ms == 0) return false;
    vg_runtime_sim_t fresh = {0};
    /* 1 and 1 are opaque DEMO alarm codes, not severity or policy. */
    if (!vg_flow_init(&fresh.flow, source_id, VG_SOURCE_SIMULATION,
                      1, 1, interval_ms, first_due_ms)) return false;
    fresh.initialized = true;
    *runtime = fresh;
    return true;
}

static inline vg_runtime_sim_result_t vg_runtime_sim_poll(
    vg_runtime_sim_t *runtime, uint64_t now_ms,
    uint64_t *out_skipped, vg_diag_result_t *out_diagnostic)
{
    if (runtime == NULL || out_skipped == NULL || out_diagnostic == NULL ||
        !runtime->initialized || !runtime->flow.initialized ||
        runtime->flow.source_mode != VG_SOURCE_SIMULATION ||
        runtime->next_step > VG_RUNTIME_SIM_STEPS) return VG_RUNTIME_SIM_REJECTED;
    if (runtime->next_step == VG_RUNTIME_SIM_STEPS) return VG_RUNTIME_SIM_COMPLETE;
    vg_measurement_t sample = {0};
    if (!vg_runtime_sim_measurement(runtime->next_step, &sample))
        return VG_RUNTIME_SIM_REJECTED;
    vg_flow_result_t result = vg_flow_sample(
        &runtime->flow, &sample, now_ms, out_skipped, out_diagnostic);
    switch (result) {
        case VG_FLOW_WAIT: return VG_RUNTIME_SIM_WAIT;
        case VG_FLOW_PROCESSED:
            runtime->next_step++;
            return VG_RUNTIME_SIM_PROCESSED;
        case VG_FLOW_TIME_REGRESSION: return VG_RUNTIME_SIM_TIME_REGRESSION;
        case VG_FLOW_EXHAUSTED: return VG_RUNTIME_SIM_EXHAUSTED;
        case VG_FLOW_JOURNAL_FULL: return VG_RUNTIME_SIM_JOURNAL_FULL;
        default: return VG_RUNTIME_SIM_REJECTED;
    }
}

#endif /* VG_CORE_RUNTIME_SIM_H */
