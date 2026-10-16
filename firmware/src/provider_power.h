#ifndef VG_PROVIDER_POWER_H
#define VG_PROVIDER_POWER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>

#include "provider_contract.h"

/*
 * IF-07 development provider.
 *
 * Voltage/current/power are development values with explicit quality.
 * INA219 is only a controlled low-power simulation/bench reference. This
 * module has no I2C driver, address/GPIO policy, shunt selection, calibration,
 * high-voltage/high-current design, isolation, protection, vessel power-bus
 * integration, energy accounting, or electrical safety certification.
 */

typedef struct {
    vg_provider_meta_t meta;
    bool has_value;
    float voltage_v;
    float current_a;
    float power_w;
} vg_power_sample_t;

static inline const char *vg_power_channel_label(void)
{
    return "low-power electrical bench prototype";
}

static inline const char *vg_power_scope_note(void)
{
    return "safe low-power bench reference only";
}

static inline const char *vg_power_hazard_note(void)
{
    return "not vessel electrical safety certification";
}

static inline bool vg_power_sample_is_consistent(const vg_power_sample_t *sample)
{
    if (sample == NULL || !vg_provider_meta_is_consistent(&sample->meta)) {
        return false;
    }

    if (sample->meta.quality == VG_QUALITY_VALID ||
        sample->meta.quality == VG_QUALITY_STALE) {
        return sample->has_value &&
               isfinite(sample->voltage_v) && sample->voltage_v >= 0.0f &&
               isfinite(sample->current_a) &&
               isfinite(sample->power_w);
    }

    if (sample->meta.quality == VG_QUALITY_INVALID ||
        sample->meta.quality == VG_QUALITY_MISSING ||
        sample->meta.quality == VG_QUALITY_UNKNOWN) {
        return !sample->has_value;
    }

    return false;
}

static inline bool vg_power_sample_is_current(const vg_power_sample_t *sample)
{
    return sample != NULL &&
           vg_power_sample_is_consistent(sample) &&
           sample->meta.quality == VG_QUALITY_VALID;
}

/*
 * Controlled-bench constructor from already decoded engineering values.
 * A future reviewed INA219 bench driver owns I2C acquisition, shunt/config
 * setup, calibration, conversion timing, range checks, and electrical safety.
 */
static inline bool vg_power_bench_build_sample(
    vg_power_sample_t *out,
    vg_data_quality_t quality,
    bool has_value,
    float voltage_v,
    float current_a,
    float power_w,
    uint64_t sampled_at_ms,
    uint32_t sequence
)
{
    if (out == NULL) {
        return false;
    }

    vg_power_sample_t candidate = {0};
    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_BENCH_TEST,
            quality,
            sampled_at_ms,
            sequence)) {
        return false;
    }

    candidate.has_value = has_value;
    candidate.voltage_v = voltage_v;
    candidate.current_a = current_a;
    candidate.power_w = power_w;

    if (!vg_power_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

#define VG_POWER_SIM_STEPS 8u

typedef enum {
    VG_POWER_SIM_REJECTED = 0,
    VG_POWER_SIM_SAMPLE,
    VG_POWER_SIM_COMPLETE
} vg_power_sim_result_t;

typedef struct {
    bool initialized;
    size_t next_step;
    uint64_t first_sample_ms;
    uint64_t interval_ms;
} vg_power_sim_t;

static inline bool vg_power_sim_init(
    vg_power_sim_t *sim,
    uint64_t first_sample_ms,
    uint64_t interval_ms
)
{
    if (sim == NULL || interval_ms == 0u) {
        return false;
    }

    vg_power_sim_t fresh = {
        .initialized = true,
        .next_step = 0u,
        .first_sample_ms = first_sample_ms,
        .interval_ms = interval_ms
    };
    *sim = fresh;
    return true;
}

static inline bool vg_power_sim_timestamp(
    const vg_power_sim_t *sim,
    size_t step,
    uint64_t *out_sampled_at_ms
)
{
    if (sim == NULL || out_sampled_at_ms == NULL || !sim->initialized ||
        step >= VG_POWER_SIM_STEPS) {
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

static inline bool vg_power_sim_sample_for_step(
    const vg_power_sim_t *sim,
    size_t step,
    vg_power_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized ||
        step >= VG_POWER_SIM_STEPS) {
        return false;
    }

    static const vg_data_quality_t quality[VG_POWER_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_STALE,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_VALID
    };
    static const bool has_value[VG_POWER_SIM_STEPS] = {
        true, true, true, true, false, false, false, true
    };
    static const float voltage_v[VG_POWER_SIM_STEPS] = {
        5.0f, 12.0f, 12.0f, 12.0f, 0.0f, 0.0f, 0.0f, 5.0f
    };
    static const float current_a[VG_POWER_SIM_STEPS] = {
        0.10f, 0.25f, -0.05f, -0.05f, 0.0f, 0.0f, 0.0f, 0.05f
    };
    static const float power_w[VG_POWER_SIM_STEPS] = {
        0.50f, 3.00f, -0.60f, -0.60f, 0.0f, 0.0f, 0.0f, 0.25f
    };

    uint64_t sampled_at_ms = 0u;
    if (!vg_power_sim_timestamp(sim, step, &sampled_at_ms)) {
        return false;
    }

    vg_power_sample_t candidate = {0};
    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_SIMULATION,
            quality[step],
            sampled_at_ms,
            (uint32_t)(step + 1u))) {
        return false;
    }

    candidate.has_value = has_value[step];
    candidate.voltage_v = voltage_v[step];
    candidate.current_a = current_a[step];
    candidate.power_w = power_w[step];

    if (!vg_power_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

static inline vg_power_sim_result_t vg_power_sim_next(
    vg_power_sim_t *sim,
    vg_power_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized) {
        return VG_POWER_SIM_REJECTED;
    }

    if (sim->next_step >= VG_POWER_SIM_STEPS) {
        return VG_POWER_SIM_COMPLETE;
    }

    if (!vg_power_sim_sample_for_step(sim, sim->next_step, out)) {
        return VG_POWER_SIM_REJECTED;
    }

    sim->next_step++;
    return VG_POWER_SIM_SAMPLE;
}

#endif /* VG_PROVIDER_POWER_H */
