#ifndef VG_PROVIDER_DOOR_H
#define VG_PROVIDER_DOOR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "provider_contract.h"

/*
 * IF-01 / SAF-001 development provider.
 *
 * Door/hatch state is modeled as OPEN, CLOSED, or UNKNOWN with explicit
 * quality metadata. This module contains no GPIO access, no electrical
 * polarity assumption, no debounce timing, and no safety-policy decision.
 *
 * The bench constructor accepts an already interpreted logical state from a
 * future reviewed bench driver. It does not claim that Adafruit 375 hardware
 * has been wired, purchased, calibrated, or tested.
 */

typedef enum {
    VG_DOOR_STATE_UNKNOWN = 0,
    VG_DOOR_STATE_OPEN,
    VG_DOOR_STATE_CLOSED
} vg_door_state_t;

typedef struct {
    vg_provider_meta_t meta;
    vg_door_state_t state;
} vg_door_sample_t;

static inline bool vg_door_state_is_known(
    vg_door_state_t state
)
{
    return state == VG_DOOR_STATE_OPEN ||
           state == VG_DOOR_STATE_CLOSED;
}

static inline bool vg_door_sample_is_consistent(
    const vg_door_sample_t *sample
)
{
    if (sample == NULL ||
        !vg_provider_meta_is_consistent(&sample->meta)) {
        return false;
    }

    /*
     * VALID and STALE may retain an interpreted OPEN/CLOSED payload.
     * INVALID, MISSING, and UNKNOWN must not be represented as a safe or
     * current OPEN/CLOSED state; their semantic state is forced UNKNOWN.
     */
    if (sample->meta.quality == VG_QUALITY_VALID ||
        sample->meta.quality == VG_QUALITY_STALE) {
        return vg_door_state_is_known(sample->state);
    }

    return sample->state == VG_DOOR_STATE_UNKNOWN;
}

static inline bool vg_door_sample_is_current(
    const vg_door_sample_t *sample
)
{
    return sample != NULL &&
           vg_door_sample_is_consistent(sample) &&
           sample->meta.quality == VG_QUALITY_VALID &&
           vg_door_state_is_known(sample->state);
}

/*
 * Build a controlled-bench provenance sample from an already interpreted
 * logical state. Electrical input polarity and debounce remain responsibilities
 * of a future reviewed bench driver and are not implemented here.
 */
static inline bool vg_door_bench_build_sample(
    vg_door_sample_t *out,
    vg_door_state_t interpreted_state,
    vg_data_quality_t quality,
    uint64_t sampled_at_ms,
    uint32_t sequence
)
{
    if (out == NULL) {
        return false;
    }

    vg_door_sample_t candidate = {0};

    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_BENCH_TEST,
            quality,
            sampled_at_ms,
            sequence)) {
        return false;
    }

    candidate.state = interpreted_state;

    if (!vg_door_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

/*
 * Deterministic software-only IF-01 simulation.
 * No Phase 5 start-permission or blocking decision is performed.
 */
#define VG_DOOR_SIM_STEPS 6u

typedef enum {
    VG_DOOR_SIM_REJECTED = 0,
    VG_DOOR_SIM_SAMPLE,
    VG_DOOR_SIM_COMPLETE
} vg_door_sim_result_t;

typedef struct {
    bool initialized;
    size_t next_step;
    uint64_t first_sample_ms;
    uint64_t interval_ms;
} vg_door_sim_t;

static inline bool vg_door_sim_init(
    vg_door_sim_t *sim,
    uint64_t first_sample_ms,
    uint64_t interval_ms
)
{
    if (sim == NULL || interval_ms == 0u) {
        return false;
    }

    vg_door_sim_t fresh = {
        .initialized = true,
        .next_step = 0u,
        .first_sample_ms = first_sample_ms,
        .interval_ms = interval_ms
    };

    *sim = fresh;
    return true;
}

static inline bool vg_door_sim_timestamp(
    const vg_door_sim_t *sim,
    size_t step,
    uint64_t *out_sampled_at_ms
)
{
    if (sim == NULL ||
        out_sampled_at_ms == NULL ||
        !sim->initialized ||
        step >= VG_DOOR_SIM_STEPS) {
        return false;
    }

    if (step != 0u &&
        sim->interval_ms > UINT64_MAX / (uint64_t)step) {
        return false;
    }

    const uint64_t offset =
        sim->interval_ms * (uint64_t)step;

    if (sim->first_sample_ms > UINT64_MAX - offset) {
        return false;
    }

    *out_sampled_at_ms = sim->first_sample_ms + offset;
    return true;
}

static inline bool vg_door_sim_sample_for_step(
    const vg_door_sim_t *sim,
    size_t step,
    vg_door_sample_t *out
)
{
    if (sim == NULL ||
        out == NULL ||
        !sim->initialized ||
        step >= VG_DOOR_SIM_STEPS) {
        return false;
    }

    static const vg_data_quality_t quality[VG_DOOR_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_STALE,
        VG_QUALITY_VALID
    };

    static const vg_door_state_t state[VG_DOOR_SIM_STEPS] = {
        VG_DOOR_STATE_OPEN,
        VG_DOOR_STATE_CLOSED,
        VG_DOOR_STATE_UNKNOWN,
        VG_DOOR_STATE_UNKNOWN,
        VG_DOOR_STATE_CLOSED,
        VG_DOOR_STATE_OPEN
    };

    uint64_t sampled_at_ms = 0u;

    if (!vg_door_sim_timestamp(sim, step, &sampled_at_ms)) {
        return false;
    }

    vg_door_sample_t candidate = {0};

    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_SIMULATION,
            quality[step],
            sampled_at_ms,
            (uint32_t)(step + 1u))) {
        return false;
    }

    candidate.state = state[step];

    if (!vg_door_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

static inline vg_door_sim_result_t vg_door_sim_next(
    vg_door_sim_t *sim,
    vg_door_sample_t *out
)
{
    if (sim == NULL ||
        out == NULL ||
        !sim->initialized ||
        sim->next_step > VG_DOOR_SIM_STEPS) {
        return VG_DOOR_SIM_REJECTED;
    }

    if (sim->next_step == VG_DOOR_SIM_STEPS) {
        return VG_DOOR_SIM_COMPLETE;
    }

    vg_door_sample_t candidate = {0};

    if (!vg_door_sim_sample_for_step(
            sim,
            sim->next_step,
            &candidate)) {
        return VG_DOOR_SIM_REJECTED;
    }

    *out = candidate;
    sim->next_step++;

    return VG_DOOR_SIM_SAMPLE;
}

#endif /* VG_PROVIDER_DOOR_H */
