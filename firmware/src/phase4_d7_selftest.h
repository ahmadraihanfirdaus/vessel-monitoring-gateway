#ifndef VG_PHASE4_D7_SELFTEST_H
#define VG_PHASE4_D7_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "provider_power.h"

/* Development-only IF-07 provider self-test. */
#define VG_D7_EXPECTED_CASES 61u

static inline void vg_d7_record(
    const char *name,
    bool success,
    size_t *passed,
    size_t *total
)
{
    printf("D7_POWER_TEST %s: %s\n", name, success ? "PASS" : "FAIL");
    (*total)++;
    if (success) {
        (*passed)++;
    }
}

static inline void run_phase4_d7_power_provider_selftest(void)
{
    size_t passed = 0u;
    size_t total = 0u;

    vg_d7_record("LABEL_LOW_POWER_BENCH",
                 strcmp(vg_power_channel_label(), "low-power electrical bench prototype") == 0,
                 &passed, &total);
    vg_d7_record("SCOPE_SAFE_LOW_POWER_ONLY",
                 strcmp(vg_power_scope_note(), "safe low-power bench reference only") == 0,
                 &passed, &total);
    vg_d7_record("DISCLAIMER_NOT_ELECTRICAL_CERTIFICATION",
                 strcmp(vg_power_hazard_note(), "not vessel electrical safety certification") == 0,
                 &passed, &total);

    vg_power_sample_t sample = {
        .meta = {
            .source_mode = VG_SOURCE_SIMULATION,
            .quality = VG_QUALITY_VALID,
            .sampled_at_ms = 100u,
            .sequence = 1u
        },
        .has_value = true,
        .voltage_v = 5.0f,
        .current_a = 0.1f,
        .power_w = 0.5f
    };

    vg_d7_record("VALID_POSITIVE_CURRENT",
                 vg_power_sample_is_consistent(&sample) && vg_power_sample_is_current(&sample),
                 &passed, &total);
    sample.current_a = -0.05f;
    sample.power_w = -0.25f;
    vg_d7_record("VALID_SIGNED_CURRENT_POWER",
                 vg_power_sample_is_consistent(&sample) && vg_power_sample_is_current(&sample),
                 &passed, &total);
    sample.voltage_v = 0.0f;
    sample.current_a = 0.0f;
    sample.power_w = 0.0f;
    vg_d7_record("VALID_ZERO_VALUES",
                 vg_power_sample_is_consistent(&sample) && vg_power_sample_is_current(&sample),
                 &passed, &total);
    sample.voltage_v = -0.01f;
    vg_d7_record("VALID_NEGATIVE_VOLTAGE_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.voltage_v = NAN;
    vg_d7_record("VALID_VOLTAGE_NAN_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.voltage_v = INFINITY;
    vg_d7_record("VALID_VOLTAGE_INF_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.voltage_v = 5.0f;
    sample.current_a = NAN;
    vg_d7_record("VALID_CURRENT_NAN_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.current_a = -INFINITY;
    vg_d7_record("VALID_CURRENT_INF_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.current_a = 0.1f;
    sample.power_w = NAN;
    vg_d7_record("VALID_POWER_NAN_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.power_w = INFINITY;
    vg_d7_record("VALID_POWER_INF_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.power_w = 0.5f;
    sample.has_value = false;
    vg_d7_record("VALID_NO_VALUE_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);

    sample.has_value = true;
    sample.meta.quality = VG_QUALITY_STALE;
    vg_d7_record("STALE_VALUES_ACCEPTED_NOT_CURRENT",
                 vg_power_sample_is_consistent(&sample) && !vg_power_sample_is_current(&sample),
                 &passed, &total);
    sample.has_value = false;
    vg_d7_record("STALE_NO_VALUE_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_MISSING;
    sample.has_value = false;
    vg_d7_record("MISSING_NO_VALUE_ACCEPTED",
                 vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d7_record("MISSING_VALUE_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_INVALID;
    sample.has_value = false;
    vg_d7_record("INVALID_NO_VALUE_ACCEPTED",
                 vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d7_record("INVALID_VALUE_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_UNKNOWN;
    sample.has_value = false;
    vg_d7_record("UNKNOWN_NO_VALUE_ACCEPTED",
                 vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.has_value = true;
    vg_d7_record("UNKNOWN_VALUE_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);

    sample.meta.quality = VG_QUALITY_VALID;
    sample.has_value = true;
    sample.meta.source_mode = VG_SOURCE_PHYSICAL;
    vg_d7_record("PHYSICAL_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.meta.source_mode = (vg_source_mode_t)99;
    vg_d7_record("UNKNOWN_SOURCE_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    sample.meta.source_mode = VG_SOURCE_SIMULATION;
    sample.meta.sequence = 0u;
    vg_d7_record("ZERO_SEQUENCE_REJECTED",
                 !vg_power_sample_is_consistent(&sample), &passed, &total);
    vg_d7_record("NULL_SAMPLE_REJECTED",
                 !vg_power_sample_is_consistent(NULL), &passed, &total);

    vg_power_sample_t bench = {0};
    vg_d7_record("BENCH_VALID_POSITIVE",
                 vg_power_bench_build_sample(&bench, VG_QUALITY_VALID, true,
                    5.0f, 0.10f, 0.50f, 200u, 1u) &&
                 vg_power_sample_is_current(&bench), &passed, &total);
    vg_d7_record("BENCH_VALID_SIGNED_CURRENT_POWER",
                 vg_power_bench_build_sample(&bench, VG_QUALITY_VALID, true,
                    12.0f, -0.05f, -0.60f, 210u, 2u), &passed, &total);
    vg_d7_record("BENCH_STALE_VALUES",
                 vg_power_bench_build_sample(&bench, VG_QUALITY_STALE, true,
                    12.0f, 0.25f, 3.0f, 220u, 3u) &&
                 !vg_power_sample_is_current(&bench), &passed, &total);
    vg_d7_record("BENCH_MISSING_NO_VALUE",
                 vg_power_bench_build_sample(&bench, VG_QUALITY_MISSING, false,
                    0.0f, 0.0f, 0.0f, 230u, 4u), &passed, &total);
    vg_d7_record("BENCH_INVALID_NO_VALUE",
                 vg_power_bench_build_sample(&bench, VG_QUALITY_INVALID, false,
                    0.0f, 0.0f, 0.0f, 240u, 5u), &passed, &total);
    vg_d7_record("BENCH_UNKNOWN_NO_VALUE",
                 vg_power_bench_build_sample(&bench, VG_QUALITY_UNKNOWN, false,
                    0.0f, 0.0f, 0.0f, 250u, 6u), &passed, &total);
    vg_d7_record("BENCH_VALID_NO_VALUE_REJECTED",
                 !vg_power_bench_build_sample(&bench, VG_QUALITY_VALID, false,
                    5.0f, 0.1f, 0.5f, 260u, 7u), &passed, &total);
    vg_d7_record("BENCH_MISSING_VALUE_REJECTED",
                 !vg_power_bench_build_sample(&bench, VG_QUALITY_MISSING, true,
                    5.0f, 0.1f, 0.5f, 270u, 8u), &passed, &total);
    vg_d7_record("BENCH_NEGATIVE_VOLTAGE_REJECTED",
                 !vg_power_bench_build_sample(&bench, VG_QUALITY_VALID, true,
                    -1.0f, 0.1f, -0.1f, 280u, 9u), &passed, &total);
    vg_d7_record("BENCH_VOLTAGE_NAN_REJECTED",
                 !vg_power_bench_build_sample(&bench, VG_QUALITY_VALID, true,
                    NAN, 0.1f, 0.5f, 290u, 10u), &passed, &total);
    vg_d7_record("BENCH_CURRENT_NAN_REJECTED",
                 !vg_power_bench_build_sample(&bench, VG_QUALITY_VALID, true,
                    5.0f, NAN, 0.5f, 300u, 11u), &passed, &total);
    vg_d7_record("BENCH_POWER_NAN_REJECTED",
                 !vg_power_bench_build_sample(&bench, VG_QUALITY_VALID, true,
                    5.0f, 0.1f, NAN, 310u, 12u), &passed, &total);
    vg_d7_record("BENCH_ZERO_SEQUENCE_REJECTED",
                 !vg_power_bench_build_sample(&bench, VG_QUALITY_VALID, true,
                    5.0f, 0.1f, 0.5f, 320u, 0u), &passed, &total);
    vg_d7_record("BENCH_NULL_REJECTED",
                 !vg_power_bench_build_sample(NULL, VG_QUALITY_VALID, true,
                    5.0f, 0.1f, 0.5f, 330u, 13u), &passed, &total);

    vg_power_sim_t sim = {0};
    vg_d7_record("SIM_INIT",
                 vg_power_sim_init(&sim, 1000u, 100u), &passed, &total);
    vg_power_sim_t bad_sim = {0};
    vg_d7_record("SIM_ZERO_INTERVAL_REJECTED",
                 !vg_power_sim_init(&bad_sim, 1000u, 0u), &passed, &total);
    vg_d7_record("SIM_NULL_INIT_REJECTED",
                 !vg_power_sim_init(NULL, 1000u, 100u), &passed, &total);

    static const vg_data_quality_t expected_quality[VG_POWER_SIM_STEPS] = {
        VG_QUALITY_VALID, VG_QUALITY_VALID, VG_QUALITY_VALID, VG_QUALITY_STALE,
        VG_QUALITY_MISSING, VG_QUALITY_INVALID, VG_QUALITY_UNKNOWN, VG_QUALITY_VALID
    };
    bool sequence_ok = true;
    bool signed_seen = false;
    bool stale_seen = false;
    bool missing_seen = false;
    bool invalid_seen = false;
    bool unknown_seen = false;
    bool recovery_ok = false;
    for (size_t i = 0u; i < VG_POWER_SIM_STEPS; ++i) {
        vg_power_sample_t step = {0};
        vg_power_sim_result_t result = vg_power_sim_next(&sim, &step);
        if (result != VG_POWER_SIM_SAMPLE || step.meta.quality != expected_quality[i] ||
            step.meta.sequence != (uint32_t)(i + 1u) ||
            step.meta.sampled_at_ms != 1000u + (uint64_t)(i * 100u) ||
            !vg_power_sample_is_consistent(&step)) {
            sequence_ok = false;
        }
        if (i == 2u && step.has_value && step.current_a < 0.0f && step.power_w < 0.0f) {
            signed_seen = true;
        }
        stale_seen |= step.meta.quality == VG_QUALITY_STALE;
        missing_seen |= step.meta.quality == VG_QUALITY_MISSING;
        invalid_seen |= step.meta.quality == VG_QUALITY_INVALID;
        unknown_seen |= step.meta.quality == VG_QUALITY_UNKNOWN;
        if (i == 7u && vg_power_sample_is_current(&step) && step.voltage_v == 5.0f) {
            recovery_ok = true;
        }
    }
    vg_d7_record("SIM_DETERMINISTIC_SEQUENCE", sequence_ok, &passed, &total);
    vg_power_sample_t done_sample = {0};
    vg_d7_record("SIM_COMPLETE",
                 vg_power_sim_next(&sim, &done_sample) == VG_POWER_SIM_COMPLETE,
                 &passed, &total);
    vg_power_sim_t uninitialized = {0};
    vg_d7_record("SIM_UNINITIALIZED_REJECTED",
                 vg_power_sim_next(&uninitialized, &done_sample) == VG_POWER_SIM_REJECTED,
                 &passed, &total);
    vg_d7_record("SIM_NULL_REJECTED",
                 vg_power_sim_next(NULL, &done_sample) == VG_POWER_SIM_REJECTED,
                 &passed, &total);
    vg_d7_record("SIM_NULL_OUTPUT_REJECTED",
                 vg_power_sim_next(&sim, NULL) == VG_POWER_SIM_REJECTED,
                 &passed, &total);

    vg_power_sim_t overflow = {0};
    (void)vg_power_sim_init(&overflow, UINT64_MAX - 10u, 10u);
    uint64_t timestamp = 0u;
    vg_d7_record("SIM_TIMESTAMP_STEP0",
                 vg_power_sim_timestamp(&overflow, 0u, &timestamp) &&
                 timestamp == UINT64_MAX - 10u, &passed, &total);
    vg_d7_record("SIM_TIMESTAMP_OVERFLOW_REJECTED",
                 !vg_power_sim_timestamp(&overflow, 2u, &timestamp), &passed, &total);
    vg_d7_record("SIM_TIMESTAMP_OUT_OF_RANGE",
                 !vg_power_sim_timestamp(&sim, VG_POWER_SIM_STEPS, &timestamp),
                 &passed, &total);
    vg_d7_record("SIM_TIMESTAMP_NULL_REJECTED",
                 !vg_power_sim_timestamp(&sim, 0u, NULL), &passed, &total);
    vg_d7_record("SIM_SAMPLE_OUT_OF_RANGE",
                 !vg_power_sim_sample_for_step(&sim, VG_POWER_SIM_STEPS, &done_sample),
                 &passed, &total);
    vg_d7_record("SIM_SAMPLE_NULL_REJECTED",
                 !vg_power_sim_sample_for_step(&sim, 0u, NULL), &passed, &total);
    vg_d7_record("SIM_SIGNED_CURRENT_POWER_PRESENT", signed_seen, &passed, &total);
    vg_d7_record("SIM_STALE_PRESENT", stale_seen, &passed, &total);
    vg_d7_record("SIM_MISSING_PRESENT", missing_seen, &passed, &total);
    vg_d7_record("SIM_INVALID_PRESENT", invalid_seen, &passed, &total);
    vg_d7_record("SIM_UNKNOWN_PRESENT", unknown_seen, &passed, &total);
    vg_d7_record("SIM_RECOVERY_VALID", recovery_ok, &passed, &total);

    vg_d7_record("CASE_COUNT_EXACT",
                 total + 1u == VG_D7_EXPECTED_CASES, &passed, &total);

    printf("PHASE4_D7_POWER_PROVIDER_SELFTEST: %s (%u/%u)\n",
           passed == total && total == VG_D7_EXPECTED_CASES ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)total);
}

#endif /* VG_PHASE4_D7_SELFTEST_H */
