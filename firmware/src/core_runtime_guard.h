#ifndef VG_CORE_RUNTIME_GUARD_H
#define VG_CORE_RUNTIME_GUARD_H

#include <stdbool.h>
#include <stdint.h>
#include "core_runtime_sim.h"

/* Simulation-only fail-stop observation layer for the finite C3 runtime.
 * This guard never drops a journal entry, retries a failed event, clears
 * an alarm, or claims fail-safe vessel control. Caller must explicitly
 * reinitialize an appropriate fresh, reviewed session after a stop.
 */
typedef enum {
    VG_GUARD_UNINITIALIZED = 0,
    VG_GUARD_RUNNING,
    VG_GUARD_COMPLETE,
    VG_GUARD_BLOCKED_JOURNAL,
    VG_GUARD_STOPPED_ERROR
} vg_guard_state_t;

typedef enum {
    VG_GUARD_INVALID = 0,
    VG_GUARD_WAIT,
    VG_GUARD_PROCESSED,
    VG_GUARD_FINISHED,
    VG_GUARD_STOPPED_JOURNAL,
    VG_GUARD_STOPPED_FAULT,
    VG_GUARD_ALREADY_STOPPED
} vg_guard_result_t;

typedef struct {
    bool initialized;
    vg_guard_state_t state;
    vg_runtime_sim_result_t last_runtime_result;
    uint64_t processed_count;
    uint64_t wait_count;
    uint64_t journal_full_count;
    uint64_t error_count;
} vg_runtime_guard_t;

static inline void vg_guard_increment(uint64_t *counter)
{
    if (counter != NULL && *counter != UINT64_MAX) ++*counter;
}

static inline bool vg_guard_init(vg_runtime_guard_t *guard,
                                  const vg_runtime_sim_t *runtime)
{
    if (guard == NULL || runtime == NULL || !runtime->initialized ||
        !runtime->flow.initialized ||
        runtime->flow.source_mode != VG_SOURCE_SIMULATION ||
        runtime->next_step > VG_RUNTIME_SIM_STEPS) return false;
    *guard = (vg_runtime_guard_t){
        .initialized = true, .state = VG_GUARD_RUNNING,
        .last_runtime_result = VG_RUNTIME_SIM_REJECTED
    };
    return true;
}

static inline vg_guard_result_t vg_guard_poll(
    vg_runtime_guard_t *guard, vg_runtime_sim_t *runtime,
    uint64_t now_ms, uint64_t *out_skipped, vg_diag_result_t *out_diag)
{
    if (guard == NULL || runtime == NULL || out_skipped == NULL ||
        out_diag == NULL || !guard->initialized ||
        guard->state < VG_GUARD_RUNNING ||
        guard->state > VG_GUARD_STOPPED_ERROR)
        return VG_GUARD_INVALID;
    if (guard->state != VG_GUARD_RUNNING) return VG_GUARD_ALREADY_STOPPED;

    const vg_runtime_sim_result_t result = vg_runtime_sim_poll(
        runtime, now_ms, out_skipped, out_diag);
    guard->last_runtime_result = result;
    switch (result) {
        case VG_RUNTIME_SIM_WAIT:
            vg_guard_increment(&guard->wait_count);
            return VG_GUARD_WAIT;
        case VG_RUNTIME_SIM_PROCESSED:
            vg_guard_increment(&guard->processed_count);
            return VG_GUARD_PROCESSED;
        case VG_RUNTIME_SIM_COMPLETE:
            guard->state = VG_GUARD_COMPLETE;
            return VG_GUARD_FINISHED;
        case VG_RUNTIME_SIM_JOURNAL_FULL:
            vg_guard_increment(&guard->journal_full_count);
            guard->state = VG_GUARD_BLOCKED_JOURNAL;
            return VG_GUARD_STOPPED_JOURNAL;
        default:
            vg_guard_increment(&guard->error_count);
            guard->state = VG_GUARD_STOPPED_ERROR;
            return VG_GUARD_STOPPED_FAULT;
    }
}

#endif /* VG_CORE_RUNTIME_GUARD_H */
