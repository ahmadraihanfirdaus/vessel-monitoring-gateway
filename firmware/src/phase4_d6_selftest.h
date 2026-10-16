#ifndef VG_PHASE4_D6_SELFTEST_H
#define VG_PHASE4_D6_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "provider_vibration.h"

/* Development-only IF-06 / MOT-002 provider self-test. */
#define VG_D6_EXPECTED_CASES 61u

static inline void vg_d6_record(
    const char *name,
    bool success,
    size_t *passed,
    size_t *total
)
{
    printf("D6_VIBRATION_TEST %s: %s\n", name, success ? "PASS" : "FAIL");
    (*total)++;
    if (success) {
        (*passed)++;
    }
}

static inline void run_phase4_d6_vibration_provider_selftest(void)
{
    size_t passed = 0u;
    size_t total = 0u;

    vg_d6_record("LABEL_VIBRATION_ACCELERATION",
                 strcmp(vg_vibration_channel_label(),
                        "vibration/acceleration prototype") == 0,
                 &passed, &total);
    vg_d6_record("DISCLAIMER_NOT_MACHINERY_CERTIFICATION",
                 strcmp(vg_vibration_scope_note(),
                        "not machinery condition certification") == 0,
                 &passed, &total);

    vg_vibration_sample_t sample = {
        .meta = {
            .source_mode = VG_SOURCE_SIMULATION,
            .quality = VG_QUALITY_VALID,
            .sampled_at_ms = 100u,
            .sequence = 1u
        },
        .has_value = true,
        .accel_x_g = 0.0f,
        .accel_y_g = 0.0f,
        .accel_z_g = 1.0f,
        .vibration_index = 0.0f
    };

    vg_d6_record("VALID_ZERO_INDEX_CURRENT",
                 vg_vibration_sample_is_consistent(&sample) &&
                 vg_vibration_sample_is_current(&sample), &passed, &total);
    sample.accel_x_g = 0.12f;
    sample.accel_y_g = -0.08f;
    sample.accel_z_g = 1.03f;
    sample.vibration_index = 0.35f;
    vg_d6_record("VALID_SIGNED_AXES_CURRENT",
                 vg_vibration_sample_is_consistent(&sample) &&
                 vg_vibration_sample_is_current(&sample), &passed, &total);

    sample.accel_x_g = NAN;
    vg_d6_record("VALID_X_NAN_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.accel_x_g = 0.1f;
    sample.accel_y_g = NAN;
    vg_d6_record("VALID_Y_NAN_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.accel_y_g = 0.1f;
    sample.accel_z_g = NAN;
    vg_d6_record("VALID_Z_NAN_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.accel_z_g = 1.0f;
    sample.vibration_index = NAN;
    vg_d6_record("VALID_INDEX_NAN_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.vibration_index = 0.2f;
    sample.accel_x_g = INFINITY;
    vg_d6_record("VALID_X_INF_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.accel_x_g = 0.1f;
    sample.accel_y_g = -INFINITY;
    vg_d6_record("VALID_Y_INF_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.accel_y_g = 0.1f;
    sample.accel_z_g = INFINITY;
    vg_d6_record("VALID_Z_INF_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.accel_z_g = 1.0f;
    sample.vibration_index = INFINITY;
    vg_d6_record("VALID_INDEX_INF_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.vibration_index = -0.01f;
    vg_d6_record("VALID_NEGATIVE_INDEX_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.vibration_index = 0.2f;
    sample.has_value = false;
    vg_d6_record("VALID_NO_VALUE_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_STALE;
    sample.has_value = true;
    sample.accel_x_g = -0.25f;
    sample.accel_y_g = 0.20f;
    sample.accel_z_g = 0.92f;
    sample.vibration_index = 0.80f;
    vg_d6_record("STALE_VALUE_ACCEPTED_NOT_CURRENT",
                 vg_vibration_sample_is_consistent(&sample) &&
                 !vg_vibration_sample_is_current(&sample), &passed, &total);
    sample.vibration_index = -1.0f;
    vg_d6_record("STALE_NEGATIVE_INDEX_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.vibration_index = 0.8f;
    sample.has_value = false;
    vg_d6_record("STALE_NO_VALUE_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);

    sample.accel_x_g = 0.0f;
    sample.accel_y_g = 0.0f;
    sample.accel_z_g = 0.0f;
    sample.vibration_index = 0.0f;
    sample.meta.quality = VG_QUALITY_MISSING;
    sample.has_value = false;
    vg_d6_record("MISSING_NO_VALUE_ACCEPTED",
                 vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d6_record("MISSING_VALUE_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_INVALID;
    sample.has_value = false;
    vg_d6_record("INVALID_NO_VALUE_ACCEPTED",
                 vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d6_record("INVALID_VALUE_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_UNKNOWN;
    sample.has_value = false;
    vg_d6_record("UNKNOWN_NO_VALUE_ACCEPTED",
                 vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d6_record("UNKNOWN_VALUE_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);

    sample.has_value = false;
    sample.meta.quality = VG_QUALITY_UNKNOWN;
    sample.meta.source_mode = VG_SOURCE_PHYSICAL;
    vg_d6_record("PHYSICAL_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.meta.source_mode = (vg_source_mode_t)99;
    vg_d6_record("UNKNOWN_SOURCE_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.meta.source_mode = VG_SOURCE_SIMULATION;
    sample.meta.sequence = 0u;
    vg_d6_record("ZERO_SEQUENCE_REJECTED",
                 !vg_vibration_sample_is_consistent(&sample), &passed, &total);
    sample.meta.sequence = 1u;
    vg_d6_record("NULL_SAMPLE_REJECTED",
                 !vg_vibration_sample_is_consistent(NULL), &passed, &total);

    vg_vibration_sample_t bench = {0};
    vg_d6_record("BENCH_VALID_ZERO_INDEX",
                 vg_vibration_bench_build_sample(&bench, VG_QUALITY_VALID,
                     true, 0.0f, 0.0f, 1.0f, 0.0f, 500u, 1u) &&
                 vg_vibration_sample_is_current(&bench), &passed, &total);
    vg_d6_record("BENCH_VALID_SIGNED",
                 vg_vibration_bench_build_sample(&bench, VG_QUALITY_VALID,
                     true, 0.2f, -0.1f, 0.95f, 0.4f, 600u, 2u) &&
                 bench.accel_y_g == -0.1f && bench.vibration_index == 0.4f,
                 &passed, &total);
    vg_d6_record("BENCH_STALE_VALUE",
                 vg_vibration_bench_build_sample(&bench, VG_QUALITY_STALE,
                     true, -0.2f, 0.1f, 1.05f, 0.5f, 700u, 3u) &&
                 !vg_vibration_sample_is_current(&bench), &passed, &total);
    vg_d6_record("BENCH_MISSING_NO_VALUE",
                 vg_vibration_bench_build_sample(&bench, VG_QUALITY_MISSING,
                     false, 0.0f, 0.0f, 0.0f, 0.0f, 800u, 4u),
                 &passed, &total);
    vg_d6_record("BENCH_INVALID_NO_VALUE",
                 vg_vibration_bench_build_sample(&bench, VG_QUALITY_INVALID,
                     false, 0.0f, 0.0f, 0.0f, 0.0f, 900u, 5u),
                 &passed, &total);
    vg_d6_record("BENCH_UNKNOWN_NO_VALUE",
                 vg_vibration_bench_build_sample(&bench, VG_QUALITY_UNKNOWN,
                     false, 0.0f, 0.0f, 0.0f, 0.0f, 1000u, 6u),
                 &passed, &total);
    vg_d6_record("BENCH_VALID_NO_VALUE_REJECTED",
                 !vg_vibration_bench_build_sample(&bench, VG_QUALITY_VALID,
                     false, 0.0f, 0.0f, 1.0f, 0.1f, 1100u, 7u),
                 &passed, &total);
    vg_d6_record("BENCH_MISSING_VALUE_REJECTED",
                 !vg_vibration_bench_build_sample(&bench, VG_QUALITY_MISSING,
                     true, 0.0f, 0.0f, 1.0f, 0.1f, 1200u, 8u),
                 &passed, &total);
    vg_d6_record("BENCH_X_NAN_REJECTED",
                 !vg_vibration_bench_build_sample(&bench, VG_QUALITY_VALID,
                     true, NAN, 0.0f, 1.0f, 0.1f, 1300u, 9u),
                 &passed, &total);
    vg_d6_record("BENCH_INDEX_NAN_REJECTED",
                 !vg_vibration_bench_build_sample(&bench, VG_QUALITY_VALID,
                     true, 0.0f, 0.0f, 1.0f, NAN, 1400u, 10u),
                 &passed, &total);
    vg_d6_record("BENCH_NEGATIVE_INDEX_REJECTED",
                 !vg_vibration_bench_build_sample(&bench, VG_QUALITY_VALID,
                     true, 0.0f, 0.0f, 1.0f, -0.1f, 1500u, 11u),
                 &passed, &total);
    vg_d6_record("BENCH_ZERO_SEQUENCE_REJECTED",
                 !vg_vibration_bench_build_sample(&bench, VG_QUALITY_VALID,
                     true, 0.0f, 0.0f, 1.0f, 0.1f, 1600u, 0u),
                 &passed, &total);
    vg_d6_record("BENCH_NULL_REJECTED",
                 !vg_vibration_bench_build_sample(NULL, VG_QUALITY_VALID,
                     true, 0.0f, 0.0f, 1.0f, 0.1f, 1700u, 12u),
                 &passed, &total);

    vg_vibration_sim_t sim = {0};
    vg_d6_record("SIM_INIT", vg_vibration_sim_init(&sim, 3000u, 100u),
                 &passed, &total);
    vg_d6_record("SIM_ZERO_INTERVAL_REJECTED",
                 !vg_vibration_sim_init(&sim, 3000u, 0u), &passed, &total);
    vg_d6_record("SIM_NULL_INIT_REJECTED",
                 !vg_vibration_sim_init(NULL, 3000u, 100u), &passed, &total);
    (void)vg_vibration_sim_init(&sim, 3000u, 100u);

    bool deterministic = true;
    static const vg_data_quality_t expected_quality[VG_VIBRATION_SIM_STEPS] = {
        VG_QUALITY_VALID, VG_QUALITY_VALID, VG_QUALITY_VALID, VG_QUALITY_STALE,
        VG_QUALITY_MISSING, VG_QUALITY_INVALID, VG_QUALITY_UNKNOWN,
        VG_QUALITY_VALID
    };
    for (size_t i = 0u; i < VG_VIBRATION_SIM_STEPS; ++i) {
        vg_vibration_sample_t out = {0};
        if (vg_vibration_sim_next(&sim, &out) != VG_VIBRATION_SIM_SAMPLE ||
            out.meta.quality != expected_quality[i] ||
            out.meta.sequence != (uint32_t)(i + 1u) ||
            out.meta.sampled_at_ms != 3000u + 100u * (uint64_t)i) {
            deterministic = false;
        }
    }
    vg_d6_record("SIM_DETERMINISTIC_SEQUENCE", deterministic, &passed, &total);
    vg_vibration_sample_t complete_out = {0};
    vg_d6_record("SIM_COMPLETE",
                 vg_vibration_sim_next(&sim, &complete_out) ==
                 VG_VIBRATION_SIM_COMPLETE, &passed, &total);
    vg_vibration_sim_t blank = {0};
    vg_d6_record("SIM_UNINITIALIZED_REJECTED",
                 vg_vibration_sim_next(&blank, &complete_out) ==
                 VG_VIBRATION_SIM_REJECTED, &passed, &total);
    vg_d6_record("SIM_NULL_REJECTED",
                 vg_vibration_sim_next(NULL, &complete_out) ==
                 VG_VIBRATION_SIM_REJECTED, &passed, &total);
    vg_d6_record("SIM_NULL_OUTPUT_REJECTED",
                 vg_vibration_sim_next(&sim, NULL) == VG_VIBRATION_SIM_REJECTED,
                 &passed, &total);

    vg_vibration_sim_t overflow = {0};
    (void)vg_vibration_sim_init(&overflow, UINT64_MAX - 50u, 100u);
    uint64_t timestamp = 0u;
    vg_d6_record("SIM_TIMESTAMP_OVERFLOW_REJECTED",
                 !vg_vibration_sim_timestamp(&overflow, 1u, &timestamp),
                 &passed, &total);
    (void)vg_vibration_sim_init(&sim, 3000u, 100u);
    vg_d6_record("SIM_TIMESTAMP_STEP0",
                 vg_vibration_sim_timestamp(&sim, 0u, &timestamp) &&
                 timestamp == 3000u, &passed, &total);
    vg_d6_record("SIM_TIMESTAMP_OUT_OF_RANGE",
                 !vg_vibration_sim_timestamp(&sim, VG_VIBRATION_SIM_STEPS,
                                             &timestamp), &passed, &total);
    vg_d6_record("SIM_SAMPLE_OUT_OF_RANGE",
                 !vg_vibration_sim_sample_for_step(&sim, VG_VIBRATION_SIM_STEPS,
                                                   &complete_out),
                 &passed, &total);
    vg_d6_record("SIM_SAMPLE_NULL_REJECTED",
                 !vg_vibration_sim_sample_for_step(&sim, 0u, NULL),
                 &passed, &total);

    vg_vibration_sample_t check = {0};
    vg_d6_record("SIM_SIGNED_AXES_PRESENT",
                 vg_vibration_sim_sample_for_step(&sim, 1u, &check) &&
                 check.accel_x_g == 0.12f && check.accel_y_g == -0.08f,
                 &passed, &total);
    vg_d6_record("SIM_INDEX_VARIATION_PRESENT",
                 vg_vibration_sim_sample_for_step(&sim, 2u, &check) &&
                 check.vibration_index == 0.80f,
                 &passed, &total);
    vg_d6_record("SIM_STALE_PRESENT",
                 vg_vibration_sim_sample_for_step(&sim, 3u, &check) &&
                 check.meta.quality == VG_QUALITY_STALE &&
                 !vg_vibration_sample_is_current(&check), &passed, &total);
    vg_d6_record("SIM_MISSING_PRESENT",
                 vg_vibration_sim_sample_for_step(&sim, 4u, &check) &&
                 check.meta.quality == VG_QUALITY_MISSING && !check.has_value,
                 &passed, &total);
    vg_d6_record("SIM_INVALID_PRESENT",
                 vg_vibration_sim_sample_for_step(&sim, 5u, &check) &&
                 check.meta.quality == VG_QUALITY_INVALID && !check.has_value,
                 &passed, &total);
    vg_d6_record("SIM_UNKNOWN_PRESENT",
                 vg_vibration_sim_sample_for_step(&sim, 6u, &check) &&
                 check.meta.quality == VG_QUALITY_UNKNOWN && !check.has_value,
                 &passed, &total);
    vg_d6_record("SIM_RECOVERY_VALID",
                 vg_vibration_sim_sample_for_step(&sim, 7u, &check) &&
                 check.meta.quality == VG_QUALITY_VALID &&
                 check.accel_x_g == 0.01f && check.accel_z_g == 1.00f &&
                 check.vibration_index == 0.05f &&
                 vg_vibration_sample_is_current(&check), &passed, &total);

    vg_d6_record("CASE_COUNT_EXACT",
                 total + 1u == VG_D6_EXPECTED_CASES, &passed, &total);

    printf("PHASE4_D6_VIBRATION_PROVIDER_SELFTEST: %s (%zu/%zu)\n",
           passed == total && total == VG_D6_EXPECTED_CASES ? "PASS" : "FAIL",
           passed, total);
}

#endif /* VG_PHASE4_D6_SELFTEST_H */
