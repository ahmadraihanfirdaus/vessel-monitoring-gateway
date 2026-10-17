#ifndef VG_PHASE5_E4_FORMAL_SCENARIOS_H
#define VG_PHASE5_E4_FORMAL_SCENARIOS_H

#include <stdbool.h>
#include <stdio.h>

#include "provider_door.h"
#include "provider_fuel_vapor.h"
#include "provider_bilge.h"
#include "provider_temperature.h"
#include "safety_policy.h"
#include "safety_policy_runtime.h"
#include "safety_monitor_policy.h"
#include "safety_monitor_runtime.h"

#define VG_E4_FORMAL_SCENARIO_COUNT 6u

static inline void vg_e4_record_scenario(
    const char *scenario_id,
    bool success,
    unsigned *passed,
    unsigned *total)
{
    ++(*total);
    if (success) {
        ++(*passed);
    }
    printf("E4_FORMAL_SCENARIO %s: %s\n",
           scenario_id, success ? "PASS" : "FAIL");
}

static inline bool vg_e4_get_door_step(size_t step, vg_door_sample_t *out)
{
    vg_door_sim_t sim = {0};
    return vg_door_sim_init(&sim, 1000u, 100u) &&
           vg_door_sim_sample_for_step(&sim, step, out);
}

static inline bool vg_e4_get_fuel_step(
    size_t step, vg_fuel_vapor_sample_t *out)
{
    vg_fuel_vapor_sim_t sim = {0};
    return vg_fuel_vapor_sim_init(&sim, 2000u, 100u) &&
           vg_fuel_vapor_sim_sample_for_step(&sim, step, out);
}

static inline bool vg_e4_get_bilge_step(size_t step, vg_bilge_sample_t *out)
{
    vg_bilge_sim_t sim = {0};
    return vg_bilge_sim_init(&sim, 3000u, 100u) &&
           vg_bilge_sim_sample_for_step(&sim, step, out);
}

static inline bool vg_e4_get_temperature_step(
    size_t step, vg_temperature_sample_t *out)
{
    vg_temperature_sim_t sim = {0};
    return vg_temperature_sim_init(&sim, 4000u, 100u) &&
           vg_temperature_sim_sample_for_step(&sim, step, out);
}

static inline vg_prestart_policy_config_t vg_e4_prestart_block_config(void)
{
    const vg_prestart_policy_config_t config = {
        .hatch_rule_mode = VG_POLICY_RULE_BLOCK,
        .fuel_vapor_rule_mode = VG_POLICY_RULE_BLOCK
    };
    return config;
}

static inline vg_monitor_policy_config_t vg_e4_monitor_alert_config(void)
{
    const vg_monitor_policy_config_t config = {
        .bilge_rule_mode = VG_POLICY_RULE_ALERT_ONLY,
        .temperature_rule_mode = VG_POLICY_RULE_ALERT_ONLY,
        .temperature_thresholds = {
            .warning_high_c = 45.0f,
            .alarm_high_c = 60.0f
        }
    };
    return config;
}

/*
 * Dedicated Phase 5 formal simulation-scenario harness for SIM-001..SIM-006.
 *
 * The harness intentionally uses deterministic software provider sequences and
 * the actual Phase 5 policy/runtime contracts. It does not emulate or control
 * a physical starter, ignition, engine, pump, GPIO, vessel network, or certified
 * marine alert device. SIM-005's "during run" wording is exercised through the
 * monitoring path only; it does not create an engine-state or stop interlock.
 */
