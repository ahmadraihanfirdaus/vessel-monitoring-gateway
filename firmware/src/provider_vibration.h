#ifndef VG_PROVIDER_VIBRATION_H
#define VG_PROVIDER_VIBRATION_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>

#include "provider_contract.h"

/*
 * IF-06 / MOT-002 development provider.
 *
 * Accelerometer axes and vibration_index are development values with explicit
 * quality. ADXL345 is only a simulation/controlled-bench reference. This
 * module has no I2C/SPI driver, bus/GPIO policy, sample-rate policy, axis-frame
 * definition, calibration, filtering, FFT/RMS analysis, mounting alignment,
 * machinery diagnosis, or physical-vessel meaning.
 */

typedef struct {
    vg_provider_meta_t meta;
    bool has_value;
    float accel_x_g;
    float accel_y_g;
    float accel_z_g;
    float vibration_index;
} vg_vibration_sample_t;

static inline const char *vg_vibration_channel_label(void)
{
    return "vibration/acceleration prototype";
}

static inline const char *vg_vibration_scope_note(void)
{
    return "not machinery condition certification";
}

static inline bool vg_vibration_sample_is_consistent(
    const vg_vibration_sample_t *sample
)
{
    if (sample == NULL || !vg_provider_meta_is_consistent(&sample->meta)) {
        return false;
    }

    if (sample->meta.quality == VG_QUALITY_VALID ||
        sample->meta.quality == VG_QUALITY_STALE) {
        return sample->has_value &&
               isfinite(sample->accel_x_g) &&
               isfinite(sample->accel_y_g) &&
               isfinite(sample->accel_z_g) &&
               isfinite(sample->vibration_index) &&
               sample->vibration_index >= 0.0f;
    }

    if (sample->meta.quality == VG_QUALITY_INVALID ||
        sample->meta.quality == VG_QUALITY_MISSING ||
        sample->meta.quality == VG_QUALITY_UNKNOWN) {
        return !sample->has_value;
    }

    return false;
}

static inline bool vg_vibration_sample_is_current(
    const vg_vibration_sample_t *sample
)
{
    return sample != NULL &&
           vg_vibration_sample_is_consistent(sample) &&
           sample->meta.quality == VG_QUALITY_VALID;
}

/*
 * Controlled-bench constructor from already decoded acceleration/index values.
 * A future reviewed ADXL345 bench driver owns bus acquisition, axis mapping,
 * calibration, sample timing, filtering, and any derived vibration metric.
 */
static inline bool vg_vibration_bench_build_sample(
    vg_vibration_sample_t *out,
    vg_data_quality_t quality,
    bool has_value,
    float accel_x_g,
    float accel_y_g,
    float accel_z_g,
    float vibration_index,
    uint64_t sampled_at_ms,
    uint32_t sequence
)
{
    if (out == NULL) {
        return false;
    }

    vg_vibration_sample_t candidate = {0};
    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_BENCH_TEST,
            quality,
            sampled_at_ms,
            sequence)) {
        return false;
    }

    candidate.has_value = has_value;
    candidate.accel_x_g = accel_x_g;
    candidate.accel_y_g = accel_y_g;
    candidate.accel_z_g = accel_z_g;
    candidate.vibration_index = vibration_index;

    if (!vg_vibration_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

#define VG_VIBRATION_SIM_STEPS 8u

typedef enum {
    VG_VIBRATION_SIM_REJECTED = 0,
    VG_VIBRATION_SIM_SAMPLE,
    VG_VIBRATION_SIM_COMPLETE
} vg_vibration_sim_result_t;

typedef struct {
    bool initialized;
    size_t next_step;
    uint64_t first_sample_ms;
    uint64_t interval_ms;
} vg_vibration_sim_t;

static inline bool vg_vibration_sim_init(
    vg_vibration_sim_t *sim,
    uint64_t first_sample_ms,
    uint64_t interval_ms
)
{
    if (sim == NULL || interval_ms == 0u) {
        return false;
    }

    vg_vibration_sim_t fresh = {
        .initialized = true,
        .next_step = 0u,
        .first_sample_ms = first_sample_ms,
        .interval_ms = interval_ms
    };
    *sim = fresh;
    return true;
}

static inline bool vg_vibration_sim_timestamp(
    const vg_vibration_sim_t *sim,
    size_t step,
    uint64_t *out_sampled_at_ms
)
{
    if (sim == NULL || out_sampled_at_ms == NULL || !sim->initialized ||
        step >= VG_VIBRATION_SIM_STEPS) {
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

static inline bool vg_vibration_sim_sample_for_step(
    const vg_vibration_sim_t *sim,
    size_t step,
    vg_vibration_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized ||
        step >= VG_VIBRATION_SIM_STEPS) {
        return false;
    }

    static const vg_data_quality_t quality[VG_VIBRATION_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_STALE,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_VALID
    };

    static const bool has_value[VG_VIBRATION_SIM_STEPS] = {
        true, true, true, true, false, false, false, true
    };

    static const float accel_x_g[VG_VIBRATION_SIM_STEPS] = {
        0.00f, 0.12f, -0.25f, -0.25f, 0.0f, 0.0f, 0.0f, 0.01f
    };
    static const float accel_y_g[VG_VIBRATION_SIM_STEPS] = {
        0.00f, -0.08f, 0.20f, 0.20f, 0.0f, 0.0f, 0.0f, 0.00f
    };
    static const float accel_z_g[VG_VIBRATION_SIM_STEPS] = {
        1.00f, 1.03f, 0.92f, 0.92f, 0.0f, 0.0f, 0.0f, 1.00f
    };
    static const float vibration_index[VG_VIBRATION_SIM_STEPS] = {
        0.02f, 0.35f, 0.80f, 0.80f, 0.0f, 0.0f, 0.0f, 0.05f
    };

    uint64_t sampled_at_ms = 0u;
    if (!vg_vibration_sim_timestamp(sim, step, &sampled_at_ms)) {
        return false;
    }

    vg_vibration_sample_t candidate = {0};
    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_SIMULATION,
            quality[step],
            sampled_at_ms,
            (uint32_t)(step + 1u))) {
        return false;
    }

    candidate.has_value = has_value[step];
    candidate.accel_x_g = accel_x_g[step];
    candidate.accel_y_g = accel_y_g[step];
    candidate.accel_z_g = accel_z_g[step];
    candidate.vibration_index = vibration_index[step];

    if (!vg_vibration_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

static inline vg_vibration_sim_result_t vg_vibration_sim_next(
    vg_vibration_sim_t *sim,
    vg_vibration_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized) {
        return VG_VIBRATION_SIM_REJECTED;
    }

    if (sim->next_step >= VG_VIBRATION_SIM_STEPS) {
        return VG_VIBRATION_SIM_COMPLETE;
    }

    if (!vg_vibration_sim_sample_for_step(sim, sim->next_step, out)) {
        return VG_VIBRATION_SIM_REJECTED;
    }

    sim->next_step++;
    return VG_VIBRATION_SIM_SAMPLE;
}

#endif /* VG_PROVIDER_VIBRATION_H */
