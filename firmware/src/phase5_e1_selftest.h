#ifndef VG_PHASE5_E1_SELFTEST_H
#define VG_PHASE5_E1_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#include "safety_policy.h"

#define VG_E1_EXPECTED_CASES 51u

static inline void vg_e1_record(
    const char *name,
    bool success,
    size_t *passed,
    size_t *total)
{
    printf("E1_SAFETY_POLICY_TEST %s: %s\n", name, success ? "PASS" : "FAIL");
    (*total)++;
    if (success) {
        (*passed)++;
    }
}

static inline vg_door_sample_t vg_e1_door_sample(
    vg_source_mode_t source_mode,
    vg_data_quality_t quality,
    vg_door_state_t state,
    uint32_t sequence)
{
    vg_door_sample_t sample = {
        .meta = {
            .source_mode = source_mode,
            .quality = quality,
            .sampled_at_ms = 100u,
            .sequence = sequence
        },
        .state = state
    };
    return sample;
}

static inline void run_phase5_e1_safety_policy_selftest(void)
{
    size_t passed = 0u;
    size_t total = 0u;

    vg_e1_record("SCOPE_VIRTUAL_PRESTART",
        strcmp(vg_safety_policy_scope_note(),
               "virtual pre-start demonstration policy only") == 0,
        &passed, &total);
    vg_e1_record("DISCLAIMER_NO_PHYSICAL_INTERLOCK",
        strcmp(vg_safety_policy_hazard_note(),
               "not a physical starter interlock or certified vessel safety rule") == 0,
        &passed, &total);

    vg_e1_record("RULE_DISABLED_KNOWN",
        vg_policy_rule_mode_is_known(VG_POLICY_RULE_DISABLED), &passed, &total);
    vg_e1_record("RULE_ALERT_ONLY_KNOWN",
        vg_policy_rule_mode_is_known(VG_POLICY_RULE_ALERT_ONLY), &passed, &total);
    vg_e1_record("RULE_BLOCK_KNOWN",
        vg_policy_rule_mode_is_known(VG_POLICY_RULE_BLOCK), &passed, &total);
    vg_e1_record("RULE_UNKNOWN_REJECTED",
        !vg_policy_rule_mode_is_known((vg_policy_rule_mode_t)99), &passed, &total);

    vg_prestart_policy_config_t config = { .hatch_rule_mode = VG_POLICY_RULE_BLOCK };
    vg_e1_record("CONFIG_BLOCK_VALID",
        vg_prestart_policy_config_is_consistent(&config), &passed, &total);
    config.hatch_rule_mode = VG_POLICY_RULE_ALERT_ONLY;
    vg_e1_record("CONFIG_ALERT_VALID",
        vg_prestart_policy_config_is_consistent(&config), &passed, &total);
    config.hatch_rule_mode = VG_POLICY_RULE_DISABLED;
    vg_e1_record("CONFIG_DISABLED_VALID",
        vg_prestart_policy_config_is_consistent(&config), &passed, &total);
    config.hatch_rule_mode = (vg_policy_rule_mode_t)99;
    vg_e1_record("CONFIG_UNKNOWN_REJECTED",
        !vg_prestart_policy_config_is_consistent(&config), &passed, &total);
    vg_e1_record("CONFIG_NULL_REJECTED",
        !vg_prestart_policy_config_is_consistent(NULL), &passed, &total);

    vg_prestart_decision_t decision = {0};
    vg_door_sample_t open = vg_e1_door_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_DOOR_STATE_OPEN, 1u);
    config.hatch_rule_mode = VG_POLICY_RULE_BLOCK;
    vg_e1_record("SIM001_OPEN_BLOCK_EVALUATED",
        vg_prestart_evaluate_hatch(&config, &open, &decision), &passed, &total);
    vg_e1_record("SIM001_OPEN_BLOCK_PERMITTED",
        decision.start_permitted && !decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_NONE,
        &passed, &total);
    vg_e1_record("SIM001_OPEN_DECISION_CONSISTENT",
        vg_prestart_decision_is_consistent(&decision), &passed, &total);
    vg_e1_record("SIM001_PROVENANCE_PRESERVED",
        decision.source_mode == VG_SOURCE_SIMULATION &&
        decision.input_quality == VG_QUALITY_VALID,
        &passed, &total);

    vg_door_sample_t closed = vg_e1_door_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_DOOR_STATE_CLOSED, 2u);
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("SIM002_CLOSED_BLOCK_EVALUATED",
        vg_prestart_evaluate_hatch(&config, &closed, &decision), &passed, &total);
    vg_e1_record("SIM002_CLOSED_BLOCK_REJECTS_START",
        !decision.start_permitted && decision.condition_present,
        &passed, &total);
    vg_e1_record("SIM002_CLOSED_REASON_CODE",
        decision.reason_code == VG_SAFETY_REASON_HATCH_CLOSED,
        &passed, &total);
    vg_e1_record("SIM002_CLOSED_DECISION_CONSISTENT",
        vg_prestart_decision_is_consistent(&decision), &passed, &total);

    config.hatch_rule_mode = VG_POLICY_RULE_ALERT_ONLY;
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("CLOSED_ALERT_EVALUATED",
        vg_prestart_evaluate_hatch(&config, &closed, &decision), &passed, &total);
    vg_e1_record("CLOSED_ALERT_PERMITS_WITH_REASON",
        decision.start_permitted && decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_HATCH_CLOSED,
        &passed, &total);

    config.hatch_rule_mode = VG_POLICY_RULE_DISABLED;
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("CLOSED_DISABLED_EVALUATED",
        vg_prestart_evaluate_hatch(&config, &closed, &decision), &passed, &total);
    vg_e1_record("CLOSED_DISABLED_NO_CONDITION",
        decision.start_permitted && !decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_NONE,
        &passed, &total);

    vg_door_sample_t missing = vg_e1_door_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_MISSING, VG_DOOR_STATE_UNKNOWN, 3u);
    config.hatch_rule_mode = VG_POLICY_RULE_BLOCK;
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("MISSING_BLOCK_EVALUATED",
        vg_prestart_evaluate_hatch(&config, &missing, &decision), &passed, &total);
    vg_e1_record("MISSING_BLOCK_NOT_SAFE",
        !decision.start_permitted && decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_HATCH_NOT_CURRENT,
        &passed, &total);

    vg_door_sample_t invalid = vg_e1_door_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_INVALID, VG_DOOR_STATE_UNKNOWN, 4u);
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("INVALID_BLOCK_NOT_SAFE",
        vg_prestart_evaluate_hatch(&config, &invalid, &decision) &&
        !decision.start_permitted &&
        decision.reason_code == VG_SAFETY_REASON_HATCH_NOT_CURRENT,
        &passed, &total);

    vg_door_sample_t unknown = vg_e1_door_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_UNKNOWN, VG_DOOR_STATE_UNKNOWN, 5u);
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("UNKNOWN_BLOCK_NOT_SAFE",
        vg_prestart_evaluate_hatch(&config, &unknown, &decision) &&
        !decision.start_permitted &&
        decision.reason_code == VG_SAFETY_REASON_HATCH_NOT_CURRENT,
        &passed, &total);

    vg_door_sample_t stale = vg_e1_door_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_STALE, VG_DOOR_STATE_OPEN, 6u);
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("STALE_OPEN_BLOCK_NOT_CURRENT",
        vg_prestart_evaluate_hatch(&config, &stale, &decision) &&
        !decision.start_permitted &&
        decision.reason_code == VG_SAFETY_REASON_HATCH_NOT_CURRENT,
        &passed, &total);

    config.hatch_rule_mode = VG_POLICY_RULE_ALERT_ONLY;
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("MISSING_ALERT_PERMITTED_WITH_FAULT_REASON",
        vg_prestart_evaluate_hatch(&config, &missing, &decision) &&
        decision.start_permitted && decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_HATCH_NOT_CURRENT,
        &passed, &total);

    config.hatch_rule_mode = VG_POLICY_RULE_DISABLED;
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("MISSING_DISABLED_IGNORED_BY_CONFIG",
        vg_prestart_evaluate_hatch(&config, &missing, &decision) &&
        decision.start_permitted && !decision.condition_present,
        &passed, &total);

    vg_door_sample_t bench_open = vg_e1_door_sample(
        VG_SOURCE_BENCH_TEST, VG_QUALITY_VALID, VG_DOOR_STATE_OPEN, 7u);
    config.hatch_rule_mode = VG_POLICY_RULE_BLOCK;
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("BENCH_OPEN_ACCEPTED",
        vg_prestart_evaluate_hatch(&config, &bench_open, &decision) &&
        decision.start_permitted && decision.source_mode == VG_SOURCE_BENCH_TEST,
        &passed, &total);

    vg_door_sample_t bench_closed = vg_e1_door_sample(
        VG_SOURCE_BENCH_TEST, VG_QUALITY_VALID, VG_DOOR_STATE_CLOSED, 8u);
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("BENCH_CLOSED_BLOCKED",
        vg_prestart_evaluate_hatch(&config, &bench_closed, &decision) &&
        !decision.start_permitted &&
        decision.reason_code == VG_SAFETY_REASON_HATCH_CLOSED,
        &passed, &total);

    vg_door_sample_t physical = vg_e1_door_sample(
        VG_SOURCE_PHYSICAL, VG_QUALITY_VALID, VG_DOOR_STATE_OPEN, 9u);
    decision = (vg_prestart_decision_t){0};
    vg_e1_record("PHYSICAL_SOURCE_REJECTED",
        !vg_prestart_evaluate_hatch(&config, &physical, &decision), &passed, &total);

    vg_door_sample_t bad_state = vg_e1_door_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_DOOR_STATE_UNKNOWN, 10u);
    vg_e1_record("VALID_UNKNOWN_STATE_REJECTED",
        !vg_prestart_evaluate_hatch(&config, &bad_state, &decision), &passed, &total);

    vg_door_sample_t zero_sequence = vg_e1_door_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_DOOR_STATE_OPEN, 0u);
    vg_e1_record("ZERO_SEQUENCE_REJECTED",
        !vg_prestart_evaluate_hatch(&config, &zero_sequence, &decision), &passed, &total);

    config.hatch_rule_mode = (vg_policy_rule_mode_t)99;
    vg_e1_record("UNKNOWN_CONFIG_REJECTED",
        !vg_prestart_evaluate_hatch(&config, &open, &decision), &passed, &total);
    config.hatch_rule_mode = VG_POLICY_RULE_BLOCK;
    vg_e1_record("NULL_CONFIG_REJECTED",
        !vg_prestart_evaluate_hatch(NULL, &open, &decision), &passed, &total);
    vg_e1_record("NULL_SAMPLE_REJECTED",
        !vg_prestart_evaluate_hatch(&config, NULL, &decision), &passed, &total);
    vg_e1_record("NULL_OUTPUT_REJECTED",
        !vg_prestart_evaluate_hatch(&config, &open, NULL), &passed, &total);

    vg_prestart_decision_t bad_decision = {
        .evaluated = true,
        .start_permitted = false,
        .condition_present = false,
        .applied_rule_mode = VG_POLICY_RULE_BLOCK,
        .reason_code = VG_SAFETY_REASON_NONE,
        .source_mode = VG_SOURCE_SIMULATION,
        .input_quality = VG_QUALITY_VALID
    };
    vg_e1_record("DECISION_NO_CONDITION_MUST_PERMIT",
        !vg_prestart_decision_is_consistent(&bad_decision), &passed, &total);
    bad_decision.start_permitted = true;
    bad_decision.condition_present = true;
    bad_decision.reason_code = VG_SAFETY_REASON_HATCH_CLOSED;
    vg_e1_record("DECISION_BLOCK_CONDITION_MUST_REJECT",
        !vg_prestart_decision_is_consistent(&bad_decision), &passed, &total);
    bad_decision.applied_rule_mode = VG_POLICY_RULE_ALERT_ONLY;
    vg_e1_record("DECISION_ALERT_CONDITION_CAN_PERMIT",
        vg_prestart_decision_is_consistent(&bad_decision), &passed, &total);
    bad_decision.applied_rule_mode = VG_POLICY_RULE_DISABLED;
    vg_e1_record("DECISION_DISABLED_CANNOT_SURFACE_CONDITION",
        !vg_prestart_decision_is_consistent(&bad_decision), &passed, &total);
    bad_decision.applied_rule_mode = VG_POLICY_RULE_ALERT_ONLY;
    bad_decision.reason_code = (vg_safety_reason_code_t)9999;
    vg_e1_record("DECISION_UNKNOWN_REASON_REJECTED",
        !vg_prestart_decision_is_consistent(&bad_decision), &passed, &total);
    bad_decision.reason_code = VG_SAFETY_REASON_HATCH_CLOSED;
    bad_decision.source_mode = VG_SOURCE_PHYSICAL;
    vg_e1_record("DECISION_PHYSICAL_SOURCE_REJECTED",
        !vg_prestart_decision_is_consistent(&bad_decision), &passed, &total);
    bad_decision.source_mode = VG_SOURCE_SIMULATION;
    bad_decision.input_quality = (vg_data_quality_t)99;
    vg_e1_record("DECISION_UNKNOWN_QUALITY_REJECTED",
        !vg_prestart_decision_is_consistent(&bad_decision), &passed, &total);
    vg_e1_record("DECISION_NULL_REJECTED",
        !vg_prestart_decision_is_consistent(NULL), &passed, &total);

    vg_e1_record("REASON_NONE_NOT_HATCH",
        !vg_safety_reason_is_hatch(VG_SAFETY_REASON_NONE), &passed, &total);
    vg_e1_record("REASON_CLOSED_IS_HATCH",
        vg_safety_reason_is_hatch(VG_SAFETY_REASON_HATCH_CLOSED), &passed, &total);
    vg_e1_record("REASON_NOT_CURRENT_IS_HATCH",
        vg_safety_reason_is_hatch(VG_SAFETY_REASON_HATCH_NOT_CURRENT), &passed, &total);

    vg_e1_record("CASE_COUNT_EXACT",
        total + 1u == VG_E1_EXPECTED_CASES, &passed, &total);

    printf("PHASE5_E1_SAFETY_POLICY_SELFTEST: %s (%u/%u)\n",
           passed == total ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)total);
}

#endif /* VG_PHASE5_E1_SELFTEST_H */