static inline void run_phase5_e4_formal_scenarios(void)
{
    unsigned passed = 0u;
    unsigned total = 0u;

    const vg_prestart_policy_config_t prestart = vg_e4_prestart_block_config();
    const vg_monitor_policy_config_t monitor = vg_e4_monitor_alert_config();

    /* SIM-001: normal pre-start; hatch open, fuel normal, monitoring inputs valid. */
    vg_door_sample_t door_open = {0};
    vg_fuel_vapor_sample_t fuel_normal = {0};
    vg_bilge_sample_t bilge_normal = {0};
    vg_temperature_sample_t temp_normal = {0};
    vg_prestart_decision_t hatch_decision = {0};
    vg_prestart_decision_t fuel_decision = {0};
    vg_monitor_decision_t bilge_decision = {0};
    vg_monitor_decision_t temp_decision = {0};

    bool sim001 =
        vg_e4_get_door_step(0u, &door_open) &&
        vg_e4_get_fuel_step(0u, &fuel_normal) &&
        vg_e4_get_bilge_step(0u, &bilge_normal) &&
        vg_e4_get_temperature_step(0u, &temp_normal) &&
        door_open.state == VG_DOOR_STATE_OPEN &&
        door_open.meta.quality == VG_QUALITY_VALID &&
        fuel_normal.state == VG_FUEL_VAPOR_NORMAL &&
        fuel_normal.meta.quality == VG_QUALITY_VALID &&
        bilge_normal.state == VG_BILGE_NORMAL &&
        bilge_normal.meta.quality == VG_QUALITY_VALID &&
        temp_normal.meta.quality == VG_QUALITY_VALID &&
        vg_prestart_evaluate_hatch(&prestart, &door_open, &hatch_decision) &&
        vg_prestart_evaluate_fuel_vapor(&prestart, &fuel_normal, &fuel_decision) &&
        vg_monitor_evaluate_bilge(&monitor, &bilge_normal, &bilge_decision) &&
        vg_monitor_evaluate_temperature(&monitor, &temp_normal, &temp_decision) &&
        hatch_decision.start_permitted && !hatch_decision.condition_present &&
        fuel_decision.start_permitted && !fuel_decision.condition_present &&
        !bilge_decision.condition_present && !bilge_decision.event_requested &&
        !temp_decision.condition_present && !temp_decision.event_requested;
    vg_e4_record_scenario("SIM-001", sim001, &passed, &total);

    /* SIM-002: blocking hatch closed. */
    vg_door_sample_t door_closed = {0};
    hatch_decision = (vg_prestart_decision_t){0};
    fuel_decision = (vg_prestart_decision_t){0};
    bool sim002 =
        vg_e4_get_door_step(1u, &door_closed) &&
        door_closed.state == VG_DOOR_STATE_CLOSED &&
        door_closed.meta.quality == VG_QUALITY_VALID &&
        vg_prestart_evaluate_hatch(&prestart, &door_closed, &hatch_decision) &&
        vg_prestart_evaluate_fuel_vapor(&prestart, &fuel_normal, &fuel_decision) &&
        hatch_decision.condition_present &&
        !hatch_decision.start_permitted &&
        hatch_decision.applied_rule_mode == VG_POLICY_RULE_BLOCK &&
        hatch_decision.reason_code == VG_SAFETY_REASON_HATCH_CLOSED &&
        fuel_decision.start_permitted;
    vg_e4_record_scenario("SIM-002", sim002, &passed, &total);

    /* SIM-003: fuel-vapor ALARM blocks virtual start and raises local alarm/event. */
    vg_fuel_vapor_sample_t fuel_alarm = {0};
    fuel_decision = (vg_prestart_decision_t){0};
    vg_safety_policy_runtime_t prestart_runtime = {0};
    bool sim003 =
        vg_e4_get_fuel_step(2u, &fuel_alarm) &&
        fuel_alarm.state == VG_FUEL_VAPOR_ALARM &&
        fuel_alarm.meta.quality == VG_QUALITY_VALID &&
        vg_prestart_evaluate_fuel_vapor(&prestart, &fuel_alarm, &fuel_decision) &&
        fuel_decision.condition_present && !fuel_decision.start_permitted &&
        fuel_decision.reason_code == VG_SAFETY_REASON_FUEL_VAPOR_ALARM &&
        vg_safety_policy_runtime_init(&prestart_runtime) &&
        vg_safety_policy_runtime_raise(
            &prestart_runtime, &fuel_decision, 203u, 1u, 5000u) &&
        prestart_runtime.has_alarm &&
        prestart_runtime.alarm.id != 0u &&
        prestart_runtime.alarm.source_id == 203u &&
        prestart_runtime.alarm.reason_code ==
            (uint32_t)VG_SAFETY_REASON_FUEL_VAPOR_ALARM &&
        prestart_runtime.alarm.state == VG_ALARM_STATE_ACTIVE_UNACK &&
        prestart_runtime.alarm.raised_at == 5000u &&
        prestart_runtime.journal.count == 1u &&
        prestart_runtime.journal.events[0].type == VG_EVENT_ALARM_RAISED &&
        prestart_runtime.journal.events[0].linked_alarm_id ==
            prestart_runtime.alarm.id &&
        prestart_runtime.local_output.led_active &&
        prestart_runtime.local_output.buzzer_active &&
        vg_local_alarm_output_is_consistent(&prestart_runtime.local_output);
    vg_e4_record_scenario("SIM-003", sim003, &passed, &total);

    /* SIM-004: missing fuel-vapor data fails safe and exposes a fault reason/event. */
    vg_fuel_vapor_sample_t fuel_missing = {0};
    fuel_decision = (vg_prestart_decision_t){0};
    vg_safety_policy_runtime_t missing_runtime = {0};
    bool sim004 =
        vg_e4_get_fuel_step(3u, &fuel_missing) &&
        fuel_missing.state == VG_FUEL_VAPOR_FAULT &&
        fuel_missing.meta.quality == VG_QUALITY_MISSING &&
        !fuel_missing.has_value &&
        vg_prestart_evaluate_fuel_vapor(&prestart, &fuel_missing, &fuel_decision) &&
        fuel_decision.condition_present && !fuel_decision.start_permitted &&
        fuel_decision.input_quality == VG_QUALITY_MISSING &&
        fuel_decision.reason_code == VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT &&
        vg_safety_policy_runtime_init(&missing_runtime) &&
        vg_safety_policy_runtime_raise(
            &missing_runtime, &fuel_decision, 204u, 1u, 5100u) &&
        missing_runtime.has_alarm &&
        missing_runtime.alarm.reason_code ==
            (uint32_t)VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT &&
        missing_runtime.journal.count == 1u &&
        missing_runtime.journal.events[0].type == VG_EVENT_ALARM_RAISED &&
        missing_runtime.local_output.led_active &&
        missing_runtime.local_output.buzzer_active;
    vg_e4_record_scenario("SIM-004", sim004, &passed, &total);

    /* SIM-005: high-water monitoring raises alert/event; no BLOCK interlock exists. */
    vg_bilge_sample_t bilge_high = {0};
    bilge_decision = (vg_monitor_decision_t){0};
    vg_safety_monitor_runtime_t bilge_runtime = {0};
    bool sim005 =
        vg_e4_get_bilge_step(1u, &bilge_high) &&
        bilge_high.state == VG_BILGE_HIGH &&
        bilge_high.meta.quality == VG_QUALITY_VALID &&
        vg_monitor_policy_config_is_consistent(&monitor) &&
        !vg_monitor_rule_mode_is_supported(VG_POLICY_RULE_BLOCK) &&
        vg_monitor_evaluate_bilge(&monitor, &bilge_high, &bilge_decision) &&
        bilge_decision.condition_present && bilge_decision.event_requested &&
        bilge_decision.applied_rule_mode == VG_POLICY_RULE_ALERT_ONLY &&
        bilge_decision.reason_code == VG_MONITOR_REASON_BILGE_HIGH &&
        bilge_decision.severity == VG_MONITOR_SEVERITY_ALARM &&
        vg_safety_monitor_runtime_init(&bilge_runtime) &&
        vg_safety_monitor_runtime_raise(
            &bilge_runtime, &bilge_decision, 305u, 1u, 6000u) &&
        bilge_runtime.has_alarm &&
        bilge_runtime.alarm.reason_code ==
            (uint32_t)VG_MONITOR_REASON_BILGE_HIGH &&
        bilge_runtime.journal.count == 1u &&
        bilge_runtime.journal.events[0].type == VG_EVENT_ALARM_RAISED &&
        bilge_runtime.local_output.led_active &&
        bilge_runtime.local_output.buzzer_active;
    vg_e4_record_scenario("SIM-005", sim005, &passed, &total);

    /* SIM-006: high compartment temperature crosses demo alarm threshold. */
    vg_temperature_sample_t temp_alarm = {0};
    temp_decision = (vg_monitor_decision_t){0};
    vg_safety_monitor_runtime_t temp_runtime = {0};
    bool sim006 =
        vg_e4_get_temperature_step(2u, &temp_alarm) &&
        temp_alarm.meta.quality == VG_QUALITY_VALID &&
        temp_alarm.has_value &&
        temp_alarm.temperature_c >= monitor.temperature_thresholds.alarm_high_c &&
        vg_monitor_evaluate_temperature(&monitor, &temp_alarm, &temp_decision) &&
        temp_decision.condition_present && temp_decision.event_requested &&
        temp_decision.applied_rule_mode == VG_POLICY_RULE_ALERT_ONLY &&
        temp_decision.reason_code == VG_MONITOR_REASON_TEMPERATURE_ALARM &&
        temp_decision.severity == VG_MONITOR_SEVERITY_ALARM &&
        vg_safety_monitor_runtime_init(&temp_runtime) &&
        vg_safety_monitor_runtime_raise(
            &temp_runtime, &temp_decision, 406u, 1u, 7000u) &&
        temp_runtime.has_alarm &&
        temp_runtime.alarm.reason_code ==
            (uint32_t)VG_MONITOR_REASON_TEMPERATURE_ALARM &&
        temp_runtime.journal.count == 1u &&
        temp_runtime.journal.events[0].type == VG_EVENT_ALARM_RAISED &&
        temp_runtime.local_output.led_active &&
        temp_runtime.local_output.buzzer_active;
    vg_e4_record_scenario("SIM-006", sim006, &passed, &total);

    const bool count_ok = total == VG_E4_FORMAL_SCENARIO_COUNT;
    const bool all_ok = count_ok && passed == total;
    printf("PHASE5_E4_FORMAL_SCENARIOS: %s (%u/%u)\n",
           all_ok ? "PASS" : "FAIL",
           passed,
           (unsigned)VG_E4_FORMAL_SCENARIO_COUNT);
}

#endif /* VG_PHASE5_E4_FORMAL_SCENARIOS_H */
