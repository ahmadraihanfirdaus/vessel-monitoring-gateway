#ifndef VG_PHASE4_D2_SELFTEST_H
#define VG_PHASE4_D2_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <math.h>

#include "provider_fuel_vapor.h"

/*
 * Phase 4 Batch D2 development self-test for IF-02 / SAF-004.
 *
 * PASS means only the software provider contract behaved as tested. It does
 * not mean MQ-2 wiring, heater/loop power, ADC compatibility, calibration,
 * gas specificity, alarm threshold validation, bench hardware, or vessel
 * integration has been verified.
 */

#define VG_D2_EXPECTED_CASES 53u

static inline void vg_d2_record(
    const char *name,
    bool success,
    size_t *passed,
    size_t *total
)
{
    printf("D2_FUEL_VAPOR_TEST %s: %s\n",
           name,
           success ? "PASS" : "FAIL");
    (*total)++;
    if (success) {
        (*passed)++;
    }
}

static inline void run_phase4_d2_fuel_vapor_provider_selftest(void)
{
    size_t passed = 0u;
    size_t total = 0u;

    vg_d2_record("STATE_NORMAL_OPERATIONAL",
                 vg_fuel_vapor_state_is_operational(VG_FUEL_VAPOR_NORMAL),
                 &passed, &total);
    vg_d2_record("STATE_WARNING_OPERATIONAL",
                 vg_fuel_vapor_state_is_operational(VG_FUEL_VAPOR_WARNING),
                 &passed, &total);
    vg_d2_record("STATE_ALARM_OPERATIONAL",
                 vg_fuel_vapor_state_is_operational(VG_FUEL_VAPOR_ALARM),
                 &passed, &total);
    vg_d2_record("STATE_FAULT_NOT_OPERATIONAL",
                 !vg_fuel_vapor_state_is_operational(VG_FUEL_VAPOR_FAULT),
                 &passed, &total);
    vg_d2_record("STATE_UNKNOWN_NOT_OPERATIONAL",
                 !vg_fuel_vapor_state_is_operational(VG_FUEL_VAPOR_UNKNOWN),
                 &passed, &total);

    vg_fuel_vapor_sample_t sample = {
        .meta = {
            .source_mode = VG_SOURCE_SIMULATION,
            .quality = VG_QUALITY_VALID,
            .sampled_at_ms = 100u,
            .sequence = 1u
        },
        .state = VG_FUEL_VAPOR_NORMAL,
        .has_value = true,
        .surrogate_value = 0.10f
    };

    vg_d2_record("VALID_NORMAL_CURRENT",
                 vg_fuel_vapor_sample_is_consistent(&sample) &&
                 vg_fuel_vapor_sample_is_current(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_WARNING;
    sample.surrogate_value = 0.55f;
    vg_d2_record("VALID_WARNING_CURRENT",
                 vg_fuel_vapor_sample_is_consistent(&sample) &&
                 vg_fuel_vapor_sample_is_current(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_ALARM;
    sample.surrogate_value = 0.90f;
    vg_d2_record("VALID_ALARM_CURRENT",
                 vg_fuel_vapor_sample_is_consistent(&sample) &&
                 vg_fuel_vapor_sample_is_current(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_FAULT;
    vg_d2_record("VALID_FAULT_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_UNKNOWN;
    vg_d2_record("VALID_UNKNOWN_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_NORMAL;
    sample.has_value = false;
    vg_d2_record("VALID_NO_VALUE_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.has_value = true;
    sample.surrogate_value = NAN;
    vg_d2_record("VALID_NAN_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.surrogate_value = INFINITY;
    vg_d2_record("VALID_POS_INF_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_STALE;
    sample.state = VG_FUEL_VAPOR_WARNING;
    sample.has_value = true;
    sample.surrogate_value = 0.60f;
    vg_d2_record("STALE_WARNING_NOT_CURRENT",
                 vg_fuel_vapor_sample_is_consistent(&sample) &&
                 !vg_fuel_vapor_sample_is_current(&sample),
                 &passed, &total);

    sample.has_value = false;
    vg_d2_record("STALE_NO_VALUE_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_MISSING;
    sample.state = VG_FUEL_VAPOR_FAULT;
    sample.has_value = false;
    sample.surrogate_value = 0.0f;
    vg_d2_record("MISSING_FAULT_ACCEPTED",
                 vg_fuel_vapor_sample_is_consistent(&sample) &&
                 !vg_fuel_vapor_sample_is_current(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_NORMAL;
    vg_d2_record("MISSING_NORMAL_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_FAULT;
    sample.has_value = true;
    sample.surrogate_value = 0.0f;
    vg_d2_record("MISSING_HAS_VALUE_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_INVALID;
    sample.state = VG_FUEL_VAPOR_FAULT;
    sample.has_value = false;
    vg_d2_record("INVALID_FAULT_ACCEPTED",
                 vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_ALARM;
    vg_d2_record("INVALID_ALARM_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.quality = VG_QUALITY_UNKNOWN;
    sample.state = VG_FUEL_VAPOR_UNKNOWN;
    sample.has_value = false;
    vg_d2_record("UNKNOWN_QUALITY_UNKNOWN_STATE_ACCEPTED",
                 vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.state = VG_FUEL_VAPOR_FAULT;
    vg_d2_record("UNKNOWN_QUALITY_FAULT_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    sample.meta.source_mode = VG_SOURCE_PHYSICAL;
    vg_d2_record("PHYSICAL_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(&sample),
                 &passed, &total);

    vg_d2_record("NULL_REJECTED",
                 !vg_fuel_vapor_sample_is_consistent(NULL) &&
                 !vg_fuel_vapor_sample_is_current(NULL),
                 &passed, &total);

    vg_fuel_vapor_sample_t bench = {0};

    vg_d2_record("BENCH_VALID_NORMAL",
                 vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_NORMAL, VG_QUALITY_VALID,
                     true, 0.10f, 1000u, 1u) &&
                 bench.meta.source_mode == VG_SOURCE_BENCH_TEST &&
                 vg_fuel_vapor_sample_is_current(&bench),
                 &passed, &total);

    vg_d2_record("BENCH_VALID_WARNING",
                 vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_WARNING, VG_QUALITY_VALID,
                     true, 0.55f, 1100u, 2u) &&
                 vg_fuel_vapor_sample_is_current(&bench),
                 &passed, &total);

    vg_d2_record("BENCH_VALID_ALARM",
                 vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_ALARM, VG_QUALITY_VALID,
                     true, 0.90f, 1200u, 3u) &&
                 vg_fuel_vapor_sample_is_current(&bench),
                 &passed, &total);

    vg_d2_record("BENCH_MISSING_FAULT",
                 vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_FAULT, VG_QUALITY_MISSING,
                     false, 0.0f, 1300u, 4u) &&
                 vg_fuel_vapor_sample_is_consistent(&bench) &&
                 !vg_fuel_vapor_sample_is_current(&bench),
                 &passed, &total);

    vg_d2_record("BENCH_INVALID_FAULT",
                 vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_FAULT, VG_QUALITY_INVALID,
                     false, 0.0f, 1400u, 5u),
                 &passed, &total);

    vg_d2_record("BENCH_UNKNOWN",
                 vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_UNKNOWN, VG_QUALITY_UNKNOWN,
                     false, 0.0f, 1500u, 6u),
                 &passed, &total);

    vg_d2_record("BENCH_STALE_ALARM",
                 vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_ALARM, VG_QUALITY_STALE,
                     true, 0.88f, 1600u, 7u) &&
                 !vg_fuel_vapor_sample_is_current(&bench),
                 &passed, &total);

    vg_d2_record("BENCH_MISSING_NORMAL_REJECTED",
                 !vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_NORMAL, VG_QUALITY_MISSING,
                     false, 0.0f, 1700u, 8u),
                 &passed, &total);

    vg_d2_record("BENCH_VALID_FAULT_REJECTED",
                 !vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_FAULT, VG_QUALITY_VALID,
                     true, 0.7f, 1800u, 9u),
                 &passed, &total);

    vg_d2_record("BENCH_VALID_NO_VALUE_REJECTED",
                 !vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_NORMAL, VG_QUALITY_VALID,
                     false, 0.0f, 1900u, 10u),
                 &passed, &total);

    vg_d2_record("BENCH_ZERO_SEQUENCE_REJECTED",
                 !vg_fuel_vapor_bench_build_sample(
                     &bench, VG_FUEL_VAPOR_NORMAL, VG_QUALITY_VALID,
                     true, 0.1f, 2000u, 0u),
                 &passed, &total);

    vg_d2_record("BENCH_NULL_REJECTED",
                 !vg_fuel_vapor_bench_build_sample(
                     NULL, VG_FUEL_VAPOR_NORMAL, VG_QUALITY_VALID,
                     true, 0.1f, 2000u, 1u),
                 &passed, &total);

    vg_fuel_vapor_sim_t sim = {0};

    vg_d2_record("SIM_INIT",
                 vg_fuel_vapor_sim_init(&sim, 3000u, 100u) &&
                 sim.initialized && sim.next_step == 0u,
                 &passed, &total);

    vg_d2_record("SIM_ZERO_INTERVAL_REJECTED",
                 !vg_fuel_vapor_sim_init(&sim, 0u, 0u),
                 &passed, &total);

    vg_d2_record("SIM_NULL_INIT_REJECTED",
                 !vg_fuel_vapor_sim_init(NULL, 0u, 100u),
                 &passed, &total);

    vg_fuel_vapor_sim_init(&sim, 3000u, 100u);

    static const vg_fuel_vapor_state_t expected_state[VG_FUEL_VAPOR_SIM_STEPS] = {
        VG_FUEL_VAPOR_NORMAL,
        VG_FUEL_VAPOR_WARNING,
        VG_FUEL_VAPOR_ALARM,
        VG_FUEL_VAPOR_FAULT,
        VG_FUEL_VAPOR_FAULT,
        VG_FUEL_VAPOR_UNKNOWN,
        VG_FUEL_VAPOR_WARNING,
        VG_FUEL_VAPOR_NORMAL
    };

    static const vg_data_quality_t expected_quality[VG_FUEL_VAPOR_SIM_STEPS] = {
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_VALID,
        VG_QUALITY_MISSING,
        VG_QUALITY_INVALID,
        VG_QUALITY_UNKNOWN,
        VG_QUALITY_STALE,
        VG_QUALITY_VALID
    };

    bool sequence_ok = true;
    for (size_t i = 0u; i < VG_FUEL_VAPOR_SIM_STEPS; ++i) {
        vg_fuel_vapor_sample_t current = {0};
        if (vg_fuel_vapor_sim_next(&sim, &current) != VG_FUEL_VAPOR_SIM_SAMPLE ||
            !vg_fuel_vapor_sample_is_consistent(&current) ||
            current.meta.source_mode != VG_SOURCE_SIMULATION ||
            current.meta.quality != expected_quality[i] ||
            current.meta.sampled_at_ms != 3000u + 100u * (uint64_t)i ||
            current.meta.sequence != (uint32_t)(i + 1u) ||
            current.state != expected_state[i]) {
            sequence_ok = false;
            break;
        }
    }

    vg_d2_record("SIM_DETERMINISTIC_SEQUENCE", sequence_ok, &passed, &total);

    vg_fuel_vapor_sample_t after = {0};
    vg_d2_record("SIM_COMPLETE",
                 vg_fuel_vapor_sim_next(&sim, &after) ==
                     VG_FUEL_VAPOR_SIM_COMPLETE &&
                 sim.next_step == VG_FUEL_VAPOR_SIM_STEPS,
                 &passed, &total);

    vg_fuel_vapor_sim_t uninitialized = {0};
    vg_d2_record("SIM_UNINITIALIZED_REJECTED",
                 vg_fuel_vapor_sim_next(&uninitialized, &after) ==
                     VG_FUEL_VAPOR_SIM_REJECTED,
                 &passed, &total);

    vg_d2_record("SIM_NULL_REJECTED",
                 vg_fuel_vapor_sim_next(NULL, &after) ==
                     VG_FUEL_VAPOR_SIM_REJECTED,
                 &passed, &total);

    vg_fuel_vapor_sim_init(&sim, 0u, 1u);
    vg_d2_record("SIM_NULL_OUTPUT_REJECTED",
                 vg_fuel_vapor_sim_next(&sim, NULL) ==
                     VG_FUEL_VAPOR_SIM_REJECTED &&
                 sim.next_step == 0u,
                 &passed, &total);

    vg_fuel_vapor_sim_init(&sim, UINT64_MAX - 1u, 2u);
    vg_d2_record("SIM_TIMESTAMP_OVERFLOW_REJECTED",
                 !vg_fuel_vapor_sim_sample_for_step(&sim, 1u, &after),
                 &passed, &total);

    vg_fuel_vapor_sim_init(&sim, 500u, 10u);
    uint64_t timestamp = 999u;
    vg_d2_record("SIM_TIMESTAMP_STEP0",
                 vg_fuel_vapor_sim_timestamp(&sim, 0u, &timestamp) &&
                 timestamp == 500u,
                 &passed, &total);

    vg_d2_record("SIM_TIMESTAMP_OUT_OF_RANGE",
                 !vg_fuel_vapor_sim_timestamp(
                     &sim, VG_FUEL_VAPOR_SIM_STEPS, &timestamp),
                 &passed, &total);

    vg_d2_record("SIM_SAMPLE_OUT_OF_RANGE",
                 !vg_fuel_vapor_sim_sample_for_step(
                     &sim, VG_FUEL_VAPOR_SIM_STEPS, &after),
                 &passed, &total);

    vg_d2_record("SIM_SAMPLE_NULL_REJECTED",
                 !vg_fuel_vapor_sim_sample_for_step(&sim, 0u, NULL),
                 &passed, &total);

    vg_fuel_vapor_sim_init(&sim, 1000u, 10u);
    vg_fuel_vapor_sample_t fault_sample = {0};
    vg_d2_record("SIM_MISSING_NEVER_NORMAL",
                 vg_fuel_vapor_sim_sample_for_step(&sim, 3u, &fault_sample) &&
                 fault_sample.meta.quality == VG_QUALITY_MISSING &&
                 fault_sample.state == VG_FUEL_VAPOR_FAULT &&
                 !fault_sample.has_value,
                 &passed, &total);

    vg_d2_record("SIM_INVALID_FAULT",
                 vg_fuel_vapor_sim_sample_for_step(&sim, 4u, &fault_sample) &&
                 fault_sample.meta.quality == VG_QUALITY_INVALID &&
                 fault_sample.state == VG_FUEL_VAPOR_FAULT &&
                 !fault_sample.has_value,
                 &passed, &total);

    vg_d2_record("SIM_UNKNOWN_UNKNOWN",
                 vg_fuel_vapor_sim_sample_for_step(&sim, 5u, &fault_sample) &&
                 fault_sample.meta.quality == VG_QUALITY_UNKNOWN &&
                 fault_sample.state == VG_FUEL_VAPOR_UNKNOWN &&
                 !fault_sample.has_value,
                 &passed, &total);

    vg_d2_record("CASE_COUNT_EXACT",
                 total + 1u == VG_D2_EXPECTED_CASES,
                 &passed, &total);

    printf("PHASE4_D2_FUEL_VAPOR_PROVIDER_SELFTEST: %s (%u/%u)\n",
           passed == total && total == VG_D2_EXPECTED_CASES ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)total);
}

#endif /* VG_PHASE4_D2_SELFTEST_H */
