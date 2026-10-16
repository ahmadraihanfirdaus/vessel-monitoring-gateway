#ifndef VG_PROVIDER_BILGE_H
#define VG_PROVIDER_BILGE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "provider_contract.h"

/*
 * IF-03 / SAF-005 development provider.
 *
 * Bilge/high-water is represented as NORMAL/HIGH/FAULT/UNKNOWN plus explicit
 * quality metadata. The selected Adafruit 4965 reference is only a future
 * controlled-bench wet/dry surrogate. This module has no GPIO access, no
 * electrical design, no debounce/filter policy, no calibrated depth, and no
 * physical-vessel meaning.
 */

typedef enum {
    VG_BILGE_UNKNOWN = 0,
    VG_BILGE_NORMAL,
    VG_BILGE_HIGH,
    VG_BILGE_FAULT
} vg_bilge_state_t;

typedef struct {
    vg_provider_meta_t meta;
    vg_bilge_state_t state;
} vg_bilge_sample_t;

static inline bool vg_bilge_state_is_operational(vg_bilge_state_t state)
{
    return state == VG_BILGE_NORMAL || state == VG_BILGE_HIGH;
}

static inline bool vg_bilge_sample_is_consistent(const vg_bilge_sample_t *sample)
{
    if (sample == NULL || !vg_provider_meta_is_consistent(&sample->meta)) {
        return false;
    }

    if (sample->meta.quality == VG_QUALITY_VALID ||
        sample->meta.quality == VG_QUALITY_STALE) {
        return vg_bilge_state_is_operational(sample->state);
    }

    if (sample->meta.quality == VG_QUALITY_INVALID ||
        sample->meta.quality == VG_QUALITY_MISSING) {
        return sample->state == VG_BILGE_FAULT;
    }

    if (sample->meta.quality == VG_QUALITY_UNKNOWN) {
        return sample->state == VG_BILGE_UNKNOWN;
    }

    return false;
}

static inline bool vg_bilge_sample_is_current(const vg_bilge_sample_t *sample)
{
    return sample != NULL &&
           vg_bilge_sample_is_consistent(sample) &&
           sample->meta.quality == VG_QUALITY_VALID;
}

/*
 * Controlled-bench constructor from an already interpreted wet/dry/high-water
 * state. A future reviewed bench driver owns raw GPIO/electrical acquisition.
 */
static inline bool vg_bilge_bench_build_sample(
    vg_bilge_sample_t *out,
    vg_bilge_state_t interpreted_state,
    vg_data_quality_t quality,
    uint64_t sampled_at_ms,
    uint32_t sequence
)
{
    if (out == NULL) {
        return false;
    }

    vg_bilge_sample_t candidate = {0};

    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_BENCH_TEST,
            quality,
            sampled_at_ms,
            sequence)) {
        return false;
    }

    candidate.state = interpreted_state;

    if (!vg_bilge_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

#define VG_BILGE_SIM_STEPS 7u

typedef enum {
    VG_BILGE_SIM_REJECTED = 0,
    VG_BILGE_SIM_SAMPLE,
    VG_BILGE_SIM_COMPLETE
} vg_bilge_sim_result_t;

typedef struct {
    bool initialized;
    size_t next_step;
    uint64_t first_sample_ms;
    uint64_t interval_ms;
} vg_bilge_sim_t;

static inline bool vg_bilge_sim_init(
    vg_bilge_sim_t *sim,
    uint64_t first_sample_ms,
    uint64_t interval_ms
)
{
    if (sim == NULL || interval_ms == 0u) {
        return false;
    }

    vg_bilge_sim_t fresh = {
        .initialized = true,
        .next_step = 0u,
        .first_sample_ms = first_sample_ms,
        .interval_ms = interval_ms
    };

    *sim = fresh;
    return true;
}

static inline bool vg_bilge_sim_timestamp(
    const vg_bilge_sim_t *sim,
    size_t step,
    uint64_t *out_sampled_at_ms
)
{
    if (sim == NULL ||
        out_sampled_at_ms == NULL ||
        !sim->initialized ||
        step >= VG_BILGE_SIM_STEPS) {
        return false;
    }

    if (step != 0u && sim->interval_ms > UINT64_MAX / (uint64_t)step) {
        return false;
    }

    const uint64_t offset = sim->interval_ms * (uint64_t)step;
    if (sim->first_sample_ms > UINT64_MAX - offset) {
        return false;
    }

    *out_sampled_at_ms = sim->first_sample_ms + offset;
    return true;
}

static inline bool vg_bilge_sim_sample_for_step(
    const vg_bilge_sim_t *sim,
    size_t step,
    vg_bilge_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized ||
        step >= VG_BILGE_SIM_STEPS) {
        return false;
    }

    static const vg_data_quality_t quality[VG_BILGE_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_STALE,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_VALID
    };

    static const vg_bilge_state_t state[VG_BILGE_SIM_STEPS] = {
        VG_BILGE_NORMAL,
        VG_BILGE_HIGH,
        VG_BILGE_HIGH,
        VG_BILGE_FAULT,
        VG_BILGE_FAULT,
        VG_BILGE_UNKNOWN,
        VG_BILGE_NORMAL
    };

    uint64_t sampled_at_ms = 0u;
    if (!vg_bilge_sim_timestamp(sim, step, &sampled_at_ms)) {
        return false;
    }

    vg_bilge_sample_t candidate = {0};
    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_SIMULATION,
            quality[step],
            sampled_at_ms,
            (uint32_t)(step + 1u))) {
        return false;
    }

    candidate.state = state[step];
    if (!vg_bilge_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

static inline vg_bilge_sim_result_t vg_bilge_sim_next(
    vg_bilge_sim_t *sim,
    vg_bilge_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized) {
        return VG_BILGE_SIM_REJECTED;
    }

    if (sim->next_step >= VG_BILGE_SIM_STEPS) {
        return VG_BILGE_SIM_COMPLETE;
    }

    if (!vg_bilge_sim_sample_for_step(sim, sim->next_step, out)) {
        return VG_BILGE_SIM_REJECTED;
    }

    sim->next_step++;
    return VG_BILGE_SIM_SAMPLE;
}

#endif /* VG_PROVIDER_BILGE_H */
