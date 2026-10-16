#ifndef VG_PHASE4_D3_SELFTEST_H
#define VG_PHASE4_D3_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "provider_bilge.h"

/* Development-only IF-03 / SAF-005 provider self-test. */
#define VG_D3_EXPECTED_CASES 47u

static inline void vg_d3_record(
    const char *name,
    bool success,
    size_t *passed,
    size_t *total
)
{
    printf("D3_BILGE_TEST %s: %s\n", name, success ? "PASS" : "FAIL");
    (*total)++;
    if (success) {
        (*passed)++;
    }
}

static inline void run_phase4_d3_bilge_provider_selftest(void)
{
    size_t passed = 0u;
    size_t total = 0u;

    vg_d3_record("STATE_NORMAL_OPERATIONAL",
                 vg_bilge_state_is_operational(VG_BILGE_NORMAL),
                 &passed, &total);
    vg_d3_record("STATE_HIGH_OPERATIONAL",
                 vg_bilge_state_is_operational(VG_BILGE_HIGH),
                 &passed, &total);
    vg_d3_record("STATE_FAULT_NOT_OPERATIONAL",
                 !vg_bilge_state_is_operational(VG_BILGE_FAULT),
                 &passed, &total);
    vg_d3_record("STATE_UNKNOWN_NOT_OPERATIONAL",
                 !vg_bilge_state_is_operational(VG_BILGE_UNKNOWN),
                 &passed, &total);

    vg_bilge_sample_t sample = {
        .meta = {
            .source_mode = VG_SOURCE_SIMULATION,
            .quality = VG_QUALITY_VALID,
            .sampled_at_ms = 100u,
            .sequence = 1u
        },
        .state = VG_BILGE_NORMAL
    };

    vg_d3_record("VALID_NORMAL_CURRENT",
                 vg_bilge_sample_is_consistent(&sample) &&
                 vg_bilge_sample_is_current(&sample),
                 &passed, &total);

    sample.state = VG_BILGE_HIGH;
    vg_d3_record("VALID_HIGH_CURRENT",
                 vg_bilge_sample_is_consistent(&sample) &&
                 vg_bilge_sample_is_current(&sample),
                 &passed, &total);

    sample.state = VG_BILGE_FAULT;
    vg_d3_record("VALID_FAULT_REJECTED",
                 !vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    sample.state = VG_BILGE_UNKNOWN;
    vg_d3_record("VALID_UNKNOWN_REJECTED",
                 !vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_STALE;
    sample.state = VG_BILGE_HIGH;
    vg_d3_record("STALE_HIGH_NOT_CURRENT",
                 vg_bilge_sample_is_consistent(&sample) &&
                 !vg_bilge_sample_is_current(&sample),
                 &passed, &total);

    sample.state = VG_BILGE_FAULT;
    vg_d3_record("STALE_FAULT_REJECTED",
                 !vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_MISSING;
    sample.state = VG_BILGE_FAULT;
    vg_d3_record("MISSING_FAULT_ACCEPTED",
                 vg_bilge_sample_is_consistent(&sample) &&
                 !vg_bilge_sample_is_current(&sample),
                 &passed, &total);

    sample.state = VG_BILGE_NORMAL;
    vg_d3_record("MISSING_NORMAL_REJECTED",
                 !vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_INVALID;
    sample.state = VG_BILGE_FAULT;
    vg_d3_record("INVALID_FAULT_ACCEPTED",
                 vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    sample.state = VG_BILGE_HIGH;
    vg_d3_record("INVALID_HIGH_REJECTED",
                 !vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_UNKNOWN;
    sample.state = VG_BILGE_UNKNOWN;
    vg_d3_record("UNKNOWN_QUALITY_UNKNOWN_STATE_ACCEPTED",
                 vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    sample.state = VG_BILGE_FAULT;
    vg_d3_record("UNKNOWN_QUALITY_FAULT_REJECTED",
                 !vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.source_mode = VG_SOURCE_PHYSICAL;
    vg_d3_record("PHYSICAL_REJECTED",
                 !vg_bilge_sample_is_consistent(&sample),
                 &passed, &total);

    vg_d3_record("NULL_REJECTED",
                 !vg_bilge_sample_is_consistent(NULL) &&
                 !vg_bilge_sample_is_current(NULL),
                 &passed, &total);

    vg_bilge_sample_t bench = {0};

    vg_d3_record("BENCH_VALID_NORMAL",
                 vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_NORMAL, VG_QUALITY_VALID, 1000u, 1u) &&
                 bench.meta.source_mode == VG_SOURCE_BENCH_TEST &&
                 vg_bilge_sample_is_current(&bench),
                 &passed, &total);

    vg_d3_record("BENCH_VALID_HIGH",
                 vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_HIGH, VG_QUALITY_VALID, 1100u, 2u) &&
                 vg_bilge_sample_is_current(&bench),
                 &passed, &total);

    vg_d3_record("BENCH_STALE_HIGH",
                 vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_HIGH, VG_QUALITY_STALE, 1200u, 3u) &&
                 !vg_bilge_sample_is_current(&bench),
                 &passed, &total);

    vg_d3_record("BENCH_MISSING_FAULT",
                 vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_FAULT, VG_QUALITY_MISSING, 1300u, 4u),
                 &passed, &total);

    vg_d3_record("BENCH_INVALID_FAULT",
                 vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_FAULT, VG_QUALITY_INVALID, 1400u, 5u),
                 &passed, &total);

    vg_d3_record("BENCH_UNKNOWN",
                 vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_UNKNOWN, VG_QUALITY_UNKNOWN, 1500u, 6u),
                 &passed, &total);

    vg_d3_record("BENCH_MISSING_NORMAL_REJECTED",
                 !vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_NORMAL, VG_QUALITY_MISSING, 1600u, 7u),
                 &passed, &total);

    vg_d3_record("BENCH_VALID_FAULT_REJECTED",
                 !vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_FAULT, VG_QUALITY_VALID, 1700u, 8u),
                 &passed, &total);

    vg_d3_record("BENCH_ZERO_SEQUENCE_REJECTED",
                 !vg_bilge_bench_build_sample(
                     &bench, VG_BILGE_NORMAL, VG_QUALITY_VALID, 1800u, 0u),
                 &passed, &total);

    vg_d3_record("BENCH_NULL_REJECTED",
                 !vg_bilge_bench_build_sample(
                     NULL, VG_BILGE_NORMAL, VG_QUALITY_VALID, 1800u, 1u),
                 &passed, &total);

    vg_bilge_sim_t sim = {0};

    vg_d3_record("SIM_INIT",
                 vg_bilge_sim_init(&sim, 3000u, 100u) &&
                 sim.initialized && sim.next_step == 0u,
                 &passed, &total);

    vg_d3_record("SIM_ZERO_INTERVAL_REJECTED",
                 !vg_bilge_sim_init(&sim, 0u, 0u),
                 &passed, &total);

    vg_d3_record("SIM_NULL_INIT_REJECTED",
                 !vg_bilge_sim_init(NULL, 0u, 100u),
                 &passed, &total);

    vg_bilge_sim_init(&sim, 3000u, 100u);

    static const vg_bilge_state_t expected_state[VG_BILGE_SIM_STEPS] = {
        VG_BILGE_NORMAL,
        VG_BILGE_HIGH,
        VG_BILGE_HIGH,
        VG_BILGE_FAULT,
        VG_BILGE_FAULT,
        VG_BILGE_UNKNOWN,
        VG_BILGE_NORMAL
    };

    static const vg_data_quality_t expected_quality[VG_BILGE_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_STALE,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_VALID
    };

    bool sequence_ok = true;
    for (size_t i = 0u; i < VG_BILGE_SIM_STEPS; ++i) {
        vg_bilge_sample_t current = {0};
        if (vg_bilge_sim_next(&sim, &current) != VG_BILGE_SIM_SAMPLE ||
            !vg_bilge_sample_is_consistent(&current) ||
            current.meta.source_mode != VG_SOURCE_SIMULATION ||
            current.meta.quality != expected_quality[i] ||
            current.meta.sampled_at_ms != 3000u + 100u * (uint64_t)i ||
            current.meta.sequence != (uint32_t)(i + 1u) ||
            current.state != expected_state[i]) {
            sequence_ok = false;
            break;
        }
    }

    vg_d3_record("SIM_DETERMINISTIC_SEQUENCE", sequence_ok, &passed, &total);

    vg_bilge_sample_t after = {0};
    vg_d3_record("SIM_COMPLETE",
                 vg_bilge_sim_next(&sim, &after) == VG_BILGE_SIM_COMPLETE &&
                 sim.next_step == VG_BILGE_SIM_STEPS,
                 &passed, &total);

    vg_bilge_sim_t uninitialized = {0};
    vg_d3_record("SIM_UNINITIALIZED_REJECTED",
                 vg_bilge_sim_next(&uninitialized, &after) ==
                     VG_BILGE_SIM_REJECTED,
                 &passed, &total);

    vg_d3_record("SIM_NULL_REJECTED",
                 vg_bilge_sim_next(NULL, &after) == VG_BILGE_SIM_REJECTED,
                 &passed, &total);

    vg_bilge_sim_init(&sim, 0u, 1u);
    vg_d3_record("SIM_NULL_OUTPUT_REJECTED",
                 vg_bilge_sim_next(&sim, NULL) == VG_BILGE_SIM_REJECTED &&
                 sim.next_step == 0u,
                 &passed, &total);

    vg_bilge_sim_init(&sim, UINT64_MAX - 1u, 2u);
    vg_d3_record("SIM_TIMESTAMP_OVERFLOW_REJECTED",
                 !vg_bilge_sim_sample_for_step(&sim, 1u, &after),
                 &passed, &total);

    vg_bilge_sim_init(&sim, 500u, 10u);
    uint64_t timestamp = 999u;
    vg_d3_record("SIM_TIMESTAMP_STEP0",
                 vg_bilge_sim_timestamp(&sim, 0u, &timestamp) &&
                 timestamp == 500u,
                 &passed, &total);

    vg_d3_record("SIM_TIMESTAMP_OUT_OF_RANGE",
                 !vg_bilge_sim_timestamp(&sim, VG_BILGE_SIM_STEPS, &timestamp),
                 &passed, &total);

    vg_d3_record("SIM_SAMPLE_OUT_OF_RANGE",
                 !vg_bilge_sim_sample_for_step(&sim, VG_BILGE_SIM_STEPS, &after),
                 &passed, &total);

    vg_d3_record("SIM_SAMPLE_NULL_REJECTED",
                 !vg_bilge_sim_sample_for_step(&sim, 0u, NULL),
                 &passed, &total);

    vg_bilge_sim_init(&sim, 1000u, 10u);
    vg_bilge_sample_t check = {0};
    vg_d3_record("SIM_MISSING_FAULT",
                 vg_bilge_sim_sample_for_step(&sim, 3u, &check) &&
                 check.meta.quality == VG_QUALITY_MISSING &&
                 check.state == VG_BILGE_FAULT,
                 &passed, &total);

    vg_d3_record("SIM_INVALID_FAULT",
                 vg_bilge_sim_sample_for_step(&sim, 4u, &check) &&
                 check.meta.quality == VG_QUALITY_INVALID &&
                 check.state == VG_BILGE_FAULT,
                 &passed, &total);

    vg_d3_record("SIM_UNKNOWN_UNKNOWN",
                 vg_bilge_sim_sample_for_step(&sim, 5u, &check) &&
                 check.meta.quality == VG_QUALITY_UNKNOWN &&
                 check.state == VG_BILGE_UNKNOWN,
                 &passed, &total);

    vg_d3_record("SIM_HIGH_PRESENT",
                 vg_bilge_sim_sample_for_step(&sim, 1u, &check) &&
                 check.meta.quality == VG_QUALITY_VALID &&
                 check.state == VG_BILGE_HIGH,
                 &passed, &total);

    vg_d3_record("SIM_RECOVERY_NORMAL",
                 vg_bilge_sim_sample_for_step(&sim, 6u, &check) &&
                 check.meta.quality == VG_QUALITY_VALID &&
                 check.state == VG_BILGE_NORMAL,
                 &passed, &total);

    vg_d3_record("CASE_COUNT_EXACT",
                 total + 1u == VG_D3_EXPECTED_CASES,
                 &passed, &total);

    printf("PHASE4_D3_BILGE_PROVIDER_SELFTEST: %s (%u/%u)\n",
           passed == total && total == VG_D3_EXPECTED_CASES ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)total);
}

#endif /* VG_PHASE4_D3_SELFTEST_H */
