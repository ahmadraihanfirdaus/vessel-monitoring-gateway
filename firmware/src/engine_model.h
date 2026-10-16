#ifndef VG_ENGINE_MODEL_H
#define VG_ENGINE_MODEL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>
#include "core_source_mode.h"

#define VG_ENGINE_MODEL_MAX_ENGINES 8u
#define VG_ENGINE_DEMO_FOUR_COUNT 4u

typedef enum {
    VG_ENGINE_STATE_UNKNOWN = 0,
    VG_ENGINE_STATE_STOPPED,
    VG_ENGINE_STATE_RUNNING,
    VG_ENGINE_STATE_FAULT
} vg_engine_state_t;

typedef enum {
    VG_ENGINE_COMM_UNKNOWN = 0,
    VG_ENGINE_COMM_GOOD,
    VG_ENGINE_COMM_DEGRADED,
    VG_ENGINE_COMM_LOST
} vg_engine_comm_quality_t;

typedef struct {
    uint8_t engine_id;
    vg_source_mode_t source_mode;
    vg_engine_state_t state;
    float rpm;
    float temperature_c;
    uint64_t runtime_s;
    bool alarm_active;
    vg_engine_comm_quality_t communication_quality;
} vg_engine_snapshot_t;

typedef struct {
    bool initialized;
    size_t engine_count;
    vg_engine_snapshot_t engines[VG_ENGINE_MODEL_MAX_ENGINES];
} vg_engine_model_t;

typedef struct {
    float warning_threshold_rpm;
} vg_engine_deviation_config_t;

typedef struct {
    bool evaluated;
    bool warning;
    uint8_t engine_id;
    size_t peer_count;
    float engine_rpm;
    float peer_mean_rpm;
    float absolute_deviation_rpm;
    float threshold_rpm;
} vg_engine_deviation_result_t;

static inline bool vg_engine_state_is_known(vg_engine_state_t state)
{
    return state == VG_ENGINE_STATE_UNKNOWN ||
           state == VG_ENGINE_STATE_STOPPED ||
           state == VG_ENGINE_STATE_RUNNING ||
           state == VG_ENGINE_STATE_FAULT;
}

static inline bool vg_engine_comm_quality_is_known(vg_engine_comm_quality_t quality)
{
    return quality == VG_ENGINE_COMM_UNKNOWN ||
           quality == VG_ENGINE_COMM_GOOD ||
           quality == VG_ENGINE_COMM_DEGRADED ||
           quality == VG_ENGINE_COMM_LOST;
}

static inline bool vg_engine_snapshot_is_consistent(const vg_engine_snapshot_t *engine)
{
    if (engine == NULL || engine->engine_id == 0u ||
        engine->source_mode != VG_SOURCE_SIMULATION ||
        !vg_engine_state_is_known(engine->state) ||
        !vg_engine_comm_quality_is_known(engine->communication_quality) ||
        !isfinite(engine->rpm) || engine->rpm < 0.0f ||
        !isfinite(engine->temperature_c)) {
        return false;
    }

    if (engine->communication_quality == VG_ENGINE_COMM_LOST ||
        engine->communication_quality == VG_ENGINE_COMM_UNKNOWN) {
        return engine->state == VG_ENGINE_STATE_UNKNOWN &&
               engine->rpm == 0.0f &&
               !engine->alarm_active;
    }

    if (engine->state == VG_ENGINE_STATE_UNKNOWN) {
        return false;
    }

    if (engine->state == VG_ENGINE_STATE_STOPPED && engine->rpm != 0.0f) {
        return false;
    }

    return true;
}

static inline bool vg_engine_model_init(vg_engine_model_t *model, size_t engine_count)
{
    if (model == NULL || engine_count == 0u ||
        engine_count > VG_ENGINE_MODEL_MAX_ENGINES) {
        return false;
    }

    vg_engine_model_t fresh = {0};
    fresh.initialized = true;
    fresh.engine_count = engine_count;

    for (size_t i = 0; i < engine_count; ++i) {
        fresh.engines[i] = (vg_engine_snapshot_t){
            .engine_id = (uint8_t)(i + 1u),
            .source_mode = VG_SOURCE_SIMULATION,
            .state = VG_ENGINE_STATE_UNKNOWN,
            .rpm = 0.0f,
            .temperature_c = 0.0f,
            .runtime_s = 0u,
            .alarm_active = false,
            .communication_quality = VG_ENGINE_COMM_UNKNOWN
        };
    }

    *model = fresh;
    return true;
}

