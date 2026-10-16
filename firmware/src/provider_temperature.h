#ifndef VG_PROVIDER_TEMPERATURE_H
#define VG_PROVIDER_TEMPERATURE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>

#include "provider_contract.h"

/*
 * IF-04 / SAF-006 development provider.
 *
 * Compartment temperature is represented as temperature_c plus explicit
 * quality metadata. DS18B20 is only a future controlled-bench reference.
 * This module has no 1-Wire bus access, GPIO/pull-up design, probe enclosure,
 * calibration, marine placement, or physical-vessel meaning.
 *
 * Demo thresholds are configurable test parameters only. They do not define
 * a vessel safety limit, machinery limit, trip point, or control action.
 */

typedef struct {
    vg_provider_meta_t meta;
    bool has_value;
    float temperature_c;
} vg_temperature_sample_t;

typedef struct {
    float warning_high_c;
    float alarm_high_c;
} vg_temperature_demo_thresholds_t;

typedef enum {
    VG_TEMPERATURE_DEMO_REJECTED = 0,
    VG_TEMPERATURE_DEMO_NOT_CURRENT,
    VG_TEMPERATURE_DEMO_BELOW_WARNING,
    VG_TEMPERATURE_DEMO_WARNING,
    VG_TEMPERATURE_DEMO_ALARM
} vg_temperature_demo_result_t;

static inline bool vg_temperature_sample_is_consistent(
    const vg_temperature_sample_t *sample
)
{
    if (sample == NULL || !vg_provider_meta_is_consistent(&sample->meta)) {
        return false;
    }

    if (sample->meta.quality == VG_QUALITY_VALID ||
        sample->meta.quality == VG_QUALITY_STALE) {
        return sample->has_value && isfinite(sample->temperature_c);
    }

    if (sample->meta.quality == VG_QUALITY_INVALID ||
        sample->meta.quality == VG_QUALITY_MISSING ||
        sample->meta.quality == VG_QUALITY_UNKNOWN) {
        return !sample->has_value;
    }

    return false;
}

static inline bool vg_temperature_sample_is_current(
    const vg_temperature_sample_t *sample
)
{
    return sample != NULL &&
           vg_temperature_sample_is_consistent(sample) &&
           sample->meta.quality == VG_QUALITY_VALID;
}

static inline bool vg_temperature_demo_thresholds_are_consistent(
    const vg_temperature_demo_thresholds_t *thresholds
)
{
    return thresholds != NULL &&
           isfinite(thresholds->warning_high_c) &&
           isfinite(thresholds->alarm_high_c) &&
           thresholds->warning_high_c < thresholds->alarm_high_c;
}

static inline vg_temperature_demo_result_t vg_temperature_demo_evaluate(
    const vg_temperature_sample_t *sample,
    const vg_temperature_demo_thresholds_t *thresholds
)
{
    if (sample == NULL ||
        thresholds == NULL ||
        !vg_temperature_sample_is_consistent(sample) ||
        !vg_temperature_demo_thresholds_are_consistent(thresholds)) {
        return VG_TEMPERATURE_DEMO_REJECTED;
    }

    if (!vg_temperature_sample_is_current(sample)) {
        return VG_TEMPERATURE_DEMO_NOT_CURRENT;
    }

    if (sample->temperature_c >= thresholds->alarm_high_c) {
        return VG_TEMPERATURE_DEMO_ALARM;
    }

    if (sample->temperature_c >= thresholds->warning_high_c) {
        return VG_TEMPERATURE_DEMO_WARNING;
    }

    return VG_TEMPERATURE_DEMO_BELOW_WARNING;
}

/*
 * Controlled-bench constructor from an already decoded Celsius value and
 * quality. A future reviewed DS18B20 bench driver owns 1-Wire acquisition,
 * electrical design, CRC handling, conversion timing, and raw decoding.
 */
