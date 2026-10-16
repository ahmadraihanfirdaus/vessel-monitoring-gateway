#ifndef VG_PHASE4_D1_SELFTEST_H
#define VG_PHASE4_D1_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "provider_contract.h"
#include "provider_door.h"

/*
 * Phase 4 Batch D1 development self-test.
 *
 * This test validates software contracts only. A PASS does not imply physical
 * bench wiring, electrical compatibility, debounce behavior, calibration,
 * sensor accuracy, or vessel integration.
 */

#define VG_D1_EXPECTED_CASES 38u

static inline void vg_d1_record(
    const char *name,
    bool success,
    size_t *passed,
    size_t *total
)
{
    printf("D1_DOOR_TEST %s: %s\n",
           name,
           success ? "PASS" : "FAIL");

    (*total)++;

    if (success) {
        (*passed)++;
    }
}

static inline void run_phase4_d1_door_provider_selftest(void)
{
    size_t passed = 0u;
    size_t total = 0u;

    vg_provider_meta_t meta = {0};

    vg_d1_record(
        "META_SIM_ACCEPTED",
        vg_provider_meta_init(
            &meta,
            VG_SOURCE_SIMULATION,
            VG_QUALITY_VALID,
            0u,
            1u) &&
        meta.source_mode == VG_SOURCE_SIMULATION &&
        meta.quality == VG_QUALITY_VALID &&
        meta.sampled_at_ms == 0u &&
        meta.sequence == 1u,
        &passed,
        &total);

    vg_d1_record(
        "META_BENCH_ACCEPTED",
        vg_provider_meta_init(
            &meta,
            VG_SOURCE_BENCH_TEST,
            VG_QUALITY_MISSING,
            25u,
            2u) &&
        meta.source_mode == VG_SOURCE_BENCH_TEST,
        &passed,
        &total);

    vg_d1_record(
        "META_PHYSICAL_REJECTED",
        !vg_provider_meta_init(
            &meta,
            VG_SOURCE_PHYSICAL,
            VG_QUALITY_VALID,
            0u,
            1u),
        &passed,
        &total);

    vg_d1_record(
        "META_UNKNOWN_SOURCE_REJECTED",
        !vg_provider_meta_init(
            &meta,
            VG_SOURCE_UNKNOWN,
            VG_QUALITY_VALID,
            0u,
            1u),
        &passed,
        &total);

    vg_d1_record(
        "META_ZERO_SEQUENCE_REJECTED",
        !vg_provider_meta_init(
            &meta,
            VG_SOURCE_SIMULATION,
            VG_QUALITY_VALID,
            0u,
            0u),
        &passed,
        &total);

    vg_d1_record(
        "META_BAD_QUALITY_REJECTED",
        !vg_provider_meta_init(
            &meta,
            VG_SOURCE_SIMULATION,
            (vg_data_quality_t)99,
            0u,
            1u),
        &passed,
        &total);

    vg_d1_record(
        "META_NULL_REJECTED",
        !vg_provider_meta_init(
            NULL,
            VG_SOURCE_SIMULATION,
            VG_QUALITY_VALID,
            0u,
            1u),
        &passed,
        &total);

    vg_door_sample_t sample = {
        .meta = {
            .source_mode = VG_SOURCE_SIMULATION,
            .quality = VG_QUALITY_VALID,
            .sampled_at_ms = 100u,
            .sequence = 1u
        },
        .state = VG_DOOR_STATE_OPEN
    };

    vg_d1_record(
        "SAMPLE_VALID_OPEN",
        vg_door_sample_is_consistent(&sample) &&
        vg_door_sample_is_current(&sample),
        &passed,
        &total);

    sample.state = VG_DOOR_STATE_CLOSED;
    vg_d1_record(
        "SAMPLE_VALID_CLOSED",
        vg_door_sample_is_consistent(&sample) &&
        vg_door_sample_is_current(&sample),
        &passed,
        &total);

    sample.state = VG_DOOR_STATE_UNKNOWN;
    vg_d1_record(
        "SAMPLE_VALID_UNKNOWN_REJECTED",
        !vg_door_sample_is_consistent(&sample) &&
        !vg_door_sample_is_current(&sample),
        &passed,
        &total);

    sample.meta.quality = VG_QUALITY_MISSING;
    sample.state = VG_DOOR_STATE_UNKNOWN;
    vg_d1_record(
        "SAMPLE_MISSING_UNKNOWN",
        vg_door_sample_is_consistent(&sample) &&
        !vg_door_sample_is_current(&sample),
        &passed,
        &total);

    sample.state = VG_DOOR_STATE_OPEN;
    vg_d1_record(
        "SAMPLE_MISSING_OPEN_REJECTED",
        !vg_door_sample_is_consistent(&sample),
        &passed,
        &total);

    sample.meta.quality = VG_QUALITY_INVALID;
    sample.state = VG_DOOR_STATE_UNKNOWN;
    vg_d1_record(
        "SAMPLE_INVALID_UNKNOWN",
        vg_door_sample_is_consistent(&sample) &&
        !vg_door_sample_is_current(&sample),
        &passed,
        &total);

    sample.meta.quality = VG_QUALITY_UNKNOWN;
    vg_d1_record(
        "SAMPLE_UNKNOWN_QUALITY_UNKNOWN_STATE",
        vg_door_sample_is_consistent(&sample),
        &passed,
        &total);

    sample.meta.quality = VG_QUALITY_STALE;
    sample.state = VG_DOOR_STATE_CLOSED;
    vg_d1_record(
        "SAMPLE_STALE_RETAINS_STATE_NOT_CURRENT",
        vg_door_sample_is_consistent(&sample) &&
        !vg_door_sample_is_current(&sample),
        &passed,
        &total);

    sample.meta.source_mode = VG_SOURCE_PHYSICAL;
    vg_d1_record(
        "SAMPLE_PHYSICAL_REJECTED",
        !vg_door_sample_is_consistent(&sample),
        &passed,
        &total);

    vg_d1_record(
        "SAMPLE_NULL_REJECTED",
        !vg_door_sample_is_consistent(NULL) &&
        !vg_door_sample_is_current(NULL),
        &passed,
        &total);

    vg_door_sample_t bench = {0};

    vg_d1_record(
        "BENCH_VALID_OPEN",
        vg_door_bench_build_sample(
            &bench,
            VG_DOOR_STATE_OPEN,
            VG_QUALITY_VALID,
            1000u,
            1u) &&
        bench.meta.source_mode == VG_SOURCE_BENCH_TEST &&
        vg_door_sample_is_current(&bench),
        &passed,
        &total);

    vg_d1_record(
        "BENCH_STALE_CLOSED",
        vg_door_bench_build_sample(
            &bench,
            VG_DOOR_STATE_CLOSED,
            VG_QUALITY_STALE,
            1100u,
            2u) &&
        vg_door_sample_is_consistent(&bench) &&
        !vg_door_sample_is_current(&bench),
        &passed,
        &total);

    vg_d1_record(
        "BENCH_MISSING_UNKNOWN",
        vg_door_bench_build_sample(
            &bench,
            VG_DOOR_STATE_UNKNOWN,
            VG_QUALITY_MISSING,
            1200u,
            3u) &&
        vg_door_sample_is_consistent(&bench),
        &passed,
        &total);

    vg_d1_record(
        "BENCH_MISSING_CLOSED_REJECTED",
        !vg_door_bench_build_sample(
            &bench,
            VG_DOOR_STATE_CLOSED,
            VG_QUALITY_MISSING,
            1300u,
            4u),
        &passed,
        &total);

    vg_d1_record(
        "BENCH_VALID_UNKNOWN_REJECTED",
        !vg_door_bench_build_sample(
            &bench,
            VG_DOOR_STATE_UNKNOWN,
            VG_QUALITY_VALID,
            1400u,
            5u),
        &passed,
        &total);

    vg_d1_record(
        "BENCH_ZERO_SEQUENCE_REJECTED",
        !vg_door_bench_build_sample(
            &bench,
            VG_DOOR_STATE_OPEN,
            VG_QUALITY_VALID,
            1500u,
            0u),
        &passed,
        &total);

    vg_d1_record(
        "BENCH_NULL_REJECTED",
        !vg_door_bench_build_sample(
            NULL,
            VG_DOOR_STATE_OPEN,
            VG_QUALITY_VALID,
            1500u,
            1u),
        &passed,
        &total);

    vg_door_sim_t sim = {0};

    vg_d1_record(
        "SIM_INIT",
        vg_door_sim_init(&sim, 2000u, 100u) &&
        sim.initialized &&
        sim.next_step == 0u,
        &passed,
        &total);

    vg_d1_record(
        "SIM_ZERO_INTERVAL_REJECTED",
        !vg_door_sim_init(&sim, 0u, 0u),
        &passed,
        &total);

    vg_d1_record(
        "SIM_NULL_INIT_REJECTED",
        !vg_door_sim_init(NULL, 0u, 100u),
        &passed,
        &total);

    vg_door_sim_init(&sim, 2000u, 100u);

    static const vg_door_state_t expected_state[VG_DOOR_SIM_STEPS] = {
        VG_DOOR_STATE_OPEN,
        VG_DOOR_STATE_CLOSED,
        VG_DOOR_STATE_UNKNOWN,
        VG_DOOR_STATE_UNKNOWN,
        VG_DOOR_STATE_CLOSED,
        VG_DOOR_STATE_OPEN
    };

    static const vg_data_quality_t expected_quality[VG_DOOR_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_STALE,
        VG_QUALITY_VALID
    };

    bool sequence_ok = true;

    for (size_t i = 0u; i < VG_DOOR_SIM_STEPS; ++i) {
        vg_door_sample_t current = {0};

        if (vg_door_sim_next(&sim, &current) != VG_DOOR_SIM_SAMPLE ||
            !vg_door_sample_is_consistent(&current) ||
            current.meta.source_mode != VG_SOURCE_SIMULATION ||
            current.meta.quality != expected_quality[i] ||
            current.meta.sampled_at_ms != 2000u + (100u * (uint64_t)i) ||
            current.meta.sequence != (uint32_t)(i + 1u) ||
            current.state != expected_state[i]) {
            sequence_ok = false;
            break;
        }
    }

    vg_d1_record(
        "SIM_DETERMINISTIC_SEQUENCE",
        sequence_ok,
        &passed,
        &total);

    vg_door_sample_t after = {0};

    vg_d1_record(
        "SIM_COMPLETE",
        vg_door_sim_next(&sim, &after) == VG_DOOR_SIM_COMPLETE &&
        sim.next_step == VG_DOOR_SIM_STEPS,
        &passed,
        &total);

    vg_door_sim_t uninitialized = {0};
    vg_d1_record(
        "SIM_UNINITIALIZED_REJECTED",
        vg_door_sim_next(&uninitialized, &after) == VG_DOOR_SIM_REJECTED,
        &passed,
        &total);

    vg_d1_record(
        "SIM_NULL_REJECTED",
        vg_door_sim_next(NULL, &after) == VG_DOOR_SIM_REJECTED,
        &passed,
        &total);

    vg_door_sim_init(&sim, 0u, 1u);
    vg_d1_record(
        "SIM_NULL_OUTPUT_REJECTED",
        vg_door_sim_next(&sim, NULL) == VG_DOOR_SIM_REJECTED &&
        sim.next_step == 0u,
        &passed,
        &total);

    vg_door_sim_init(&sim, UINT64_MAX - 1u, 2u);
    vg_d1_record(
        "SIM_TIMESTAMP_OVERFLOW_REJECTED",
        !vg_door_sim_sample_for_step(&sim, 1u, &after),
        &passed,
        &total);

    vg_door_sim_init(&sim, 500u, 10u);
    uint64_t timestamp = 999u;
    vg_d1_record(
        "SIM_TIMESTAMP_STEP0",
        vg_door_sim_timestamp(&sim, 0u, &timestamp) &&
        timestamp == 500u,
        &passed,
        &total);

    vg_d1_record(
        "SIM_TIMESTAMP_OUT_OF_RANGE",
        !vg_door_sim_timestamp(
            &sim,
            VG_DOOR_SIM_STEPS,
            &timestamp),
        &passed,
        &total);

    vg_d1_record(
        "SIM_SAMPLE_OUT_OF_RANGE",
        !vg_door_sim_sample_for_step(
            &sim,
            VG_DOOR_SIM_STEPS,
            &after),
        &passed,
        &total);

    vg_d1_record(
        "SIM_SAMPLE_NULL_REJECTED",
        !vg_door_sim_sample_for_step(
            &sim,
            0u,
            NULL),
        &passed,
        &total);

    vg_d1_record(
        "CASE_COUNT_EXACT",
        total + 1u == VG_D1_EXPECTED_CASES,
        &passed,
        &total);

    printf("PHASE4_D1_DOOR_PROVIDER_SELFTEST: %s (%u/%u)\n",
           passed == total && total == VG_D1_EXPECTED_CASES ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)total);
}

#endif /* VG_PHASE4_D1_SELFTEST_H */
