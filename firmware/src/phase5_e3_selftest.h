#ifndef VG_PHASE5_E3_SELFTEST_H
#define VG_PHASE5_E3_SELFTEST_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "safety_monitor_policy.h"
#include "safety_monitor_runtime.h"

#define VG_E3_EXPECTED_CASES 85u

static inline void vg_e3_record(
    const char *name, bool success, unsigned *passed, unsigned *total)
{
    ++(*total);
    if (success) {
        ++(*passed);
    }
    printf("E3_MONITOR_SAFETY_TEST %s: %s\n", name, success ? "PASS" : "FAIL");
}

static inline vg_bilge_sample_t vg_e3_bilge_sample(
    vg_source_mode_t source_mode,
    vg_data_quality_t quality,
    vg_bilge_state_t state,
    uint32_t sequence)
{
    vg_bilge_sample_t sample = {0};
    (void)vg_provider_meta_init(
        &sample.meta, source_mode, quality, 100u, sequence);
    sample.state = state;
    return sample;
}

static inline vg_temperature_sample_t vg_e3_temperature_sample(
    vg_source_mode_t source_mode,
    vg_data_quality_t quality,
    bool has_value,
    float temperature_c,
    uint32_t sequence)
{
    vg_temperature_sample_t sample = {0};
    (void)vg_provider_meta_init(
        &sample.meta, source_mode, quality, 100u, sequence);
    sample.has_value = has_value;
    sample.temperature_c = temperature_c;
    return sample;
}

