#ifndef VG_PHASE5_E2_SELFTEST_H
#define VG_PHASE5_E2_SELFTEST_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "provider_fuel_vapor.h"
#include "safety_local_alarm.h"
#include "safety_policy.h"
#include "safety_policy_runtime.h"

#define VG_E2_EXPECTED_CASES 60u

static inline void vg_e2_record(const char *name, bool ok,
                                unsigned *passed, unsigned *total)
{
    ++(*total);
    if (ok) ++(*passed);
    printf("E2_FUEL_SAFETY_TEST %s: %s\n", name, ok ? "PASS" : "FAIL");
}

static inline vg_fuel_vapor_sample_t vg_e2_fuel_sample(
    vg_source_mode_t source,
    vg_data_quality_t quality,
    vg_fuel_vapor_state_t state,
    bool has_value,
    float value,
    uint32_t sequence)
{
    vg_fuel_vapor_sample_t sample = {0};
    sample.meta.source_mode = source;
    sample.meta.quality = quality;
    sample.meta.sampled_at_ms = 100u + sequence;
    sample.meta.sequence = sequence;
    sample.state = state;
    sample.has_value = has_value;
    sample.surrogate_value = value;
    return sample;
}

static inline void run_phase5_e2_fuel_safety_selftest(void)
{
    unsigned passed = 0u;
    unsigned total = 0u;

    vg_e2_record("SCOPE_VIRTUAL_ONLY",
        vg_safety_policy_scope_note() != NULL, &passed, &total);
    vg_e2_record("LOCAL_OUTPUT_LOGICAL_ONLY",
        vg_local_alarm_scope_note() != NULL, &passed, &total);
    vg_e2_record("REASON_ALARM_IS_FUEL",
        vg_safety_reason_is_fuel_vapor(VG_SAFETY_REASON_FUEL_VAPOR_ALARM), &passed, &total);
    vg_e2_record("REASON_NOT_CURRENT_IS_FUEL",
        vg_safety_reason_is_fuel_vapor(VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT), &passed, &total);
    vg_e2_record("HATCH_REASON_NOT_FUEL",
        !vg_safety_reason_is_fuel_vapor(VG_SAFETY_REASON_HATCH_CLOSED), &passed, &total);

    vg_prestart_policy_config_t config = {
        .hatch_rule_mode = VG_POLICY_RULE_BLOCK,
        .fuel_vapor_rule_mode = VG_POLICY_RULE_BLOCK
    };
    vg_e2_record("CONFIG_BOTH_RULES_VALID",
        vg_prestart_policy_config_is_consistent(&config), &passed, &total);

    vg_fuel_vapor_sample_t normal = vg_e2_fuel_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_FUEL_VAPOR_NORMAL, true, 0.10f, 1u);
    vg_fuel_vapor_sample_t warning = vg_e2_fuel_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_FUEL_VAPOR_WARNING, true, 0.55f, 2u);
    vg_fuel_vapor_sample_t alarm = vg_e2_fuel_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_FUEL_VAPOR_ALARM, true, 0.90f, 3u);
    vg_fuel_vapor_sample_t missing = vg_e2_fuel_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_MISSING, VG_FUEL_VAPOR_FAULT, false, 0.0f, 4u);
    vg_fuel_vapor_sample_t invalid = vg_e2_fuel_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_INVALID, VG_FUEL_VAPOR_FAULT, false, 0.0f, 5u);
    vg_fuel_vapor_sample_t unknown = vg_e2_fuel_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_UNKNOWN, VG_FUEL_VAPOR_UNKNOWN, false, 0.0f, 6u);
    vg_fuel_vapor_sample_t stale = vg_e2_fuel_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_STALE, VG_FUEL_VAPOR_WARNING, true, 0.60f, 7u);

    vg_e2_record("NORMAL_SAMPLE_CONSISTENT", vg_fuel_vapor_sample_is_consistent(&normal), &passed, &total);
    vg_e2_record("ALARM_SAMPLE_CONSISTENT", vg_fuel_vapor_sample_is_consistent(&alarm), &passed, &total);
    vg_e2_record("MISSING_SAMPLE_CONSISTENT", vg_fuel_vapor_sample_is_consistent(&missing), &passed, &total);

    vg_prestart_decision_t decision = {0};
    vg_e2_record("NORMAL_EVALUATED",
        vg_prestart_evaluate_fuel_vapor(&config, &normal, &decision), &passed, &total);
    vg_e2_record("NORMAL_PERMITTED",
        decision.start_permitted && !decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_NONE, &passed, &total);

    decision = (vg_prestart_decision_t){0};
    vg_e2_record("WARNING_EVALUATED",
        vg_prestart_evaluate_fuel_vapor(&config, &warning, &decision), &passed, &total);
    vg_e2_record("WARNING_NOT_INVENTED_AS_BLOCK",
        decision.start_permitted && !decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_NONE, &passed, &total);

    decision = (vg_prestart_decision_t){0};
    vg_e2_record("SIM003_ALARM_EVALUATED",
        vg_prestart_evaluate_fuel_vapor(&config, &alarm, &decision), &passed, &total);
    vg_e2_record("SIM003_ALARM_REJECTS_START",
        !decision.start_permitted && decision.condition_present, &passed, &total);
    vg_e2_record("SIM003_ALARM_REASON_CODE",
        decision.reason_code == VG_SAFETY_REASON_FUEL_VAPOR_ALARM, &passed, &total);
    vg_e2_record("SIM003_ALARM_PROVENANCE",
        decision.source_mode == VG_SOURCE_SIMULATION &&
        decision.input_quality == VG_QUALITY_VALID, &passed, &total);
    vg_prestart_decision_t alarm_decision = decision;

    decision = (vg_prestart_decision_t){0};
    vg_e2_record("SIM004_MISSING_EVALUATED",
        vg_prestart_evaluate_fuel_vapor(&config, &missing, &decision), &passed, &total);
    vg_e2_record("SIM004_MISSING_REJECTS_START",
        !decision.start_permitted && decision.condition_present, &passed, &total);
    vg_e2_record("SIM004_MISSING_NOT_SAFE_REASON",
        decision.reason_code == VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT, &passed, &total);
    vg_e2_record("SIM004_MISSING_QUALITY_VISIBLE",
        decision.input_quality == VG_QUALITY_MISSING, &passed, &total);
    vg_prestart_decision_t missing_decision = decision;

    decision = (vg_prestart_decision_t){0};
    vg_e2_record("INVALID_FAILSAFE",
        vg_prestart_evaluate_fuel_vapor(&config, &invalid, &decision) &&
        !decision.start_permitted &&
        decision.reason_code == VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT, &passed, &total);
    decision = (vg_prestart_decision_t){0};
    vg_e2_record("UNKNOWN_FAILSAFE",
        vg_prestart_evaluate_fuel_vapor(&config, &unknown, &decision) &&
        !decision.start_permitted &&
        decision.reason_code == VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT, &passed, &total);
    decision = (vg_prestart_decision_t){0};
    vg_e2_record("STALE_FAILSAFE",
        vg_prestart_evaluate_fuel_vapor(&config, &stale, &decision) &&
        !decision.start_permitted &&
        decision.reason_code == VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT, &passed, &total);

    config.fuel_vapor_rule_mode = VG_POLICY_RULE_ALERT_ONLY;
    decision = (vg_prestart_decision_t){0};
    vg_e2_record("ALERT_ONLY_ALARM_EVALUATED",
        vg_prestart_evaluate_fuel_vapor(&config, &alarm, &decision), &passed, &total);
    vg_e2_record("ALERT_ONLY_ALARM_PERMITS_WITH_REASON",
        decision.start_permitted && decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_FUEL_VAPOR_ALARM, &passed, &total);

    config.fuel_vapor_rule_mode = VG_POLICY_RULE_DISABLED;
    decision = (vg_prestart_decision_t){0};
    vg_e2_record("DISABLED_ALARM_EVALUATED",
        vg_prestart_evaluate_fuel_vapor(&config, &alarm, &decision), &passed, &total);
    vg_e2_record("DISABLED_ALARM_NOT_SURFACED",
        decision.start_permitted && !decision.condition_present &&
        decision.reason_code == VG_SAFETY_REASON_NONE, &passed, &total);

    config.fuel_vapor_rule_mode = VG_POLICY_RULE_BLOCK;
    vg_fuel_vapor_sample_t bench_alarm = alarm;
    bench_alarm.meta.source_mode = VG_SOURCE_BENCH_TEST;
    decision = (vg_prestart_decision_t){0};
    vg_e2_record("BENCH_ALARM_ACCEPTED",
        vg_prestart_evaluate_fuel_vapor(&config, &bench_alarm, &decision) &&
        !decision.start_permitted, &passed, &total);

    vg_fuel_vapor_sample_t physical = alarm;
    physical.meta.source_mode = VG_SOURCE_PHYSICAL;
    decision = (vg_prestart_decision_t){0};
    vg_e2_record("PHYSICAL_SOURCE_REJECTED",
        !vg_prestart_evaluate_fuel_vapor(&config, &physical, &decision), &passed, &total);

    vg_fuel_vapor_sample_t bad_valid_fault = alarm;
    bad_valid_fault.state = VG_FUEL_VAPOR_FAULT;
    vg_e2_record("VALID_FAULT_REJECTED",
        !vg_prestart_evaluate_fuel_vapor(&config, &bad_valid_fault, &decision), &passed, &total);
    vg_fuel_vapor_sample_t zero_sequence = alarm;
    zero_sequence.meta.sequence = 0u;
    vg_e2_record("ZERO_SEQUENCE_REJECTED",
        !vg_prestart_evaluate_fuel_vapor(&config, &zero_sequence, &decision), &passed, &total);
    vg_e2_record("NULL_CONFIG_REJECTED",
        !vg_prestart_evaluate_fuel_vapor(NULL, &alarm, &decision), &passed, &total);
    vg_e2_record("NULL_SAMPLE_REJECTED",
        !vg_prestart_evaluate_fuel_vapor(&config, NULL, &decision), &passed, &total);
    vg_e2_record("NULL_OUTPUT_REJECTED",
        !vg_prestart_evaluate_fuel_vapor(&config, &alarm, NULL), &passed, &total);

    vg_safety_policy_runtime_t runtime = {0};
    vg_e2_record("RUNTIME_INIT", vg_safety_policy_runtime_init(&runtime), &passed, &total);
    vg_e2_record("RUNTIME_INITIAL_EMPTY",
        runtime.initialized && !runtime.has_alarm && runtime.journal.count == 0u, &passed, &total);
    vg_e2_record("SIM003_RAISE_TRANSACTION",
        vg_safety_policy_runtime_raise(&runtime, &alarm_decision, 20u, 2u, 1000u), &passed, &total);
    vg_e2_record("SIM003_ALARM_METADATA",
        runtime.has_alarm && runtime.alarm.id == 1u &&
        runtime.alarm.source_id == 20u && runtime.alarm.priority_code == 2u &&
        runtime.alarm.reason_code == (uint32_t)VG_SAFETY_REASON_FUEL_VAPOR_ALARM &&
        runtime.alarm.state == VG_ALARM_STATE_ACTIVE_UNACK, &passed, &total);
    vg_e2_record("SIM003_EVENT_RAISED",
        runtime.journal.count == 1u &&
        runtime.journal.events[0].type == VG_EVENT_ALARM_RAISED &&
        runtime.journal.events[0].linked_alarm_id == runtime.alarm.id, &passed, &total);
    vg_e2_record("SIM003_LOCAL_OUTPUT_ACTIVE",
        runtime.local_output.led_active && runtime.local_output.buzzer_active &&
        runtime.local_output.linked_alarm_id == runtime.alarm.id, &passed, &total);
    vg_e2_record("LOCAL_PATH_HAS_NO_DASHBOARD_INPUT",
        vg_local_alarm_output_is_consistent(&runtime.local_output), &passed, &total);

    vg_e2_record("ACK_TRANSACTION",
        vg_safety_policy_runtime_acknowledge(&runtime, 1010u), &passed, &total);
    vg_e2_record("ACK_DOES_NOT_CLEAR_CONDITION",
        runtime.alarm.state == VG_ALARM_STATE_ACTIVE_ACK &&
        runtime.alarm.condition_active && runtime.alarm.acknowledged, &passed, &total);
    vg_e2_record("ACK_EVENT_RECORDED",
        runtime.journal.count == 2u &&
        runtime.journal.events[1].type == VG_EVENT_ALARM_ACK, &passed, &total);
    vg_e2_record("ACK_LOCAL_OUTPUT_REMAINS_ACTIVE",
        runtime.local_output.led_active && runtime.local_output.buzzer_active, &passed, &total);
    vg_e2_record("SECOND_RAISE_WHILE_ACTIVE_REJECTED",
        !vg_safety_policy_runtime_raise(&runtime, &alarm_decision, 20u, 2u, 1020u) &&
        runtime.journal.count == 2u, &passed, &total);

    vg_safety_policy_runtime_t missing_runtime = {0};
    vg_e2_record("SIM004_RUNTIME_INIT",
        vg_safety_policy_runtime_init(&missing_runtime), &passed, &total);
    vg_e2_record("SIM004_FAULT_VISIBLE_TRANSACTION",
        vg_safety_policy_runtime_raise(&missing_runtime, &missing_decision, 20u, 2u, 2000u), &passed, &total);
    vg_e2_record("SIM004_FAULT_REASON_VISIBLE",
        missing_runtime.alarm.reason_code ==
        (uint32_t)VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT, &passed, &total);
    vg_e2_record("SIM004_FAULT_EVENT_VISIBLE",
        missing_runtime.journal.count == 1u &&
        missing_runtime.journal.events[0].type == VG_EVENT_ALARM_RAISED, &passed, &total);
    vg_e2_record("SIM004_LOCAL_OUTPUT_ACTIVE",
        missing_runtime.local_output.led_active &&
        missing_runtime.local_output.buzzer_active, &passed, &total);

    vg_safety_policy_runtime_t full = {0};
    bool full_ok = vg_safety_policy_runtime_init(&full);
    for (size_t i = 0u; full_ok && i < VG_JOURNAL_CAPACITY; ++i) {
        uint64_t event_id = 0u;
        full_ok = vg_journal_append(&full.journal, 0u, 77u,
            VG_SOURCE_SIMULATION, VG_EVENT_FAULT, (uint64_t)i + 1u, &event_id);
    }
    vg_e2_record("RUNTIME_FULL_JOURNAL_PREP",
        full_ok && full.journal.count == VG_JOURNAL_CAPACITY, &passed, &total);
    const uint64_t old_next_id = full.alarm_ids.next_id;
    vg_e2_record("RUNTIME_FULL_JOURNAL_ROLLBACK",
        !vg_safety_policy_runtime_raise(&full, &alarm_decision, 20u, 2u, 20u) &&
        !full.has_alarm && full.alarm_ids.next_id == old_next_id &&
        full.journal.count == VG_JOURNAL_CAPACITY, &passed, &total);

    vg_alarm_id_allocator_t ids = {0};
    vg_alarm_id_allocator_init(&ids);
    vg_alarm_t clear_alarm = {0};
    vg_local_alarm_output_t local = {0};
    bool clear_ok = vg_alarm_try_raise(&ids, &clear_alarm, 20u,
        VG_SOURCE_SIMULATION, 2u,
        (uint32_t)VG_SAFETY_REASON_FUEL_VAPOR_ALARM, 10u);
    clear_ok = clear_ok && vg_local_alarm_from_alarm(&clear_alarm, &local);
    vg_e2_record("LOCAL_OUTPUT_ACTIVE_FROM_ACTIVE_ALARM",
        clear_ok && local.led_active && local.buzzer_active, &passed, &total);
    clear_ok = clear_ok && vg_alarm_try_clear_condition(&clear_alarm, 11u);
    clear_ok = clear_ok && vg_local_alarm_from_alarm(&clear_alarm, &local);
    vg_e2_record("LOCAL_OUTPUT_OFF_AFTER_CLEAR",
        clear_ok && !local.led_active && !local.buzzer_active, &passed, &total);

    vg_e2_record("RUNTIME_NULL_INIT_REJECTED",
        !vg_safety_policy_runtime_init(NULL), &passed, &total);
    vg_e2_record("RUNTIME_NULL_DECISION_REJECTED",
        !vg_safety_policy_runtime_raise(&missing_runtime, NULL, 20u, 2u, 3000u), &passed, &total);
    vg_e2_record("RUNTIME_ZERO_SOURCE_REJECTED",
        !vg_safety_policy_runtime_raise(&(vg_safety_policy_runtime_t){0},
            &alarm_decision, 0u, 2u, 3000u), &passed, &total);

    vg_e2_record("CASE_COUNT_EXACT",
        total + 1u == VG_E2_EXPECTED_CASES, &passed, &total);

    printf("PHASE5_E2_FUEL_SAFETY_SELFTEST: %s (%u/%u)\n",
           passed == total ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)total);
}

#endif /* VG_PHASE5_E2_SELFTEST_H */
