#ifndef VG_PROVIDER_FUEL_VAPOR_H
#define VG_PROVIDER_FUEL_VAPOR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>

#include "provider_contract.h"

/*
 * IF-02 / SAF-004 development provider.
 *
 * Fuel-vapor is represented by an interpreted gas state plus an optional
 * finite surrogate value and explicit quality metadata. The surrogate value
 * is intentionally unitless: it is not ppm, %LEL, concentration, or a
 * calibrated marine fuel-vapor measurement.
 *
 * MQ-2 is only a future controlled-bench surrogate reference. This module has
 * no ADC/GPIO access, no heater/loop wiring, no voltage-divider design, no
 * calibration curve, no gas-specific conversion, and no start-blocking policy.
 */

typedef enum {
    VG_FUEL_VAPOR_UNKNOWN = 0,
    VG_FUEL_VAPOR_NORMAL,
    VG_FUEL_VAPOR_WARNING,
    VG_FUEL_VAPOR_ALARM,
    VG_FUEL_VAPOR_FAULT
} vg_fuel_vapor_state_t;

typedef struct {
    vg_provider_meta_t meta;
    vg_fuel_vapor_state_t state;
    bool has_value;
    float surrogate_value;
} vg_fuel_vapor_sample_t;

static inline bool vg_fuel_vapor_state_is_operational(
    vg_fuel_vapor_state_t state
)
{
    return state == VG_FUEL_VAPOR_NORMAL ||
           state == VG_FUEL_VAPOR_WARNING ||
           state == VG_FUEL_VAPOR_ALARM;
}

static inline bool vg_fuel_vapor_sample_is_consistent(
    const vg_fuel_vapor_sample_t *sample
)
{
    if (sample == NULL ||
        !vg_provider_meta_is_consistent(&sample->meta)) {
        return false;
    }

    if (sample->meta.quality == VG_QUALITY_VALID ||
        sample->meta.quality == VG_QUALITY_STALE) {
        return vg_fuel_vapor_state_is_operational(sample->state) &&
               sample->has_value &&
               isfinite(sample->surrogate_value);
    }

    if (sample->meta.quality == VG_QUALITY_INVALID ||
        sample->meta.quality == VG_QUALITY_MISSING) {
        /* Missing/invalid is explicit FAULT, never a safe NORMAL state. */
        return sample->state == VG_FUEL_VAPOR_FAULT &&
               !sample->has_value;
    }

    if (sample->meta.quality == VG_QUALITY_UNKNOWN) {
        return sample->state == VG_FUEL_VAPOR_UNKNOWN &&
               !sample->has_value;
    }

    return false;
}

static inline bool vg_fuel_vapor_sample_is_current(
    const vg_fuel_vapor_sample_t *sample
)
{
    return sample != NULL &&
           vg_fuel_vapor_sample_is_consistent(sample) &&
           sample->meta.quality == VG_QUALITY_VALID;
}

/*
 * Build a controlled-bench provenance sample from an already interpreted
 * state/value pair. A future reviewed bench driver is responsible for any raw
 * electrical acquisition and interpretation. No threshold is defined here.
 */
