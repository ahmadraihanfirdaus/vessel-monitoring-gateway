#ifndef VG_PHASE4_D5_SELFTEST_H
#define VG_PHASE4_D5_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "provider_attitude.h"

/* Development-only IF-05 / MOT-001 provider self-test. */
#define VG_D5_EXPECTED_CASES 54u

static inline void vg_d5_record(
    const char *name,
    bool success,
    size_t *passed,
    size_t *total
)
{
    printf("D5_ATTITUDE_TEST %s: %s\n", name, success ? "PASS" : "FAIL");
    (*total)++;
    if (success) {
        (*passed)++;
    }
}

static inline void run_phase4_d5_attitude_provider_selftest(void)
{
    size_t passed = 0u;
    size_t total = 0u;

    vg_d5_record("LABEL_ATTITUDE_MOTION",
                 strcmp(vg_attitude_channel_label(),
                        "attitude/motion prototype") == 0,
                 &passed, &total);
    vg_d5_record("DISCLAIMER_NOT_STABILITY_CERTIFICATION",
                 strcmp(vg_attitude_scope_note(),
                        "not vessel stability certification") == 0,
                 &passed, &total);

    vg_attitude_sample_t sample = {
        .meta = {
            .source_mode = VG_SOURCE_SIMULATION,
            .quality = VG_QUALITY_VALID,
            .sampled_at_ms = 100u,
            .sequence = 1u
        },
        .has_value = true,
        .roll_deg = 0.0f,
        .pitch_deg = 0.0f
    };

    vg_d5_record("VALID_ZERO_CURRENT",
                 vg_attitude_sample_is_consistent(&sample) &&
                 vg_attitude_sample_is_current(&sample), &passed, &total);

    sample.roll_deg = 12.5f;
    sample.pitch_deg = -4.0f;
    vg_d5_record("VALID_SIGNED_CURRENT",
                 vg_attitude_sample_is_consistent(&sample) &&
                 vg_attitude_sample_is_current(&sample), &passed, &total);

    sample.roll_deg = NAN;
    vg_d5_record("VALID_ROLL_NAN_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.roll_deg = 1.0f;
    sample.pitch_deg = NAN;
    vg_d5_record("VALID_PITCH_NAN_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.pitch_deg = 1.0f;
    sample.roll_deg = INFINITY;
    vg_d5_record("VALID_ROLL_INF_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.roll_deg = 1.0f;
    sample.pitch_deg = -INFINITY;
    vg_d5_record("VALID_PITCH_INF_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);

    sample.pitch_deg = 1.0f;
    sample.has_value = false;
    vg_d5_record("VALID_NO_VALUE_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_STALE;
    sample.has_value = true;
    sample.roll_deg = -8.0f;
    sample.pitch_deg = 6.0f;
    vg_d5_record("STALE_VALUE_ACCEPTED_NOT_CURRENT",
                 vg_attitude_sample_is_consistent(&sample) &&
                 !vg_attitude_sample_is_current(&sample), &passed, &total);
    sample.has_value = false;
    vg_d5_record("STALE_NO_VALUE_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    sample.roll_deg = NAN;
    vg_d5_record("STALE_NAN_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);

    sample.roll_deg = 0.0f;
    sample.pitch_deg = 0.0f;
    sample.meta.quality = VG_QUALITY_MISSING;
    sample.has_value = false;
    vg_d5_record("MISSING_NO_VALUE_ACCEPTED",
                 vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d5_record("MISSING_VALUE_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_INVALID;
    sample.has_value = false;
    vg_d5_record("INVALID_NO_VALUE_ACCEPTED",
                 vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d5_record("INVALID_VALUE_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_UNKNOWN;
    sample.has_value = false;
    vg_d5_record("UNKNOWN_NO_VALUE_ACCEPTED",
                 vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d5_record("UNKNOWN_VALUE_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);

    sample.has_value = false;
    sample.meta.source_mode = VG_SOURCE_PHYSICAL;
    vg_d5_record("PHYSICAL_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.meta.source_mode = (vg_source_mode_t)99;
    vg_d5_record("UNKNOWN_SOURCE_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);
    sample.meta.source_mode = VG_SOURCE_SIMULATION;
    sample.meta.sequence = 0u;
    vg_d5_record("ZERO_SEQUENCE_REJECTED",
                 !vg_attitude_sample_is_consistent(&sample), &passed, &total);
    vg_d5_record("NULL_SAMPLE_REJECTED",
                 !vg_attitude_sample_is_consistent(NULL) &&
                 !vg_attitude_sample_is_current(NULL), &passed, &total);

    vg_attitude_sample_t bench = {0};
    vg_d5_record("BENCH_VALID_ZERO",
                 vg_attitude_bench_build_sample(&bench, VG_QUALITY_VALID,
                                                true, 0.0f, 0.0f,
                                                1000u, 1u) &&
                 vg_attitude_sample_is_current(&bench), &passed, &total);
    vg_d5_record("BENCH_VALID_SIGNED",
                 vg_attitude_bench_build_sample(&bench, VG_QUALITY_VALID,
                                                true, 14.0f, -3.0f,
                                                1010u, 2u), &passed, &total);
    vg_d5_record("BENCH_STALE_VALUE",
                 vg_attitude_bench_build_sample(&bench, VG_QUALITY_STALE,
                                                true, 14.0f, -3.0f,
                                                1020u, 3u) &&
                 !vg_attitude_sample_is_current(&bench), &passed, &total);
    vg_d5_record("BENCH_MISSING_NO_VALUE",
                 vg_attitude_bench_build_sample(&bench, VG_QUALITY_MISSING,
                                                false, 0.0f, 0.0f,
                                                1030u, 4u), &passed, &total);
    vg_d5_record("BENCH_INVALID_NO_VALUE",
                 vg_attitude_bench_build_sample(&bench, VG_QUALITY_INVALID,
                                                false, 0.0f, 0.0f,
                                                1040u, 5u), &passed, &total);
    vg_d5_record("BENCH_UNKNOWN_NO_VALUE",
                 vg_attitude_bench_build_sample(&bench, VG_QUALITY_UNKNOWN,
                                                false, 0.0f, 0.0f,
                                                1050u, 6u), &passed, &total);
    vg_d5_record("BENCH_VALID_NO_VALUE_REJECTED",
                 !vg_attitude_bench_build_sample(&bench, VG_QUALITY_VALID,
                                                 false, 1.0f, 1.0f,
                                                 1060u, 7u), &passed, &total);
    vg_d5_record("BENCH_MISSING_VALUE_REJECTED",
                 !vg_attitude_bench_build_sample(&bench, VG_QUALITY_MISSING,
                                                 true, 1.0f, 1.0f,
                                                 1070u, 8u), &passed, &total);
    vg_d5_record("BENCH_ROLL_NAN_REJECTED",
                 !vg_attitude_bench_build_sample(&bench, VG_QUALITY_VALID,
                                                 true, NAN, 1.0f,
                                                 1080u, 9u), &passed, &total);
    vg_d5_record("BENCH_PITCH_NAN_REJECTED",
                 !vg_attitude_bench_build_sample(&bench, VG_QUALITY_VALID,
                                                 true, 1.0f, NAN,
                                                 1090u, 10u), &passed, &total);
    vg_d5_record("BENCH_ZERO_SEQUENCE_REJECTED",
                 !vg_attitude_bench_build_sample(&bench, VG_QUALITY_VALID,
                                                 true, 1.0f, 1.0f,
                                                 1100u, 0u), &passed, &total);
    vg_d5_record("BENCH_NULL_REJECTED",
                 !vg_attitude_bench_build_sample(NULL, VG_QUALITY_VALID,
                                                 true, 1.0f, 1.0f,
                                                 1110u, 11u), &passed, &total);

    vg_attitude_sim_t sim = {0};
    vg_d5_record("SIM_INIT",
                 vg_attitude_sim_init(&sim, 2000u, 100u), &passed, &total);
    vg_d5_record("SIM_ZERO_INTERVAL_REJECTED",
                 !vg_attitude_sim_init(&sim, 2000u, 0u), &passed, &total);
    vg_d5_record("SIM_NULL_INIT_REJECTED",
                 !vg_attitude_sim_init(NULL, 2000u, 100u), &passed, &total);

    (void)vg_attitude_sim_init(&sim, 2000u, 100u);
    bool deterministic = true;
    const vg_data_quality_t expected_quality[VG_ATTITUDE_SIM_STEPS] = {
        VG_QUALITY_VALID, VG_QUALITY_VALID, VG_QUALITY_VALID,
        VG_QUALITY_STALE, VG_QUALITY_MISSING, VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN, VG_QUALITY_VALID
    };
    const bool expected_has[VG_ATTITUDE_SIM_STEPS] = {
        true, true, true, true, false, false, false, true
    };
    for (size_t i = 0u; i < VG_ATTITUDE_SIM_STEPS; ++i) {
        vg_attitude_sample_t item = {0};
        if (vg_attitude_sim_next(&sim, &item) != VG_ATTITUDE_SIM_SAMPLE ||
            item.meta.source_mode != VG_SOURCE_SIMULATION ||
            item.meta.quality != expected_quality[i] ||
            item.meta.sequence != (uint32_t)(i + 1u) ||
            item.has_value != expected_has[i] ||
            item.meta.sampled_at_ms != 2000u + (uint64_t)i * 100u) {
            deterministic = false;
            break;
        }
    }
    vg_d5_record("SIM_DETERMINISTIC_SEQUENCE", deterministic, &passed, &total);
    vg_attitude_sample_t complete_out = {0};
    vg_d5_record("SIM_COMPLETE",
                 vg_attitude_sim_next(&sim, &complete_out) ==
                 VG_ATTITUDE_SIM_COMPLETE, &passed, &total);

    vg_attitude_sim_t uninitialized = {0};
    vg_d5_record("SIM_UNINITIALIZED_REJECTED",
                 vg_attitude_sim_next(&uninitialized, &complete_out) ==
                 VG_ATTITUDE_SIM_REJECTED, &passed, &total);
    vg_d5_record("SIM_NULL_REJECTED",
                 vg_attitude_sim_next(NULL, &complete_out) ==
                 VG_ATTITUDE_SIM_REJECTED, &passed, &total);
    vg_d5_record("SIM_NULL_OUTPUT_REJECTED",
                 vg_attitude_sim_next(&sim, NULL) == VG_ATTITUDE_SIM_REJECTED,
                 &passed, &total);

    vg_attitude_sim_t overflow = {0};
    (void)vg_attitude_sim_init(&overflow, UINT64_MAX - 50u, 100u);
    uint64_t timestamp = 0u;
    vg_d5_record("SIM_TIMESTAMP_OVERFLOW_REJECTED",
                 !vg_attitude_sim_timestamp(&overflow, 1u, &timestamp),
                 &passed, &total);
    (void)vg_attitude_sim_init(&sim, 3000u, 100u);
    vg_d5_record("SIM_TIMESTAMP_STEP0",
                 vg_attitude_sim_timestamp(&sim, 0u, &timestamp) &&
                 timestamp == 3000u, &passed, &total);
    vg_d5_record("SIM_TIMESTAMP_OUT_OF_RANGE",
                 !vg_attitude_sim_timestamp(&sim, VG_ATTITUDE_SIM_STEPS,
                                            &timestamp), &passed, &total);
    vg_d5_record("SIM_SAMPLE_OUT_OF_RANGE",
                 !vg_attitude_sim_sample_for_step(&sim, VG_ATTITUDE_SIM_STEPS,
                                                  &complete_out),
                 &passed, &total);
    vg_d5_record("SIM_SAMPLE_NULL_REJECTED",
                 !vg_attitude_sim_sample_for_step(&sim, 0u, NULL),
                 &passed, &total);

    vg_attitude_sample_t check = {0};
    vg_d5_record("SIM_SIGNED_VALUES_PRESENT",
                 vg_attitude_sim_sample_for_step(&sim, 1u, &check) &&
                 check.roll_deg == 12.5f && check.pitch_deg == -4.0f,
                 &passed, &total);
    vg_d5_record("SIM_STALE_PRESENT",
                 vg_attitude_sim_sample_for_step(&sim, 3u, &check) &&
                 check.meta.quality == VG_QUALITY_STALE &&
                 !vg_attitude_sample_is_current(&check), &passed, &total);
    vg_d5_record("SIM_MISSING_PRESENT",
                 vg_attitude_sim_sample_for_step(&sim, 4u, &check) &&
                 check.meta.quality == VG_QUALITY_MISSING && !check.has_value,
                 &passed, &total);
    vg_d5_record("SIM_INVALID_PRESENT",
                 vg_attitude_sim_sample_for_step(&sim, 5u, &check) &&
                 check.meta.quality == VG_QUALITY_INVALID && !check.has_value,
                 &passed, &total);
    vg_d5_record("SIM_UNKNOWN_PRESENT",
                 vg_attitude_sim_sample_for_step(&sim, 6u, &check) &&
                 check.meta.quality == VG_QUALITY_UNKNOWN && !check.has_value,
                 &passed, &total);
    vg_d5_record("SIM_RECOVERY_VALID",
                 vg_attitude_sim_sample_for_step(&sim, 7u, &check) &&
                 check.meta.quality == VG_QUALITY_VALID &&
                 check.roll_deg == 1.0f && check.pitch_deg == -1.0f &&
                 vg_attitude_sample_is_current(&check), &passed, &total);

    vg_d5_record("CASE_COUNT_EXACT",
                 total + 1u == VG_D5_EXPECTED_CASES, &passed, &total);

    printf("PHASE4_D5_ATTITUDE_PROVIDER_SELFTEST: %s (%zu/%zu)\n",
           passed == total && total == VG_D5_EXPECTED_CASES ? "PASS" : "FAIL",
           passed, total);
}

#endif /* VG_PHASE4_D5_SELFTEST_H */
