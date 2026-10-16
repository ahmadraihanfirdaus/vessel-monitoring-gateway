#ifndef VG_PHASE6_F2_FORMAL_SCENARIOS_H
#define VG_PHASE6_F2_FORMAL_SCENARIOS_H

#include <stdbool.h>
#include <stdio.h>
#include "engine_model.h"

static inline void vg_f2_check(const char *name, bool ok,
                               unsigned *passed, unsigned *total)
{
    (*total)++;
    if (ok) {
        (*passed)++;
    }
    printf("F2_SIM007_CHECK %s: %s\n", name, ok ? "PASS" : "FAIL");
}

static inline bool vg_f2_run_sim007_scenario(void)
{
    unsigned passed = 0u;
    unsigned total = 0u;

    vg_engine_model_t model = {0};
    const bool profile_ok = vg_engine_demo_four_profile(&model, true);

    vg_f2_check(
        "FOUR_ENGINE_PROFILE",
        profile_ok &&
        model.initialized &&
        model.engine_count == VG_ENGINE_DEMO_FOUR_COUNT &&
        model.engine_count == 4u,
        &passed, &total);

    /*
     * Dedicated software-simulation scenario inputs for SIM-007.
     * These are demonstration values, not vessel-calibrated acceptance limits.
     */
    const bool input_shape_ok =
        profile_ok &&
        model.engines[0].engine_id == 1u &&
        model.engines[1].engine_id == 2u &&
        model.engines[2].engine_id == 3u &&
        model.engines[3].engine_id == 4u &&
        model.engines[0].source_mode == VG_SOURCE_SIMULATION &&
        model.engines[1].source_mode == VG_SOURCE_SIMULATION &&
        model.engines[2].source_mode == VG_SOURCE_SIMULATION &&
        model.engines[3].source_mode == VG_SOURCE_SIMULATION &&
        model.engines[0].state == VG_ENGINE_STATE_RUNNING &&
        model.engines[1].state == VG_ENGINE_STATE_RUNNING &&
        model.engines[2].state == VG_ENGINE_STATE_RUNNING &&
        model.engines[3].state == VG_ENGINE_STATE_RUNNING &&
        model.engines[0].rpm == 2000.0f &&
        model.engines[1].rpm == 2020.0f &&
        model.engines[2].rpm == 1500.0f &&
        model.engines[3].rpm == 1990.0f &&
        model.engines[2].rpm < model.engines[0].rpm &&
        model.engines[2].rpm < model.engines[1].rpm &&
        model.engines[2].rpm < model.engines[3].rpm;

    vg_f2_check("INPUT_ENGINE3_LOWER", input_shape_ok, &passed, &total);

    vg_engine_deviation_config_t cfg = {
        .warning_threshold_rpm = 250.0f
    };

    vg_f2_check(
        "CONFIGURABLE_THRESHOLD",
        vg_engine_deviation_config_is_valid(&cfg) &&
        cfg.warning_threshold_rpm == 250.0f,
        &passed, &total);

    vg_engine_deviation_result_t e1 = {0};
    vg_engine_deviation_result_t e2 = {0};
    vg_engine_deviation_result_t e3 = {0};
    vg_engine_deviation_result_t e4 = {0};

    const bool e1_ok =
        vg_engine_evaluate_rpm_deviation(&model, 0u, &cfg, &e1);
    const bool e2_ok =
        vg_engine_evaluate_rpm_deviation(&model, 1u, &cfg, &e2);
    const bool e3_ok =
        vg_engine_evaluate_rpm_deviation(&model, 2u, &cfg, &e3);
    const bool e4_ok =
        vg_engine_evaluate_rpm_deviation(&model, 3u, &cfg, &e4);

    vg_f2_check(
        "ENGINE3_EVALUATED",
        e3_ok &&
        e3.evaluated &&
        e3.engine_id == 3u &&
        e3.peer_count == 3u &&
        e3.engine_rpm == 1500.0f &&
        e3.threshold_rpm == cfg.warning_threshold_rpm,
        &passed, &total);

    vg_f2_check(
        "ENGINE3_DEVIATION_WARNING",
        e3_ok &&
        e3.evaluated &&
        e3.warning &&
        e3.absolute_deviation_rpm > e3.threshold_rpm,
        &passed, &total);

    vg_f2_check(
        "PEERS_NO_FALSE_WARNING",
        e1_ok && e1.evaluated && !e1.warning &&
        e2_ok && e2.evaluated && !e2.warning &&
        e4_ok && e4.evaluated && !e4.warning,
        &passed, &total);

    return passed == total && total == 6u;
}

static inline void run_phase6_f2_formal_scenarios(void)
{
    unsigned passed = 0u;
    const unsigned total = 1u;

    const bool sim007_ok = vg_f2_run_sim007_scenario();
    if (sim007_ok) {
        passed++;
    }

    printf("F2_FORMAL_SCENARIO SIM-007: %s\n",
           sim007_ok ? "PASS" : "FAIL");
    printf("PHASE6_F2_FORMAL_SCENARIOS: %s (%u/%u)\n",
           passed == total ? "PASS" : "FAIL",
           passed, total);
}

#endif
