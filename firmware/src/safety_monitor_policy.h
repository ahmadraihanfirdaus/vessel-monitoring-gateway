#ifndef VG_SAFETY_MONITOR_POLICY_H
#define VG_SAFETY_MONITOR_POLICY_H

#include <stdbool.h>
#include <stdint.h>

#include "provider_bilge.h"
#include "provider_temperature.h"
#include "safety_policy.h"

/*
 * Phase 5 E3 development-only monitoring policy.
 *
 * SIM-005 and SIM-006 are monitoring scenarios, not authorization for a
 * physical interlock. E3 therefore supports only DISABLED and ALERT_ONLY
 * monitoring actions. VG_POLICY_RULE_BLOCK is deliberately rejected here so
 * a high-water or temperature condition cannot silently become an invented
 * starter/engine-stop interlock.
 *
 * Temperature thresholds are configurable demonstration values only.
 */
typedef enum {
    VG_MONITOR_REASON_NONE = 0,
    VG_MONITOR_REASON_BILGE_HIGH = 3001,
    VG_MONITOR_REASON_BILGE_NOT_CURRENT = 3002,
    VG_MONITOR_REASON_TEMPERATURE_WARNING = 4001,
    VG_MONITOR_REASON_TEMPERATURE_ALARM = 4002,
    VG_MONITOR_REASON_TEMPERATURE_NOT_CURRENT = 4003
} vg_monitor_reason_code_t;

typedef enum {
    VG_MONITOR_SEVERITY_NONE = 0,
    VG_MONITOR_SEVERITY_WARNING = 1,
    VG_MONITOR_SEVERITY_ALARM = 2,
    VG_MONITOR_SEVERITY_FAULT = 3
} vg_monitor_severity_t;

typedef struct {
    vg_policy_rule_mode_t bilge_rule_mode;
    vg_policy_rule_mode_t temperature_rule_mode;
    vg_temperature_demo_thresholds_t temperature_thresholds;
} vg_monitor_policy_config_t;

typedef struct {
    bool evaluated;
    bool condition_present;
    bool event_requested;
    vg_policy_rule_mode_t applied_rule_mode;
    vg_monitor_reason_code_t reason_code;
    vg_monitor_severity_t severity;
    vg_source_mode_t source_mode;
    vg_data_quality_t input_quality;
} vg_monitor_decision_t;

static inline const char *vg_monitor_policy_scope_note(void)
{
    return "development monitoring policy; alert/event only";
}

static inline const char *vg_monitor_policy_interlock_note(void)
{
    return "no physical starter, ignition, engine-stop, pump, or other interlock";
}

static inline bool vg_monitor_rule_mode_is_supported(vg_policy_rule_mode_t mode)
{
    return mode == VG_POLICY_RULE_DISABLED ||
           mode == VG_POLICY_RULE_ALERT_ONLY;
}

static inline bool vg_monitor_policy_config_is_consistent(
    const vg_monitor_policy_config_t *config)
{
    return config != NULL &&
           vg_monitor_rule_mode_is_supported(config->bilge_rule_mode) &&
           vg_monitor_rule_mode_is_supported(config->temperature_rule_mode) &&
           vg_temperature_demo_thresholds_are_consistent(
               &config->temperature_thresholds);
}

static inline bool vg_monitor_reason_is_known(vg_monitor_reason_code_t reason)
{
    return reason == VG_MONITOR_REASON_BILGE_HIGH ||
           reason == VG_MONITOR_REASON_BILGE_NOT_CURRENT ||
           reason == VG_MONITOR_REASON_TEMPERATURE_WARNING ||
           reason == VG_MONITOR_REASON_TEMPERATURE_ALARM ||
           reason == VG_MONITOR_REASON_TEMPERATURE_NOT_CURRENT;
}

static inline bool vg_monitor_severity_is_known(vg_monitor_severity_t severity)
{
    return severity == VG_MONITOR_SEVERITY_NONE ||
           severity == VG_MONITOR_SEVERITY_WARNING ||
           severity == VG_MONITOR_SEVERITY_ALARM ||
           severity == VG_MONITOR_SEVERITY_FAULT;
}