static inline void run_phase5_e3_monitor_safety_selftest(void)
{
    /* Boot-scoped, single-threaded fixtures use reset static scratch so
     * model/journal copies do not consume the small ESP main task stack. */
    unsigned passed = 0u;
    unsigned total = 0u;

    vg_e3_record("SCOPE_MONITOR_ALERT_EVENT_ONLY",
        vg_monitor_policy_scope_note() != NULL, &passed, &total);
    vg_e3_record("DISCLAIMER_NO_INTERLOCK",
        vg_monitor_policy_interlock_note() != NULL, &passed, &total);
    vg_e3_record("RULE_DISABLED_SUPPORTED",
        vg_monitor_rule_mode_is_supported(VG_POLICY_RULE_DISABLED), &passed, &total);
    vg_e3_record("RULE_ALERT_ONLY_SUPPORTED",
        vg_monitor_rule_mode_is_supported(VG_POLICY_RULE_ALERT_ONLY), &passed, &total);
    vg_e3_record("RULE_BLOCK_REJECTED_NO_INVENTED_INTERLOCK",
        !vg_monitor_rule_mode_is_supported(VG_POLICY_RULE_BLOCK), &passed, &total);

    vg_monitor_policy_config_t config = {
        .bilge_rule_mode = VG_POLICY_RULE_ALERT_ONLY,
        .temperature_rule_mode = VG_POLICY_RULE_ALERT_ONLY,
        .temperature_thresholds = {
            .warning_high_c = 45.0f,
            .alarm_high_c = 60.0f
        }
    };
    vg_e3_record("CONFIG_ALERT_ONLY_VALID",
        vg_monitor_policy_config_is_consistent(&config), &passed, &total);

    vg_monitor_policy_config_t disabled = config;
    disabled.bilge_rule_mode = VG_POLICY_RULE_DISABLED;
    disabled.temperature_rule_mode = VG_POLICY_RULE_DISABLED;
    vg_e3_record("CONFIG_DISABLED_VALID",
        vg_monitor_policy_config_is_consistent(&disabled), &passed, &total);

    vg_monitor_policy_config_t bad_block = config;
    bad_block.bilge_rule_mode = VG_POLICY_RULE_BLOCK;
    vg_e3_record("CONFIG_BILGE_BLOCK_REJECTED",
        !vg_monitor_policy_config_is_consistent(&bad_block), &passed, &total);
    bad_block = config;
    bad_block.temperature_rule_mode = VG_POLICY_RULE_BLOCK;
    vg_e3_record("CONFIG_TEMPERATURE_BLOCK_REJECTED",
        !vg_monitor_policy_config_is_consistent(&bad_block), &passed, &total);

    vg_monitor_policy_config_t bad_threshold = config;
    bad_threshold.temperature_thresholds.warning_high_c = 65.0f;
    bad_threshold.temperature_thresholds.alarm_high_c = 60.0f;
    vg_e3_record("CONFIG_BAD_THRESHOLDS_REJECTED",
        !vg_monitor_policy_config_is_consistent(&bad_threshold), &passed, &total);
    vg_e3_record("CONFIG_NULL_REJECTED",
        !vg_monitor_policy_config_is_consistent(NULL), &passed, &total);

    vg_bilge_sample_t bilge_normal = vg_e3_bilge_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_BILGE_NORMAL, 1u);
    vg_bilge_sample_t bilge_high = vg_e3_bilge_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, VG_BILGE_HIGH, 2u);
    vg_bilge_sample_t bilge_missing = vg_e3_bilge_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_MISSING, VG_BILGE_FAULT, 3u);
    vg_bilge_sample_t bilge_stale = vg_e3_bilge_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_STALE, VG_BILGE_HIGH, 4u);
    vg_e3_record("BILGE_NORMAL_SAMPLE_CONSISTENT",
        vg_bilge_sample_is_consistent(&bilge_normal), &passed, &total);
    vg_e3_record("BILGE_HIGH_SAMPLE_CONSISTENT",
        vg_bilge_sample_is_consistent(&bilge_high), &passed, &total);
    vg_e3_record("BILGE_MISSING_SAMPLE_CONSISTENT",
        vg_bilge_sample_is_consistent(&bilge_missing), &passed, &total);
    vg_e3_record("BILGE_STALE_SAMPLE_CONSISTENT",
        vg_bilge_sample_is_consistent(&bilge_stale), &passed, &total);

    vg_monitor_decision_t decision = {0};
    vg_e3_record("SIM005_NORMAL_EVALUATED",
        vg_monitor_evaluate_bilge(&config, &bilge_normal, &decision), &passed, &total);
    vg_e3_record("SIM005_NORMAL_NO_EVENT",
        !decision.condition_present && !decision.event_requested &&
        decision.reason_code == VG_MONITOR_REASON_NONE, &passed, &total);

    decision = (vg_monitor_decision_t){0};
    vg_e3_record("SIM005_HIGH_EVALUATED",
        vg_monitor_evaluate_bilge(&config, &bilge_high, &decision), &passed, &total);
    vg_e3_record("SIM005_HIGH_ALERT_ONLY",
        decision.condition_present && decision.event_requested &&
        decision.applied_rule_mode == VG_POLICY_RULE_ALERT_ONLY, &passed, &total);
    vg_e3_record("SIM005_HIGH_REASON",
        decision.reason_code == VG_MONITOR_REASON_BILGE_HIGH, &passed, &total);
    vg_e3_record("SIM005_HIGH_SEVERITY",
        decision.severity == VG_MONITOR_SEVERITY_ALARM, &passed, &total);
    vg_e3_record("SIM005_HIGH_PROVENANCE",
        decision.source_mode == VG_SOURCE_SIMULATION &&
        decision.input_quality == VG_QUALITY_VALID, &passed, &total);
    vg_monitor_decision_t bilge_high_decision = decision;

    decision = (vg_monitor_decision_t){0};
    vg_e3_record("BILGE_MISSING_EVALUATED",
        vg_monitor_evaluate_bilge(&config, &bilge_missing, &decision), &passed, &total);
    vg_e3_record("BILGE_MISSING_FAULT_VISIBLE",
        decision.reason_code == VG_MONITOR_REASON_BILGE_NOT_CURRENT &&
        decision.severity == VG_MONITOR_SEVERITY_FAULT, &passed, &total);

    decision = (vg_monitor_decision_t){0};
    vg_e3_record("BILGE_STALE_EVALUATED",
        vg_monitor_evaluate_bilge(&config, &bilge_stale, &decision), &passed, &total);
    vg_e3_record("BILGE_STALE_NOT_CURRENT",
        decision.reason_code == VG_MONITOR_REASON_BILGE_NOT_CURRENT &&
        decision.input_quality == VG_QUALITY_STALE, &passed, &total);

    disabled.bilge_rule_mode = VG_POLICY_RULE_DISABLED;
    decision = (vg_monitor_decision_t){0};
    vg_e3_record("BILGE_DISABLED_EVALUATED",
        vg_monitor_evaluate_bilge(&disabled, &bilge_high, &decision), &passed, &total);
    vg_e3_record("BILGE_DISABLED_SUPPRESSES_EVENT",
        !decision.condition_present && !decision.event_requested, &passed, &total);

    vg_bilge_sample_t bilge_bench = bilge_high;
    bilge_bench.meta.source_mode = VG_SOURCE_BENCH_TEST;
    decision = (vg_monitor_decision_t){0};
    vg_e3_record("BILGE_BENCH_ACCEPTED",
        vg_monitor_evaluate_bilge(&config, &bilge_bench, &decision) &&
        decision.condition_present, &passed, &total);

    vg_bilge_sample_t bilge_physical = bilge_high;
    bilge_physical.meta.source_mode = VG_SOURCE_PHYSICAL;
    vg_e3_record("BILGE_PHYSICAL_REJECTED",
        !vg_monitor_evaluate_bilge(&config, &bilge_physical, &decision), &passed, &total);
    vg_bilge_sample_t bilge_zero_seq = bilge_high;
    bilge_zero_seq.meta.sequence = 0u;
    vg_e3_record("BILGE_ZERO_SEQUENCE_REJECTED",
        !vg_monitor_evaluate_bilge(&config, &bilge_zero_seq, &decision), &passed, &total);
    vg_e3_record("BILGE_NULL_SAMPLE_REJECTED",
        !vg_monitor_evaluate_bilge(&config, NULL, &decision), &passed, &total);
    vg_e3_record("BILGE_NULL_OUTPUT_REJECTED",
        !vg_monitor_evaluate_bilge(&config, &bilge_high, NULL), &passed, &total);

    vg_temperature_sample_t temp_normal = vg_e3_temperature_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 30.0f, 1u);
    vg_temperature_sample_t temp_warning = vg_e3_temperature_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 50.0f, 2u);
    vg_temperature_sample_t temp_alarm = vg_e3_temperature_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_VALID, true, 65.0f, 3u);
    vg_temperature_sample_t temp_stale = vg_e3_temperature_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_STALE, true, 65.0f, 4u);
    vg_temperature_sample_t temp_missing = vg_e3_temperature_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_MISSING, false, 0.0f, 5u);
    vg_temperature_sample_t temp_invalid = vg_e3_temperature_sample(
        VG_SOURCE_SIMULATION, VG_QUALITY_INVALID, false, 0.0f, 6u);

    vg_e3_record("TEMP_NORMAL_SAMPLE_CONSISTENT",
        vg_temperature_sample_is_consistent(&temp_normal), &passed, &total);
    vg_e3_record("TEMP_WARNING_SAMPLE_CONSISTENT",
        vg_temperature_sample_is_consistent(&temp_warning), &passed, &total);
    vg_e3_record("TEMP_ALARM_SAMPLE_CONSISTENT",
        vg_temperature_sample_is_consistent(&temp_alarm), &passed, &total);
    vg_e3_record("TEMP_STALE_SAMPLE_CONSISTENT",
        vg_temperature_sample_is_consistent(&temp_stale), &passed, &total);
    vg_e3_record("TEMP_MISSING_SAMPLE_CONSISTENT",
        vg_temperature_sample_is_consistent(&temp_missing), &passed, &total);
    vg_e3_record("TEMP_INVALID_SAMPLE_CONSISTENT",
        vg_temperature_sample_is_consistent(&temp_invalid), &passed, &total);

    decision = (vg_monitor_decision_t){0};
    vg_e3_record("SIM006_NORMAL_EVALUATED",
        vg_monitor_evaluate_temperature(&config, &temp_normal, &decision), &passed, &total);
    vg_e3_record("SIM006_NORMAL_NO_EVENT",
        !decision.condition_present &&
        decision.reason_code == VG_MONITOR_REASON_NONE, &passed, &total);

    decision = (vg_monitor_decision_t){0};
    vg_e3_record("SIM006_WARNING_EVALUATED",
        vg_monitor_evaluate_temperature(&config, &temp_warning, &decision), &passed, &total);
    vg_e3_record("SIM006_WARNING_REASON",
        decision.reason_code == VG_MONITOR_REASON_TEMPERATURE_WARNING, &passed, &total);
    vg_e3_record("SIM006_WARNING_SEVERITY",
        decision.severity == VG_MONITOR_SEVERITY_WARNING &&
        decision.event_requested, &passed, &total);

    decision = (vg_monitor_decision_t){0};
    vg_e3_record("SIM006_ALARM_EVALUATED",
        vg_monitor_evaluate_temperature(&config, &temp_alarm, &decision), &passed, &total);
    vg_e3_record("SIM006_ALARM_REASON",
        decision.reason_code == VG_MONITOR_REASON_TEMPERATURE_ALARM, &passed, &total);
    vg_e3_record("SIM006_ALARM_SEVERITY",
        decision.severity == VG_MONITOR_SEVERITY_ALARM &&
        decision.event_requested, &passed, &total);
    vg_e3_record("SIM006_ALARM_PROVENANCE",
        decision.source_mode == VG_SOURCE_SIMULATION &&
        decision.input_quality == VG_QUALITY_VALID, &passed, &total);
    vg_monitor_decision_t temp_alarm_decision = decision;

    decision = (vg_monitor_decision_t){0};
    vg_e3_record("TEMP_STALE_EVALUATED",
        vg_monitor_evaluate_temperature(&config, &temp_stale, &decision), &passed, &total);
    vg_e3_record("TEMP_STALE_FAULT_VISIBLE",
        decision.reason_code == VG_MONITOR_REASON_TEMPERATURE_NOT_CURRENT &&
        decision.severity == VG_MONITOR_SEVERITY_FAULT, &passed, &total);
    decision = (vg_monitor_decision_t){0};
    vg_e3_record("TEMP_MISSING_EVALUATED",
        vg_monitor_evaluate_temperature(&config, &temp_missing, &decision), &passed, &total);
    vg_e3_record("TEMP_MISSING_FAULT_VISIBLE",
        decision.reason_code == VG_MONITOR_REASON_TEMPERATURE_NOT_CURRENT &&
        decision.input_quality == VG_QUALITY_MISSING, &passed, &total);
    decision = (vg_monitor_decision_t){0};
    vg_e3_record("TEMP_INVALID_EVALUATED",
        vg_monitor_evaluate_temperature(&config, &temp_invalid, &decision), &passed, &total);
    vg_e3_record("TEMP_INVALID_FAULT_VISIBLE",
        decision.reason_code == VG_MONITOR_REASON_TEMPERATURE_NOT_CURRENT &&
        decision.input_quality == VG_QUALITY_INVALID, &passed, &total);

    disabled.temperature_rule_mode = VG_POLICY_RULE_DISABLED;
    decision = (vg_monitor_decision_t){0};
    vg_e3_record("TEMP_DISABLED_EVALUATED",
        vg_monitor_evaluate_temperature(&disabled, &temp_alarm, &decision), &passed, &total);
    vg_e3_record("TEMP_DISABLED_SUPPRESSES_EVENT",
        !decision.condition_present && !decision.event_requested, &passed, &total);

    vg_temperature_sample_t temp_bench = temp_alarm;
    temp_bench.meta.source_mode = VG_SOURCE_BENCH_TEST;
    decision = (vg_monitor_decision_t){0};
    vg_e3_record("TEMP_BENCH_ACCEPTED",
        vg_monitor_evaluate_temperature(&config, &temp_bench, &decision) &&
        decision.condition_present, &passed, &total);
    vg_temperature_sample_t temp_physical = temp_alarm;
    temp_physical.meta.source_mode = VG_SOURCE_PHYSICAL;
    vg_e3_record("TEMP_PHYSICAL_REJECTED",
        !vg_monitor_evaluate_temperature(&config, &temp_physical, &decision), &passed, &total);
    vg_temperature_sample_t temp_zero_seq = temp_alarm;
    temp_zero_seq.meta.sequence = 0u;
    vg_e3_record("TEMP_ZERO_SEQUENCE_REJECTED",
        !vg_monitor_evaluate_temperature(&config, &temp_zero_seq, &decision), &passed, &total);
    vg_e3_record("TEMP_NULL_SAMPLE_REJECTED",
        !vg_monitor_evaluate_temperature(&config, NULL, &decision), &passed, &total);
    vg_e3_record("TEMP_NULL_OUTPUT_REJECTED",
        !vg_monitor_evaluate_temperature(&config, &temp_alarm, NULL), &passed, &total);

    static vg_safety_monitor_runtime_t runtime;
    memset(&runtime, 0, sizeof(runtime));
    vg_e3_record("RUNTIME_INIT",
        vg_safety_monitor_runtime_init(&runtime), &passed, &total);
    vg_e3_record("RUNTIME_INITIAL_EMPTY",
        runtime.initialized && !runtime.has_alarm &&
        runtime.journal.count == 0u, &passed, &total);
    vg_e3_record("SIM005_RAISE_TRANSACTION",
        vg_safety_monitor_runtime_raise(
            &runtime, &bilge_high_decision, 30u, 2u, 1000u), &passed, &total);
    vg_e3_record("SIM005_ALARM_METADATA",
        runtime.has_alarm && runtime.alarm.id == 1u &&
        runtime.alarm.reason_code == (uint32_t)VG_MONITOR_REASON_BILGE_HIGH &&
        runtime.alarm.state == VG_ALARM_STATE_ACTIVE_UNACK, &passed, &total);
    vg_e3_record("SIM005_EVENT_RAISED",
        runtime.journal.count == 1u &&
        runtime.journal.events[0].type == VG_EVENT_ALARM_RAISED &&
        runtime.journal.events[0].linked_alarm_id == runtime.alarm.id,
        &passed, &total);
    vg_e3_record("SIM005_LOCAL_OUTPUT_ACTIVE",
        runtime.local_output.led_active &&
        runtime.local_output.buzzer_active, &passed, &total);
    vg_e3_record("SIM005_NO_DASHBOARD_INPUT",
        vg_local_alarm_output_is_consistent(&runtime.local_output),
        &passed, &total);
    vg_e3_record("SIM005_ACK_TRANSACTION",
        vg_safety_monitor_runtime_acknowledge(&runtime, 1010u),
        &passed, &total);
    vg_e3_record("SIM005_ACK_DOES_NOT_CLEAR",
        runtime.alarm.state == VG_ALARM_STATE_ACTIVE_ACK &&
        runtime.alarm.condition_active &&
        runtime.local_output.led_active, &passed, &total);
    vg_e3_record("SIM005_CLEAR_TRANSACTION",
        vg_safety_monitor_runtime_clear(&runtime, 1020u),
        &passed, &total);
    vg_e3_record("SIM005_CLEAR_EVENT_RECORDED",
        runtime.journal.count == 3u &&
        runtime.journal.events[2].type == VG_EVENT_ALARM_CLEARED,
        &passed, &total);
    vg_e3_record("SIM005_LOCAL_OUTPUT_OFF_AFTER_CLEAR",
        !runtime.local_output.led_active &&
        !runtime.local_output.buzzer_active, &passed, &total);

    static vg_safety_monitor_runtime_t temp_runtime;
    memset(&temp_runtime, 0, sizeof(temp_runtime));
    vg_e3_record("SIM006_RUNTIME_INIT",
        vg_safety_monitor_runtime_init(&temp_runtime), &passed, &total);
    vg_e3_record("SIM006_RAISE_TRANSACTION",
        vg_safety_monitor_runtime_raise(
            &temp_runtime, &temp_alarm_decision, 40u, 2u, 2000u),
        &passed, &total);
    vg_e3_record("SIM006_EVENT_REASON",
        temp_runtime.alarm.reason_code ==
        (uint32_t)VG_MONITOR_REASON_TEMPERATURE_ALARM &&
        temp_runtime.journal.events[0].type == VG_EVENT_ALARM_RAISED,
        &passed, &total);
    vg_e3_record("SIM006_LOCAL_OUTPUT_ACTIVE",
        temp_runtime.local_output.led_active &&
        temp_runtime.local_output.buzzer_active, &passed, &total);

    static vg_safety_monitor_runtime_t full;
    memset(&full, 0, sizeof(full));
    bool full_ok = vg_safety_monitor_runtime_init(&full);
    for (size_t i = 0u; full_ok && i < VG_JOURNAL_CAPACITY; ++i) {
        uint64_t event_id = 0u;
        full_ok = vg_journal_append(
            &full.journal, 0u, 90u, VG_SOURCE_SIMULATION,
            VG_EVENT_FAULT, (uint64_t)i + 1u, &event_id);
    }
    vg_e3_record("RUNTIME_FULL_JOURNAL_PREP",
        full_ok && full.journal.count == VG_JOURNAL_CAPACITY,
        &passed, &total);
    const uint64_t old_next_id = full.alarm_ids.next_id;
    vg_e3_record("RUNTIME_FULL_JOURNAL_ROLLBACK",
        !vg_safety_monitor_runtime_raise(
            &full, &temp_alarm_decision, 40u, 2u, 20u) &&
        !full.has_alarm && full.alarm_ids.next_id == old_next_id &&
        full.journal.count == VG_JOURNAL_CAPACITY, &passed, &total);

    vg_monitor_decision_t bad_decision = bilge_high_decision;
    bad_decision.applied_rule_mode = VG_POLICY_RULE_BLOCK;
    vg_e3_record("DECISION_BLOCK_MODE_INCONSISTENT",
        !vg_monitor_decision_is_consistent(&bad_decision), &passed, &total);
    bad_decision = bilge_high_decision;
    bad_decision.event_requested = false;
    vg_e3_record("DECISION_CONDITION_WITHOUT_EVENT_REJECTED",
        !vg_monitor_decision_is_consistent(&bad_decision), &passed, &total);
    vg_e3_record("RUNTIME_NULL_INIT_REJECTED",
        !vg_safety_monitor_runtime_init(NULL), &passed, &total);
    vg_e3_record("RUNTIME_NULL_DECISION_REJECTED",
        !vg_safety_monitor_runtime_raise(
            &temp_runtime, NULL, 40u, 2u, 3000u), &passed, &total);
    vg_e3_record("RUNTIME_ZERO_SOURCE_REJECTED",
        !vg_safety_monitor_runtime_raise(
            &(vg_safety_monitor_runtime_t){0},
            &temp_alarm_decision, 0u, 2u, 3000u), &passed, &total);

    vg_e3_record("CASE_COUNT_EXACT",
        total + 1u == VG_E3_EXPECTED_CASES, &passed, &total);

    printf("PHASE5_E3_MONITOR_SAFETY_SELFTEST: %s (%u/%u)\n",
           passed == total ? "PASS" : "FAIL",
           (unsigned)passed,
           (unsigned)total);
}

#endif /* VG_PHASE5_E3_SELFTEST_H */
