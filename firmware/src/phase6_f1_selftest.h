#ifndef VG_PHASE6_F1_SELFTEST_H
#define VG_PHASE6_F1_SELFTEST_H

#include <stdio.h>
#include <math.h>
#include "engine_model.h"

static inline void vg_f1_record(const char *name, bool ok,
                                unsigned *passed, unsigned *total)
{
    (*total)++;
    if (ok) (*passed)++;
    printf("F1_ENGINE_MODEL_TEST %s: %s\n", name, ok ? "PASS" : "FAIL");
}

static inline void run_phase6_f1_engine_model_selftest(void)
{
    unsigned passed = 0u, total = 0u;

    vg_f1_record("SCOPE_SIMULATION_ONLY", VG_SOURCE_SIMULATION != VG_SOURCE_PHYSICAL, &passed, &total);
    vg_f1_record("CAPACITY_AT_LEAST_FOUR", VG_ENGINE_MODEL_MAX_ENGINES >= 4u, &passed, &total);
    vg_f1_record("FOUR_PROFILE_COUNT_CONSTANT", VG_ENGINE_DEMO_FOUR_COUNT == 4u, &passed, &total);

    vg_f1_record("STATE_UNKNOWN_KNOWN", vg_engine_state_is_known(VG_ENGINE_STATE_UNKNOWN), &passed, &total);
    vg_f1_record("STATE_STOPPED_KNOWN", vg_engine_state_is_known(VG_ENGINE_STATE_STOPPED), &passed, &total);
    vg_f1_record("STATE_RUNNING_KNOWN", vg_engine_state_is_known(VG_ENGINE_STATE_RUNNING), &passed, &total);
    vg_f1_record("STATE_FAULT_KNOWN", vg_engine_state_is_known(VG_ENGINE_STATE_FAULT), &passed, &total);
    vg_f1_record("STATE_INVALID_REJECTED", !vg_engine_state_is_known((vg_engine_state_t)99), &passed, &total);

    vg_f1_record("COMM_UNKNOWN_KNOWN", vg_engine_comm_quality_is_known(VG_ENGINE_COMM_UNKNOWN), &passed, &total);
    vg_f1_record("COMM_GOOD_KNOWN", vg_engine_comm_quality_is_known(VG_ENGINE_COMM_GOOD), &passed, &total);
    vg_f1_record("COMM_DEGRADED_KNOWN", vg_engine_comm_quality_is_known(VG_ENGINE_COMM_DEGRADED), &passed, &total);
    vg_f1_record("COMM_LOST_KNOWN", vg_engine_comm_quality_is_known(VG_ENGINE_COMM_LOST), &passed, &total);
    vg_f1_record("COMM_INVALID_REJECTED", !vg_engine_comm_quality_is_known((vg_engine_comm_quality_t)99), &passed, &total);

    vg_engine_model_t model = {0};
    vg_f1_record("MODEL_ZERO_COUNT_REJECTED", !vg_engine_model_init(&model, 0u), &passed, &total);
    vg_f1_record("MODEL_OVER_CAPACITY_REJECTED", !vg_engine_model_init(&model, VG_ENGINE_MODEL_MAX_ENGINES + 1u), &passed, &total);
    vg_f1_record("MODEL_NULL_REJECTED", !vg_engine_model_init(NULL, 4u), &passed, &total);
    vg_f1_record("MODEL_ONE_ENGINE_ACCEPTED", vg_engine_model_init(&model, 1u) && model.engine_count == 1u, &passed, &total);
    vg_f1_record("MODEL_TWO_ENGINE_ACCEPTED", vg_engine_model_init(&model, 2u) && model.engine_count == 2u, &passed, &total);
    vg_f1_record("MODEL_FOUR_ENGINE_ACCEPTED", vg_engine_model_init(&model, 4u) && model.engine_count == 4u, &passed, &total);
    vg_f1_record("MODEL_MAX_ENGINE_ACCEPTED", vg_engine_model_init(&model, VG_ENGINE_MODEL_MAX_ENGINES) && model.engine_count == VG_ENGINE_MODEL_MAX_ENGINES, &passed, &total);

    vg_engine_snapshot_t good = {
        .engine_id = 1u, .source_mode = VG_SOURCE_SIMULATION,
        .state = VG_ENGINE_STATE_RUNNING, .rpm = 2000.0f,
        .temperature_c = 82.0f, .runtime_s = 3600u,
        .alarm_active = false, .communication_quality = VG_ENGINE_COMM_GOOD
    };
    vg_f1_record("SNAPSHOT_RUNNING_CONSISTENT", vg_engine_snapshot_is_consistent(&good), &passed, &total);

    vg_engine_snapshot_t stopped = good;
    stopped.state = VG_ENGINE_STATE_STOPPED; stopped.rpm = 0.0f;
    vg_f1_record("SNAPSHOT_STOPPED_ZERO_RPM", vg_engine_snapshot_is_consistent(&stopped), &passed, &total);

    vg_engine_snapshot_t stopped_bad = stopped; stopped_bad.rpm = 100.0f;
    vg_f1_record("SNAPSHOT_STOPPED_NONZERO_REJECTED", !vg_engine_snapshot_is_consistent(&stopped_bad), &passed, &total);

    vg_engine_snapshot_t physical = good; physical.source_mode = VG_SOURCE_PHYSICAL;
    vg_f1_record("SNAPSHOT_PHYSICAL_REJECTED", !vg_engine_snapshot_is_consistent(&physical), &passed, &total);

    vg_engine_snapshot_t nan_rpm = good; nan_rpm.rpm = NAN;
    vg_f1_record("SNAPSHOT_NAN_RPM_REJECTED", !vg_engine_snapshot_is_consistent(&nan_rpm), &passed, &total);

    vg_engine_snapshot_t neg_rpm = good; neg_rpm.rpm = -1.0f;
    vg_f1_record("SNAPSHOT_NEGATIVE_RPM_REJECTED", !vg_engine_snapshot_is_consistent(&neg_rpm), &passed, &total);

    vg_engine_snapshot_t nan_temp = good; nan_temp.temperature_c = NAN;
    vg_f1_record("SNAPSHOT_NAN_TEMP_REJECTED", !vg_engine_snapshot_is_consistent(&nan_temp), &passed, &total);

    vg_engine_snapshot_t lost = good;
    lost.state = VG_ENGINE_STATE_UNKNOWN; lost.rpm = 0.0f; lost.alarm_active = false; lost.communication_quality = VG_ENGINE_COMM_LOST;
    vg_f1_record("SNAPSHOT_COMM_LOST_EXPLICIT_UNKNOWN", vg_engine_snapshot_is_consistent(&lost), &passed, &total);

    vg_engine_snapshot_t lost_bad = lost; lost_bad.state = VG_ENGINE_STATE_RUNNING;
    vg_f1_record("SNAPSHOT_COMM_LOST_RUNNING_REJECTED", !vg_engine_snapshot_is_consistent(&lost_bad), &passed, &total);

    vg_f1_record("MODEL_INIT_FOR_SET", vg_engine_model_init(&model, 4u), &passed, &total);
    vg_f1_record("MODEL_SET_ENGINE1", vg_engine_model_set(&model, 0u, &good), &passed, &total);

    vg_engine_snapshot_t wrong_id = good; wrong_id.engine_id = 2u;
    vg_f1_record("MODEL_SET_WRONG_ID_REJECTED", !vg_engine_model_set(&model, 0u, &wrong_id), &passed, &total);
    vg_f1_record("MODEL_SET_OOB_REJECTED", !vg_engine_model_set(&model, 4u, &good), &passed, &total);
    vg_f1_record("MODEL_SET_NULL_REJECTED", !vg_engine_model_set(&model, 0u, NULL), &passed, &total);

    vg_engine_snapshot_t out = {0};
    vg_f1_record("MODEL_GET_ENGINE1", vg_engine_model_get(&model, 0u, &out) && out.engine_id == 1u && out.rpm == 2000.0f, &passed, &total);
    vg_f1_record("MODEL_GET_OOB_REJECTED", !vg_engine_model_get(&model, 4u, &out), &passed, &total);
    vg_f1_record("MODEL_GET_NULL_REJECTED", !vg_engine_model_get(&model, 0u, NULL), &passed, &total);

    vg_engine_model_t normal4 = {0};
    vg_f1_record("DEMO_FOUR_NORMAL_BUILD", vg_engine_demo_four_profile(&normal4, false), &passed, &total);
    vg_f1_record("DEMO_FOUR_NORMAL_COUNT", normal4.engine_count == 4u, &passed, &total);
    vg_f1_record("DEMO_FOUR_FIELDS_EXPOSED",
        normal4.engines[0].state == VG_ENGINE_STATE_RUNNING &&
        normal4.engines[0].rpm > 0.0f &&
        isfinite(normal4.engines[0].temperature_c) &&
        normal4.engines[0].runtime_s > 0u &&
        !normal4.engines[0].alarm_active &&
        normal4.engines[0].communication_quality == VG_ENGINE_COMM_GOOD, &passed, &total);

    vg_engine_deviation_config_t cfg = {.warning_threshold_rpm = 250.0f};
    vg_f1_record("DEVIATION_CONFIG_VALID", vg_engine_deviation_config_is_valid(&cfg), &passed, &total);

    vg_engine_deviation_config_t zero_cfg = {.warning_threshold_rpm = 0.0f};
    vg_f1_record("DEVIATION_ZERO_THRESHOLD_REJECTED", !vg_engine_deviation_config_is_valid(&zero_cfg), &passed, &total);

    vg_engine_deviation_config_t nan_cfg = {.warning_threshold_rpm = NAN};
    vg_f1_record("DEVIATION_NAN_THRESHOLD_REJECTED", !vg_engine_deviation_config_is_valid(&nan_cfg), &passed, &total);

    vg_engine_deviation_result_t result = {0};
    vg_f1_record("NORMAL_PROFILE_ENGINE3_EVALUATED", vg_engine_evaluate_rpm_deviation(&normal4, 2u, &cfg, &result), &passed, &total);
    vg_f1_record("NORMAL_PROFILE_ENGINE3_NO_WARNING", result.evaluated && !result.warning && result.engine_id == 3u && result.peer_count == 3u, &passed, &total);

    vg_engine_model_t sim007 = {0};
    vg_f1_record("SIM007_PROFILE_BUILD", vg_engine_demo_four_profile(&sim007, true), &passed, &total);
    vg_f1_record("SIM007_ENGINE3_LOWER", sim007.engines[2].rpm < sim007.engines[0].rpm && sim007.engines[2].rpm < sim007.engines[1].rpm && sim007.engines[2].rpm < sim007.engines[3].rpm, &passed, &total);

    vg_engine_deviation_result_t e3 = {0};
    vg_f1_record("SIM007_ENGINE3_EVALUATED", vg_engine_evaluate_rpm_deviation(&sim007, 2u, &cfg, &e3), &passed, &total);
    vg_f1_record("SIM007_ENGINE3_WARNING", e3.evaluated && e3.warning && e3.engine_id == 3u && e3.absolute_deviation_rpm > cfg.warning_threshold_rpm, &passed, &total);

    vg_engine_deviation_result_t e1 = {0};
    vg_f1_record("SIM007_ENGINE1_EVALUATED", vg_engine_evaluate_rpm_deviation(&sim007, 0u, &cfg, &e1), &passed, &total);
    vg_f1_record("SIM007_ENGINE1_NOT_FALSE_POSITIVE", e1.evaluated && !e1.warning, &passed, &total);

    vg_engine_deviation_result_t e2 = {0};
    vg_f1_record("SIM007_ENGINE2_EVALUATED", vg_engine_evaluate_rpm_deviation(&sim007, 1u, &cfg, &e2), &passed, &total);
    vg_f1_record("SIM007_ENGINE2_NOT_FALSE_POSITIVE", e2.evaluated && !e2.warning, &passed, &total);

    vg_engine_deviation_result_t e4 = {0};
    vg_f1_record("SIM007_ENGINE4_EVALUATED", vg_engine_evaluate_rpm_deviation(&sim007, 3u, &cfg, &e4), &passed, &total);
    vg_f1_record("SIM007_ENGINE4_NOT_FALSE_POSITIVE", e4.evaluated && !e4.warning, &passed, &total);

    vg_engine_model_t lost_peer = sim007;
    lost_peer.engines[1].state = VG_ENGINE_STATE_UNKNOWN;
    lost_peer.engines[1].rpm = 0.0f;
    lost_peer.engines[1].communication_quality = VG_ENGINE_COMM_LOST;
    vg_engine_deviation_result_t isolated = {0};
    vg_f1_record("LOST_PEER_EXCLUDED", vg_engine_evaluate_rpm_deviation(&lost_peer, 2u, &cfg, &isolated) && isolated.peer_count == 2u, &passed, &total);

    vg_engine_model_t lost_target = sim007;
    lost_target.engines[2].state = VG_ENGINE_STATE_UNKNOWN;
    lost_target.engines[2].rpm = 0.0f;
    lost_target.engines[2].communication_quality = VG_ENGINE_COMM_LOST;
    vg_f1_record("LOST_TARGET_NOT_EVALUATED", !vg_engine_evaluate_rpm_deviation(&lost_target, 2u, &cfg, &result), &passed, &total);

    vg_engine_model_t single = {0};
    (void)vg_engine_model_init(&single, 1u);
    vg_f1_record("SINGLE_ENGINE_DEVIATION_REJECTED", !vg_engine_evaluate_rpm_deviation(&single, 0u, &cfg, &result), &passed, &total);
    vg_f1_record("DEVIATION_NULL_MODEL_REJECTED", !vg_engine_evaluate_rpm_deviation(NULL, 0u, &cfg, &result), &passed, &total);
    vg_f1_record("DEVIATION_NULL_CONFIG_REJECTED", !vg_engine_evaluate_rpm_deviation(&sim007, 2u, NULL, &result), &passed, &total);
    vg_f1_record("DEVIATION_NULL_OUTPUT_REJECTED", !vg_engine_evaluate_rpm_deviation(&sim007, 2u, &cfg, NULL), &passed, &total);
    vg_f1_record("DEVIATION_OOB_REJECTED", !vg_engine_evaluate_rpm_deviation(&sim007, 4u, &cfg, &result), &passed, &total);

    printf("PHASE6_F1_ENGINE_MODEL_SELFTEST: %s (%u/%u)\n",
           passed == total ? "PASS" : "FAIL", passed, total);
}

#endif
