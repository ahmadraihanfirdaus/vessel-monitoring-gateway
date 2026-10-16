#ifndef VG_PROVIDER_ATTITUDE_H
#define VG_PROVIDER_ATTITUDE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>

#include "provider_contract.h"

/*
 * IF-05 / MOT-001 development provider.
 *
 * Roll/pitch are prototype attitude/motion values with explicit quality.
 * MPU-6050 is only a simulation/controlled-bench reference. This module has
 * no I2C driver, bus address policy, axis-frame definition, filtering,
 * calibration, sensor-fusion, mounting alignment, or physical-vessel meaning.
 * It is explicitly not a vessel stability assessment or certification.
 */

typedef struct {
    vg_provider_meta_t meta;
    bool has_value;
    float roll_deg;
    float pitch_deg;
} vg_attitude_sample_t;

static inline const char *vg_attitude_channel_label(void)
{
    return "attitude/motion prototype";
}

static inline const char *vg_attitude_scope_note(void)
{
    return "not vessel stability certification";
}

static inline bool vg_attitude_sample_is_consistent(
    const vg_attitude_sample_t *sample
)
{
    if (sample == NULL || !vg_provider_meta_is_consistent(&sample->meta)) {
        return false;
    }

    if (sample->meta.quality == VG_QUALITY_VALID ||
        sample->meta.quality == VG_QUALITY_STALE) {
        return sample->has_value &&
               isfinite(sample->roll_deg) &&
               isfinite(sample->pitch_deg);
    }

    if (sample->meta.quality == VG_QUALITY_INVALID ||
        sample->meta.quality == VG_QUALITY_MISSING ||
        sample->meta.quality == VG_QUALITY_UNKNOWN) {
        return !sample->has_value;
    }

    return false;
}

static inline bool vg_attitude_sample_is_current(
    const vg_attitude_sample_t *sample
)
{
    return sample != NULL &&
           vg_attitude_sample_is_consistent(sample) &&
           sample->meta.quality == VG_QUALITY_VALID;
}

/*
 * Controlled-bench constructor from already decoded roll/pitch values.
 * A future reviewed MPU-6050 bench driver owns I2C acquisition, axis mapping,
 * calibration, timing, filtering, and raw conversion.
 */
static inline bool vg_attitude_bench_build_sample(
    vg_attitude_sample_t *out,
    vg_data_quality_t quality,
    bool has_value,
    float roll_deg,
    float pitch_deg,
    uint64_t sampled_at_ms,
    uint32_t sequence
)
{
    if (out == NULL) {
        return false;
    }

    vg_attitude_sample_t candidate = {0};
    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_BENCH_TEST,
            quality,
            sampled_at_ms,
            sequence)) {
        return false;
    }

    candidate.has_value = has_value;
    candidate.roll_deg = roll_deg;
    candidate.pitch_deg = pitch_deg;

    if (!vg_attitude_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

#define VG_ATTITUDE_SIM_STEPS 8u

typedef enum {
    VG_ATTITUDE_SIM_REJECTED = 0,
    VG_ATTITUDE_SIM_SAMPLE,
    VG_ATTITUDE_SIM_COMPLETE
} vg_attitude_sim_result_t;

typedef struct {
    bool initialized;
    size_t next_step;
    uint64_t first_sample_ms;
    uint64_t interval_ms;
} vg_attitude_sim_t;

static inline bool vg_attitude_sim_init(
    vg_attitude_sim_t *sim,
    uint64_t first_sample_ms,
    uint64_t interval_ms
)
{
    if (sim == NULL || interval_ms == 0u) {
        return false;
    }

    vg_attitude_sim_t fresh = {
        .initialized = true,
        .next_step = 0u,
        .first_sample_ms = first_sample_ms,
        .interval_ms = interval_ms
    };
    *sim = fresh;
    return true;
}

static inline bool vg_attitude_sim_timestamp(
    const vg_attitude_sim_t *sim,
    size_t step,
    uint64_t *out_sampled_at_ms
)
{
    if (sim == NULL || out_sampled_at_ms == NULL || !sim->initialized ||
        step >= VG_ATTITUDE_SIM_STEPS) {
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

static inline bool vg_attitude_sim_sample_for_step(
    const vg_attitude_sim_t *sim,
    size_t step,
    vg_attitude_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized ||
        step >= VG_ATTITUDE_SIM_STEPS) {
        return false;
    }

    static const vg_data_quality_t quality[VG_ATTITUDE_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_STALE,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_VALID
    };

    static const bool has_value[VG_ATTITUDE_SIM_STEPS] = {
        true, true, true, true, false, false, false, true
    };

    static const float roll_deg[VG_ATTITUDE_SIM_STEPS] = {
        0.0f, 12.5f, -8.0f, -8.0f, 0.0f, 0.0f, 0.0f, 1.0f
    };

    static const float pitch_deg[VG_ATTITUDE_SIM_STEPS] = {
        0.0f, -4.0f, 6.0f, 6.0f, 0.0f, 0.0f, 0.0f, -1.0f
    };

    uint64_t sampled_at_ms = 0u;
    if (!vg_attitude_sim_timestamp(sim, step, &sampled_at_ms)) {
        return false;
    }

    vg_attitude_sample_t candidate = {0};
    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_SIMULATION,
            quality[step],
            sampled_at_ms,
            (uint32_t)(step + 1u))) {
        return false;
    }

    candidate.has_value = has_value[step];
    candidate.roll_deg = roll_deg[step];
    candidate.pitch_deg = pitch_deg[step];

    if (!vg_attitude_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

static inline vg_attitude_sim_result_t vg_attitude_sim_next(
    vg_attitude_sim_t *sim,
    vg_attitude_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized) {
        return VG_ATTITUDE_SIM_REJECTED;
    }

    if (sim->next_step >= VG_ATTITUDE_SIM_STEPS) {
        return VG_ATTITUDE_SIM_COMPLETE;
    }

    if (!vg_attitude_sim_sample_for_step(sim, sim->next_step, out)) {
        return VG_ATTITUDE_SIM_REJECTED;
    }

    sim->next_step++;
    return VG_ATTITUDE_SIM_SAMPLE;
}

#endif /* VG_PROVIDER_ATTITUDE_H */