static inline bool vg_fuel_vapor_bench_build_sample(
    vg_fuel_vapor_sample_t *out,
    vg_fuel_vapor_state_t interpreted_state,
    vg_data_quality_t quality,
    bool has_value,
    float surrogate_value,
    uint64_t sampled_at_ms,
    uint32_t sequence
)
{
    if (out == NULL) {
        return false;
    }

    vg_fuel_vapor_sample_t candidate = {0};

    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_BENCH_TEST,
            quality,
            sampled_at_ms,
            sequence)) {
        return false;
    }

    candidate.state = interpreted_state;
    candidate.has_value = has_value;
    candidate.surrogate_value = surrogate_value;

    if (!vg_fuel_vapor_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

/* Deterministic software-only IF-02 simulation. */
#define VG_FUEL_VAPOR_SIM_STEPS 8u

typedef enum {
    VG_FUEL_VAPOR_SIM_REJECTED = 0,
    VG_FUEL_VAPOR_SIM_SAMPLE,
    VG_FUEL_VAPOR_SIM_COMPLETE
} vg_fuel_vapor_sim_result_t;

typedef struct {
    bool initialized;
    size_t next_step;
    uint64_t first_sample_ms;
    uint64_t interval_ms;
} vg_fuel_vapor_sim_t;

static inline bool vg_fuel_vapor_sim_init(
    vg_fuel_vapor_sim_t *sim,
    uint64_t first_sample_ms,
    uint64_t interval_ms
)
{
    if (sim == NULL || interval_ms == 0u) {
        return false;
    }

    vg_fuel_vapor_sim_t fresh = {
        .initialized = true,
        .next_step = 0u,
        .first_sample_ms = first_sample_ms,
        .interval_ms = interval_ms
    };

    *sim = fresh;
    return true;
}

static inline bool vg_fuel_vapor_sim_timestamp(
    const vg_fuel_vapor_sim_t *sim,
    size_t step,
    uint64_t *out_sampled_at_ms
)
{
    if (sim == NULL ||
        out_sampled_at_ms == NULL ||
        !sim->initialized ||
        step >= VG_FUEL_VAPOR_SIM_STEPS) {
        return false;
    }

    if (step != 0u &&
        sim->interval_ms > UINT64_MAX / (uint64_t)step) {
        return false;
    }

    const uint64_t offset = sim->interval_ms * (uint64_t)step;

    if (sim->first_sample_ms > UINT64_MAX - offset) {
        return false;
    }

    *out_sampled_at_ms = sim->first_sample_ms + offset;
    return true;
}

static inline bool vg_fuel_vapor_sim_sample_for_step(
    const vg_fuel_vapor_sim_t *sim,
    size_t step,
    vg_fuel_vapor_sample_t *out
)
{
    if (sim == NULL ||
        out == NULL ||
        !sim->initialized ||
        step >= VG_FUEL_VAPOR_SIM_STEPS) {
        return false;
    }

    static const vg_data_quality_t quality[VG_FUEL_VAPOR_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_STALE,
        VG_QUALITY_VALID
    };

    static const vg_fuel_vapor_state_t state[VG_FUEL_VAPOR_SIM_STEPS] = {
        VG_FUEL_VAPOR_NORMAL,
        VG_FUEL_VAPOR_WARNING,
        VG_FUEL_VAPOR_ALARM,
        VG_FUEL_VAPOR_FAULT,
        VG_FUEL_VAPOR_FAULT,
        VG_FUEL_VAPOR_UNKNOWN,
        VG_FUEL_VAPOR_WARNING,
        VG_FUEL_VAPOR_NORMAL
    };

    static const bool has_value[VG_FUEL_VAPOR_SIM_STEPS] = {
        true, true, true, false, false, false, true, true
    };

    static const float surrogate_value[VG_FUEL_VAPOR_SIM_STEPS] = {
        0.10f, 0.55f, 0.90f, 0.0f, 0.0f, 0.0f, 0.60f, 0.20f
    };

    uint64_t sampled_at_ms = 0u;

    if (!vg_fuel_vapor_sim_timestamp(sim, step, &sampled_at_ms)) {
        return false;
    }

    vg_fuel_vapor_sample_t candidate = {0};

    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_SIMULATION,
            quality[step],
            sampled_at_ms,
            (uint32_t)(step + 1u))) {
        return false;
    }

    candidate.state = state[step];
    candidate.has_value = has_value[step];
    candidate.surrogate_value = surrogate_value[step];

    if (!vg_fuel_vapor_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

static inline vg_fuel_vapor_sim_result_t vg_fuel_vapor_sim_next(
    vg_fuel_vapor_sim_t *sim,
    vg_fuel_vapor_sample_t *out
)
{
    if (sim == NULL ||
        out == NULL ||
        !sim->initialized ||
        sim->next_step > VG_FUEL_VAPOR_SIM_STEPS) {
        return VG_FUEL_VAPOR_SIM_REJECTED;
    }

    if (sim->next_step == VG_FUEL_VAPOR_SIM_STEPS) {
        return VG_FUEL_VAPOR_SIM_COMPLETE;
    }

    vg_fuel_vapor_sample_t candidate = {0};

    if (!vg_fuel_vapor_sim_sample_for_step(
            sim,
            sim->next_step,
            &candidate)) {
        return VG_FUEL_VAPOR_SIM_REJECTED;
    }

    *out = candidate;
    sim->next_step++;
    return VG_FUEL_VAPOR_SIM_SAMPLE;
}

#endif /* VG_PROVIDER_FUEL_VAPOR_H */