static inline bool vg_monitor_decision_is_consistent(
    const vg_monitor_decision_t *decision)
{
    if (decision == NULL || !decision->evaluated ||
        !vg_monitor_rule_mode_is_supported(decision->applied_rule_mode) ||
        !vg_provider_source_is_phase4_supported(decision->source_mode) ||
        !vg_provider_quality_is_known(decision->input_quality) ||
        !vg_monitor_severity_is_known(decision->severity)) {
        return false;
    }

    if (!decision->condition_present) {
        return !decision->event_requested &&
               decision->reason_code == VG_MONITOR_REASON_NONE &&
               decision->severity == VG_MONITOR_SEVERITY_NONE;
    }

    return decision->applied_rule_mode == VG_POLICY_RULE_ALERT_ONLY &&
           decision->event_requested &&
           vg_monitor_reason_is_known(decision->reason_code) &&
           decision->severity != VG_MONITOR_SEVERITY_NONE;
}

static inline bool vg_monitor_evaluate_bilge(
    const vg_monitor_policy_config_t *config,
    const vg_bilge_sample_t *bilge,
    vg_monitor_decision_t *out)
{
    if (!vg_monitor_policy_config_is_consistent(config) ||
        bilge == NULL || out == NULL ||
        !vg_bilge_sample_is_consistent(bilge)) {
        return false;
    }

    vg_monitor_decision_t decision = {
        .evaluated = true,
        .condition_present = false,
        .event_requested = false,
        .applied_rule_mode = config->bilge_rule_mode,
        .reason_code = VG_MONITOR_REASON_NONE,
        .severity = VG_MONITOR_SEVERITY_NONE,
        .source_mode = bilge->meta.source_mode,
        .input_quality = bilge->meta.quality
    };

    if (config->bilge_rule_mode == VG_POLICY_RULE_DISABLED) {
        *out = decision;
        return vg_monitor_decision_is_consistent(out);
    }

    if (!vg_bilge_sample_is_current(bilge)) {
        decision.condition_present = true;
        decision.event_requested = true;
        decision.reason_code = VG_MONITOR_REASON_BILGE_NOT_CURRENT;
        decision.severity = VG_MONITOR_SEVERITY_FAULT;
    } else if (bilge->state == VG_BILGE_HIGH) {
        decision.condition_present = true;
        decision.event_requested = true;
        decision.reason_code = VG_MONITOR_REASON_BILGE_HIGH;
        decision.severity = VG_MONITOR_SEVERITY_ALARM;
    }

    if (!vg_monitor_decision_is_consistent(&decision)) {
        return false;
    }
    *out = decision;
    return true;
}

static inline bool vg_monitor_evaluate_temperature(
    const vg_monitor_policy_config_t *config,
    const vg_temperature_sample_t *temperature,
    vg_monitor_decision_t *out)
{
    if (!vg_monitor_policy_config_is_consistent(config) ||
        temperature == NULL || out == NULL ||
        !vg_temperature_sample_is_consistent(temperature)) {
        return false;
    }

    vg_monitor_decision_t decision = {
        .evaluated = true,
        .condition_present = false,
        .event_requested = false,
        .applied_rule_mode = config->temperature_rule_mode,
        .reason_code = VG_MONITOR_REASON_NONE,
        .severity = VG_MONITOR_SEVERITY_NONE,
        .source_mode = temperature->meta.source_mode,
        .input_quality = temperature->meta.quality
    };

    if (config->temperature_rule_mode == VG_POLICY_RULE_DISABLED) {
        *out = decision;
        return vg_monitor_decision_is_consistent(out);
    }

    const vg_temperature_demo_result_t result =
        vg_temperature_demo_evaluate(
            temperature, &config->temperature_thresholds);

    if (result == VG_TEMPERATURE_DEMO_REJECTED) {
        return false;
    }
    if (result == VG_TEMPERATURE_DEMO_NOT_CURRENT) {
        decision.condition_present = true;
        decision.event_requested = true;
        decision.reason_code = VG_MONITOR_REASON_TEMPERATURE_NOT_CURRENT;
        decision.severity = VG_MONITOR_SEVERITY_FAULT;
    } else if (result == VG_TEMPERATURE_DEMO_WARNING) {
        decision.condition_present = true;
        decision.event_requested = true;
        decision.reason_code = VG_MONITOR_REASON_TEMPERATURE_WARNING;
        decision.severity = VG_MONITOR_SEVERITY_WARNING;
    } else if (result == VG_TEMPERATURE_DEMO_ALARM) {
        decision.condition_present = true;
        decision.event_requested = true;
        decision.reason_code = VG_MONITOR_REASON_TEMPERATURE_ALARM;
        decision.severity = VG_MONITOR_SEVERITY_ALARM;
    }

    if (!vg_monitor_decision_is_consistent(&decision)) {
        return false;
    }
    *out = decision;
    return true;
}

#endif /* VG_SAFETY_MONITOR_POLICY_H */