static inline bool vg_temperature_bench_build_sample(
    vg_temperature_sample_t *out,
    vg_data_quality_t quality,
    bool has_value,
    float temperature_c,
    uint64_t sampled_at_ms,
    uint32_t sequence
)
{
    if (out == NULL) {
        return false;
    }

    vg_temperature_sample_t candidate = {0};

    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_BENCH_TEST,
            quality,
            sampled_at_ms,
            sequence)) {
        return false;
    }

    candidate.has_value = has_value;
    candidate.temperature_c = temperature_c;

    if (!vg_temperature_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

#define VG_TEMPERATURE_SIM_STEPS 8u

typedef enum {
    VG_TEMPERATURE_SIM_REJECTED = 0,
    VG_TEMPERATURE_SIM_SAMPLE,
    VG_TEMPERATURE_SIM_COMPLETE
} vg_temperature_sim_result_t;

typedef struct {
    bool initialized;
    size_t next_step;
    uint64_t first_sample_ms;
    uint64_t interval_ms;
} vg_temperature_sim_t;

static inline bool vg_temperature_sim_init(
    vg_temperature_sim_t *sim,
    uint64_t first_sample_ms,
    uint64_t interval_ms
)
{
    if (sim == NULL || interval_ms == 0u) {
        return false;
    }

    vg_temperature_sim_t fresh = {
        .initialized = true,
        .next_step = 0u,
        .first_sample_ms = first_sample_ms,
        .interval_ms = interval_ms
    };

    *sim = fresh;
    return true;
}

static inline bool vg_temperature_sim_timestamp(
    const vg_temperature_sim_t *sim,
    size_t step,
    uint64_t *out_sampled_at_ms
)
{
    if (sim == NULL ||
        out_sampled_at_ms == NULL ||
        !sim->initialized ||
        step >= VG_TEMPERATURE_SIM_STEPS) {
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

static inline bool vg_temperature_sim_sample_for_step(
    const vg_temperature_sim_t *sim,
    size_t step,
    vg_temperature_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized ||
        step >= VG_TEMPERATURE_SIM_STEPS) {
        return false;
    }

    static const vg_data_quality_t quality[VG_TEMPERATURE_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_STALE,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_VALID
    };

    static const bool has_value[VG_TEMPERATURE_SIM_STEPS] = {
        true, true, true, true, false, false, false, true
    };

    static const float temperature_c[VG_TEMPERATURE_SIM_STEPS] = {
        25.0f, 45.0f, 65.0f, 65.0f, 0.0f, 0.0f, 0.0f, 30.0f
    };

    uint64_t sampled_at_ms = 0u;
    if (!vg_temperature_sim_timestamp(sim, step, &sampled_at_ms)) {
        return false;
    }

    vg_temperature_sample_t candidate = {0};
    if (!vg_provider_meta_init(
            &candidate.meta,
            VG_SOURCE_SIMULATION,
            quality[step],
            sampled_at_ms,
            (uint32_t)(step + 1u))) {
        return false;
    }

    candidate.has_value = has_value[step];
    candidate.temperature_c = temperature_c[step];

    if (!vg_temperature_sample_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

static inline vg_temperature_sim_result_t vg_temperature_sim_next(
    vg_temperature_sim_t *sim,
    vg_temperature_sample_t *out
)
{
    if (sim == NULL || out == NULL || !sim->initialized) {
        return VG_TEMPERATURE_SIM_REJECTED;
    }

    if (sim->next_step >= VG_TEMPERATURE_SIM_STEPS) {
        return VG_TEMPERATURE_SIM_COMPLETE;
    }

    if (!vg_temperature_sim_sample_for_step(sim, sim->next_step, out)) {
        return VG_TEMPERATURE_SIM_REJECTED;
    }

    sim->next_step++;
    return VG_TEMPERATURE_SIM_SAMPLE;
}

#endif /* VG_PROVIDER_TEMPERATURE_H */