static inline bool vg_engine_model_set(vg_engine_model_t *model,
                                       size_t index,
                                       const vg_engine_snapshot_t *engine)
{
    if (model == NULL || engine == NULL || !model->initialized ||
        model->engine_count == 0u ||
        model->engine_count > VG_ENGINE_MODEL_MAX_ENGINES ||
        index >= model->engine_count ||
        engine->engine_id != (uint8_t)(index + 1u) ||
        !vg_engine_snapshot_is_consistent(engine)) {
        return false;
    }

    model->engines[index] = *engine;
    return true;
}

static inline bool vg_engine_model_get(const vg_engine_model_t *model,
                                       size_t index,
                                       vg_engine_snapshot_t *out)
{
    if (model == NULL || out == NULL || !model->initialized ||
        model->engine_count == 0u ||
        model->engine_count > VG_ENGINE_MODEL_MAX_ENGINES ||
        index >= model->engine_count) {
        return false;
    }

    *out = model->engines[index];
    return true;
}

static inline bool vg_engine_demo_four_profile(vg_engine_model_t *model,
                                               bool engine3_deviation)
{
    if (!vg_engine_model_init(model, VG_ENGINE_DEMO_FOUR_COUNT)) {
        return false;
    }

    static const float normal_rpm[VG_ENGINE_DEMO_FOUR_COUNT] = {
        2000.0f, 2020.0f, 2010.0f, 1990.0f
    };
    static const float temp_c[VG_ENGINE_DEMO_FOUR_COUNT] = {
        82.0f, 83.0f, 84.0f, 82.5f
    };

    for (size_t i = 0; i < VG_ENGINE_DEMO_FOUR_COUNT; ++i) {
        vg_engine_snapshot_t engine = {
            .engine_id = (uint8_t)(i + 1u),
            .source_mode = VG_SOURCE_SIMULATION,
            .state = VG_ENGINE_STATE_RUNNING,
            .rpm = normal_rpm[i],
            .temperature_c = temp_c[i],
            .runtime_s = 3600u + (uint64_t)(i * 60u),
            .alarm_active = false,
            .communication_quality = VG_ENGINE_COMM_GOOD
        };
        if (engine3_deviation && i == 2u) {
            engine.rpm = 1500.0f;
        }
        if (!vg_engine_model_set(model, i, &engine)) {
            return false;
        }
    }

    return true;
}

static inline bool vg_engine_deviation_config_is_valid(
    const vg_engine_deviation_config_t *config)
{
    return config != NULL &&
           isfinite(config->warning_threshold_rpm) &&
           config->warning_threshold_rpm > 0.0f;
}

static inline bool vg_engine_is_rpm_peer_eligible(
    const vg_engine_snapshot_t *engine)
{
    return vg_engine_snapshot_is_consistent(engine) &&
           engine->state == VG_ENGINE_STATE_RUNNING &&
           (engine->communication_quality == VG_ENGINE_COMM_GOOD ||
            engine->communication_quality == VG_ENGINE_COMM_DEGRADED);
}

static inline bool vg_engine_evaluate_rpm_deviation(
    const vg_engine_model_t *model,
    size_t index,
    const vg_engine_deviation_config_t *config,
    vg_engine_deviation_result_t *out)
{
    if (model == NULL || config == NULL || out == NULL ||
        !model->initialized || model->engine_count < 2u ||
        model->engine_count > VG_ENGINE_MODEL_MAX_ENGINES ||
        index >= model->engine_count ||
        !vg_engine_deviation_config_is_valid(config) ||
        !vg_engine_is_rpm_peer_eligible(&model->engines[index])) {
        return false;
    }

    float peer_sum = 0.0f;
    size_t peer_count = 0u;

    for (size_t i = 0; i < model->engine_count; ++i) {
        if (i == index) continue;
        if (vg_engine_is_rpm_peer_eligible(&model->engines[i])) {
            peer_sum += model->engines[i].rpm;
            peer_count++;
        }
    }

    if (peer_count == 0u) {
        return false;
    }

    const float peer_mean = peer_sum / (float)peer_count;
    const float deviation = fabsf(model->engines[index].rpm - peer_mean);

    *out = (vg_engine_deviation_result_t){
        .evaluated = true,
        .warning = deviation > config->warning_threshold_rpm,
        .engine_id = model->engines[index].engine_id,
        .peer_count = peer_count,
        .engine_rpm = model->engines[index].rpm,
        .peer_mean_rpm = peer_mean,
        .absolute_deviation_rpm = deviation,
        .threshold_rpm = config->warning_threshold_rpm
    };
    return true;
}

#endif
