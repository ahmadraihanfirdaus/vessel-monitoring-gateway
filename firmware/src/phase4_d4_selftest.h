#ifndef VG_PHASE4_D4_SELFTEST_H
#define VG_PHASE4_D4_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <math.h>

#include "provider_temperature.h"

/* Development-only IF-04 / SAF-006 provider self-test. */
#define VG_D4_EXPECTED_CASES 67u

static inline void vg_d4_record(
    const char *name,
    bool success,
    size_t *passed,
    size_t *total
)
{
    printf("D4_TEMPERATURE_TEST %s: %s\n", name, success ? "PASS" : "FAIL");
    (*total)++;
    if (success) {
        (*passed)++;
    }
}

static inline void run_phase4_d4_temperature_provider_selftest(void)
{
    size_t passed = 0u;
    size_t total = 0u;

    vg_temperature_sample_t sample = {
        .meta = {
            .source_mode = VG_SOURCE_SIMULATION,
            .quality = VG_QUALITY_VALID,
            .sampled_at_ms = 100u,
            .sequence = 1u
        },
        .has_value = true,
        .temperature_c = 25.0f
    };

    vg_d4_record("VALID_FINITE_CURRENT",
                 vg_temperature_sample_is_consistent(&sample) &&
                 vg_temperature_sample_is_current(&sample),
                 &passed, &total);

    sample.temperature_c = -20.0f;
    vg_d4_record("VALID_NEGATIVE_CURRENT",
                 vg_temperature_sample_is_consistent(&sample) &&
                 vg_temperature_sample_is_current(&sample),
                 &passed, &total);

    sample.temperature_c = 0.0f;
    vg_d4_record("VALID_ZERO_CURRENT",
                 vg_temperature_sample_is_consistent(&sample) &&
                 vg_temperature_sample_is_current(&sample),
                 &passed, &total);

    sample.temperature_c = NAN;
    vg_d4_record("VALID_NAN_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.temperature_c = INFINITY;
    vg_d4_record("VALID_POS_INF_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.temperature_c = -INFINITY;
    vg_d4_record("VALID_NEG_INF_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.temperature_c = 25.0f;
    sample.has_value = false;
    vg_d4_record("VALID_NO_VALUE_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_STALE;
    sample.has_value = true;
    sample.temperature_c = 40.0f;
    vg_d4_record("STALE_VALUE_ACCEPTED_NOT_CURRENT",
                 vg_temperature_sample_is_consistent(&sample) &&
                 !vg_temperature_sample_is_current(&sample),
                 &passed, &total);

    sample.has_value = false;
    vg_d4_record("STALE_NO_VALUE_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_MISSING;
    sample.has_value = false;
    vg_d4_record("MISSING_NO_VALUE_ACCEPTED",
                 vg_temperature_sample_is_consistent(&sample) &&
                 !vg_temperature_sample_is_current(&sample),
                 &passed, &total);

    sample.has_value = true;
    sample.temperature_c = 10.0f;
    vg_d4_record("MISSING_VALUE_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_INVALID;
    sample.has_value = false;
    vg_d4_record("INVALID_NO_VALUE_ACCEPTED",
                 vg_temperature_sample_is_consistent(&sample) &&
                 !vg_temperature_sample_is_current(&sample),
                 &passed, &total);

    sample.has_value = true;
    vg_d4_record("INVALID_VALUE_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_UNKNOWN;
    sample.has_value = false;
    vg_d4_record("UNKNOWN_NO_VALUE_ACCEPTED",
                 vg_temperature_sample_is_consistent(&sample) &&
                 !vg_temperature_sample_is_current(&sample),
                 &passed, &total);

    sample.has_value = true;
    vg_d4_record("UNKNOWN_VALUE_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.source_mode = VG_SOURCE_PHYSICAL;
    sample.has_value = false;
    vg_d4_record("PHYSICAL_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.source_mode = (vg_source_mode_t)99;
    vg_d4_record("UNKNOWN_SOURCE_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.source_mode = VG_SOURCE_SIMULATION;
    sample.meta.sequence = 0u;
    vg_d4_record("ZERO_SEQUENCE_REJECTED",
                 !vg_temperature_sample_is_consistent(&sample),
                 &passed, &total);

    vg_d4_record("NULL_SAMPLE_REJECTED",
                 !vg_temperature_sample_is_consistent(NULL) &&
                 !vg_temperature_sample_is_current(NULL),
                 &passed, &total);

    const vg_temperature_demo_thresholds_t thresholds = {
        .warning_high_c = 40.0f,
        .alarm_high_c = 60.0f
    };
    vg_d4_record("THRESHOLDS_VALID",
                 vg_temperature_demo_thresholds_are_consistent(&thresholds),
                 &passed, &total);

    const vg_temperature_demo_thresholds_t equal_thresholds = {
        .warning_high_c = 50.0f,
        .alarm_high_c = 50.0f
    };
    vg_d4_record("THRESHOLDS_EQUAL_REJECTED",
                 !vg_temperature_demo_thresholds_are_consistent(&equal_thresholds),
                 &passed, &total);

    const vg_temperature_demo_thresholds_t reversed_thresholds = {
        .warning_high_c = 70.0f,
        .alarm_high_c = 60.0f
    };
    vg_d4_record("THRESHOLDS_REVERSED_REJECTED",
                 !vg_temperature_demo_thresholds_are_consistent(&reversed_thresholds),
                 &passed, &total);

    const vg_temperature_demo_thresholds_t nan_warning = {
        .warning_high_c = NAN,
        .alarm_high_c = 60.0f
    };
    vg_d4_record("THRESHOLDS_NAN_WARNING_REJECTED",
                 !vg_temperature_demo_thresholds_are_consistent(&nan_warning),
                 &passed, &total);

    const vg_temperature_demo_thresholds_t inf_alarm = {
        .warning_high_c = 40.0f,
        .alarm_high_c = INFINITY
    };
    vg_d4_record("THRESHOLDS_INF_ALARM_REJECTED",
                 !vg_temperature_demo_thresholds_are_consistent(&inf_alarm),
                 &passed, &total);

    vg_d4_record("THRESHOLDS_NULL_REJECTED",
                 !vg_temperature_demo_thresholds_are_consistent(NULL),
                 &passed, &total);

    sample.meta.source_mode = VG_SOURCE_SIMULATION;
    sample.meta.quality = VG_QUALITY_VALID;
    sample.meta.sequence = 1u;
    sample.has_value = true;
    sample.temperature_c = 39.99f;
    vg_d4_record("DEMO_BELOW_WARNING",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_BELOW_WARNING,
                 &passed, &total);

    sample.temperature_c = 40.0f;
    vg_d4_record("DEMO_WARNING_BOUNDARY",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_WARNING,
                 &passed, &total);

    sample.temperature_c = 59.99f;
    vg_d4_record("DEMO_WARNING_BAND",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_WARNING,
                 &passed, &total);

    sample.temperature_c = 60.0f;
    vg_d4_record("DEMO_ALARM_BOUNDARY",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_ALARM,
                 &passed, &total);

    sample.temperature_c = 80.0f;
    vg_d4_record("DEMO_ABOVE_ALARM",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_ALARM,
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_STALE;
    vg_d4_record("DEMO_STALE_NOT_CURRENT",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_NOT_CURRENT,
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_MISSING;
    sample.has_value = false;
    vg_d4_record("DEMO_MISSING_NOT_CURRENT",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_NOT_CURRENT,
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_INVALID;
    vg_d4_record("DEMO_INVALID_NOT_CURRENT",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_NOT_CURRENT,
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_UNKNOWN;
    vg_d4_record("DEMO_UNKNOWN_NOT_CURRENT",
                 vg_temperature_demo_evaluate(&sample, &thresholds) ==
                     VG_TEMPERATURE_DEMO_NOT_CURRENT,
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_VALID;
    sample.has_value = true;
    sample.temperature_c = 25.0f;
    vg_d4_record("DEMO_BAD_THRESHOLDS_REJECTED",
                 vg_temperature_demo_evaluate(&sample, &reversed_thresholds) ==
                     VG_TEMPERATURE_DEMO_REJECTED,
                 &passed, &total);

    vg_d4_record("DEMO_NULL_SAMPLE_REJECTED",
                 vg_temperature_demo_evaluate(NULL, &thresholds) ==
                     VG_TEMPERATURE_DEMO_REJECTED,
                 &passed, &total);

    vg_d4_record("DEMO_NULL_THRESHOLDS_REJECTED",
                 vg_temperature_demo_evaluate(&sample, NULL) ==
                     VG_TEMPERATURE_DEMO_REJECTED,
                 &passed, &total);

    vg_temperature_sample_t bench = {0};
    vg_d4_record("BENCH_VALID_VALUE",
                 vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_VALID, true, 32.5f, 1000u, 1u) &&
                 bench.meta.source_mode == VG_SOURCE_BENCH_TEST &&
                 vg_temperature_sample_is_current(&bench),
                 &passed, &total);

    vg_d4_record("BENCH_STALE_VALUE",
                 vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_STALE, true, 33.0f, 1100u, 2u) &&
                 vg_temperature_sample_is_consistent(&bench) &&
                 !vg_temperature_sample_is_current(&bench),
                 &passed, &total);

    vg_d4_record("BENCH_MISSING_NO_VALUE",
                 vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_MISSING, false, 0.0f, 1200u, 3u),
                 &passed, &total);

    vg_d4_record("BENCH_INVALID_NO_VALUE",
                 vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_INVALID, false, 0.0f, 1300u, 4u),
                 &passed, &total);

    vg_d4_record("BENCH_UNKNOWN_NO_VALUE",
                 vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_UNKNOWN, false, 0.0f, 1400u, 5u),
                 &passed, &total);

    vg_d4_record("BENCH_VALID_NO_VALUE_REJECTED",
                 !vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_VALID, false, 0.0f, 1500u, 6u),
                 &passed, &total);

    vg_d4_record("BENCH_MISSING_VALUE_REJECTED",
                 !vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_MISSING, true, 10.0f, 1600u, 7u),
                 &passed, &total);

    vg_d4_record("BENCH_NAN_REJECTED",
                 !vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_VALID, true, NAN, 1700u, 8u),
                 &passed, &total);

    vg_d4_record("BENCH_ZERO_SEQUENCE_REJECTED",
                 !vg_temperature_bench_build_sample(
                     &bench, VG_QUALITY_VALID, true, 20.0f, 1800u, 0u),
                 &passed, &total);

    vg_d4_record("BENCH_NULL_REJECTED",
                 !vg_temperature_bench_build_sample(
                     NULL, VG_QUALITY_VALID, true, 20.0f, 1800u, 9u),
                 &passed, &total);

    vg_temperature_sim_t sim = {0};
    vg_d4_record("SIM_INIT",
                 vg_temperature_sim_init(&sim, 5000u, 250u),
                 &passed, &total);

    vg_temperature_sim_t bad_interval = {0};
    vg_d4_record("SIM_ZERO_INTERVAL_REJECTED",
                 !vg_temperature_sim_init(&bad_interval, 0u, 0u),
                 &passed, &total);

    vg_d4_record("SIM_NULL_INIT_REJECTED",
                 !vg_temperature_sim_init(NULL, 0u, 100u),
                 &passed, &total);

    static const vg_data_quality_t expected_quality[VG_TEMPERATURE_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_STALE,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_VALID
    };
    static const bool expected_has_value[VG_TEMPERATURE_SIM_STEPS] = {
        true, true, true, true, false, false, false, true
    };
    static const float expected_value[VG_TEMPERATURE_SIM_STEPS] = {
        25.0f, 45.0f, 65.0f, 65.0f, 0.0f, 0.0f, 0.0f, 30.0f
    };

    bool deterministic = true;
    bool threshold_sequence = true;
    vg_temperature_sample_t simulated = {0};
    for (size_t i = 0u; i < VG_TEMPERATURE_SIM_STEPS; ++i) {
        const vg_temperature_sim_result_t result =
            vg_temperature_sim_next(&sim, &simulated);
        deterministic = deterministic &&
            result == VG_TEMPERATURE_SIM_SAMPLE &&
            simulated.meta.source_mode == VG_SOURCE_SIMULATION &&
            simulated.meta.quality == expected_quality[i] &&
            simulated.meta.sequence == (uint32_t)(i + 1u) &&
            simulated.meta.sampled_at_ms == 5000u + 250u * (uint64_t)i &&
            simulated.has_value == expected_has_value[i] &&
            (!expected_has_value[i] || simulated.temperature_c == expected_value[i]) &&
            vg_temperature_sample_is_consistent(&simulated);

        const vg_temperature_demo_result_t eval =
            vg_temperature_demo_evaluate(&simulated, &thresholds);
        static const vg_temperature_demo_result_t expected_eval[VG_TEMPERATURE_SIM_STEPS] = {
            VG_TEMPERATURE_DEMO_BELOW_WARNING,
            VG_TEMPERATURE_DEMO_WARNING,
            VG_TEMPERATURE_DEMO_ALARM,
            VG_TEMPERATURE_DEMO_NOT_CURRENT,
            VG_TEMPERATURE_DEMO_NOT_CURRENT,
            VG_TEMPERATURE_DEMO_NOT_CURRENT,
            VG_TEMPERATURE_DEMO_NOT_CURRENT,
            VG_TEMPERATURE_DEMO_BELOW_WARNING
        };
        threshold_sequence = threshold_sequence && eval == expected_eval[i];
    }

    vg_d4_record("SIM_DETERMINISTIC_SEQUENCE", deterministic, &passed, &total);
    vg_d4_record("SIM_THRESHOLD_SEQUENCE", threshold_sequence, &passed, &total);
    vg_d4_record("SIM_COMPLETE",
                 vg_temperature_sim_next(&sim, &simulated) ==
                     VG_TEMPERATURE_SIM_COMPLETE,
                 &passed, &total);

    vg_temperature_sim_t uninitialized = {0};
    vg_d4_record("SIM_UNINITIALIZED_REJECTED",
                 vg_temperature_sim_next(&uninitialized, &simulated) ==
                     VG_TEMPERATURE_SIM_REJECTED,
                 &passed, &total);

    vg_d4_record("SIM_NULL_REJECTED",
                 vg_temperature_sim_next(NULL, &simulated) ==
                     VG_TEMPERATURE_SIM_REJECTED,
                 &passed, &total);

    vg_d4_record("SIM_NULL_OUTPUT_REJECTED",
                 vg_temperature_sim_next(&sim, NULL) ==
                     VG_TEMPERATURE_SIM_REJECTED,
                 &passed, &total);

    vg_temperature_sim_t overflow = {0};
    const bool overflow_init = vg_temperature_sim_init(
        &overflow, UINT64_MAX - 1u, 2u);
    uint64_t timestamp = 0u;
    vg_d4_record("SIM_TIMESTAMP_OVERFLOW_REJECTED",
                 overflow_init &&
                 !vg_temperature_sim_timestamp(&overflow, 1u, &timestamp),
                 &passed, &total);

    vg_temperature_sim_t timestamp_sim = {0};
    const bool timestamp_init = vg_temperature_sim_init(
        &timestamp_sim, 123u, 10u);
    vg_d4_record("SIM_TIMESTAMP_STEP0",
                 timestamp_init &&
                 vg_temperature_sim_timestamp(&timestamp_sim, 0u, &timestamp) &&
                 timestamp == 123u,
                 &passed, &total);

    vg_d4_record("SIM_TIMESTAMP_OUT_OF_RANGE",
                 !vg_temperature_sim_timestamp(
                     &timestamp_sim, VG_TEMPERATURE_SIM_STEPS, &timestamp),
                 &passed, &total);

    vg_d4_record("SIM_SAMPLE_OUT_OF_RANGE",
                 !vg_temperature_sim_sample_for_step(
                     &timestamp_sim, VG_TEMPERATURE_SIM_STEPS, &simulated),
                 &passed, &total);

    vg_d4_record("SIM_SAMPLE_NULL_REJECTED",
                 !vg_temperature_sim_sample_for_step(&timestamp_sim, 0u, NULL),
                 &passed, &total);

    vg_temperature_sample_t check = {0};
    const bool step3_ok = vg_temperature_sim_sample_for_step(&timestamp_sim, 3u, &check);
    vg_d4_record("SIM_STALE_PRESENT",
                 step3_ok && check.meta.quality == VG_QUALITY_STALE &&
                 check.has_value && !vg_temperature_sample_is_current(&check),
                 &passed, &total);

    const bool step4_ok = vg_temperature_sim_sample_for_step(&timestamp_sim, 4u, &check);
    vg_d4_record("SIM_MISSING_PRESENT",
                 step4_ok && check.meta.quality == VG_QUALITY_MISSING &&
                 !check.has_value,
                 &passed, &total);

    const bool step5_ok = vg_temperature_sim_sample_for_step(&timestamp_sim, 5u, &check);
    vg_d4_record("SIM_INVALID_PRESENT",
                 step5_ok && check.meta.quality == VG_QUALITY_INVALID &&
                 !check.has_value,
                 &passed, &total);

    const bool step6_ok = vg_temperature_sim_sample_for_step(&timestamp_sim, 6u, &check);
    vg_d4_record("SIM_UNKNOWN_PRESENT",
                 step6_ok && check.meta.quality == VG_QUALITY_UNKNOWN &&
                 !check.has_value,
                 &passed, &total);

    const bool step7_ok = vg_temperature_sim_sample_for_step(&timestamp_sim, 7u, &check);
    vg_d4_record("SIM_RECOVERY_VALID",
                 step7_ok && check.meta.quality == VG_QUALITY_VALID &&
                 check.has_value && check.temperature_c == 30.0f &&
                 vg_temperature_sample_is_current(&check),
                 &passed, &total);

    vg_d4_record("CASE_COUNT_EXACT",
                 total + 1u == VG_D4_EXPECTED_CASES,
                 &passed, &total);

    printf("PHASE4_D4_TEMPERATURE_PROVIDER_SELFTEST: %s (%u/%u)\n",
           passed == total && total == VG_D4_EXPECTED_CASES ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)total);
}

#endif /* VG_PHASE4_D4_SELFTEST_H */
