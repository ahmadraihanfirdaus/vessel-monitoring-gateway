#ifndef VG_SAFETY_POLICY_H
#define VG_SAFETY_POLICY_H

#include <stdbool.h>
#include <stdint.h>

#include "provider_door.h"
#include "provider_fuel_vapor.h"

/*
 * Phase 5 development-only pre-start safety policy foundation.
 *
 * E1 introduced hatch/door policy evaluation. E2 extends the same explicit,
 * configuration-driven contract to the fuel-vapor provider for SIM-003 and
 * SIM-004 preparation. Results remain virtual decisions only: no starter,
 * ignition, GPIO, relay, certified vessel rule, calibrated fuel-vapor limit,
 * or field-verified operating interlock is implemented here.
 */

typedef enum {
    VG_POLICY_RULE_DISABLED = 0,
    VG_POLICY_RULE_ALERT_ONLY = 1,
    VG_POLICY_RULE_BLOCK = 2
} vg_policy_rule_mode_t;

typedef enum {
    VG_SAFETY_REASON_NONE = 0,
    VG_SAFETY_REASON_HATCH_CLOSED = 1001,
    VG_SAFETY_REASON_HATCH_NOT_CURRENT = 1002,
    VG_SAFETY_REASON_FUEL_VAPOR_ALARM = 2001,
    VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT = 2002
} vg_safety_reason_code_t;

typedef struct {
    vg_policy_rule_mode_t hatch_rule_mode;
    vg_policy_rule_mode_t fuel_vapor_rule_mode;
} vg_prestart_policy_config_t;

typedef struct {
    bool evaluated;
    bool start_permitted;
    bool condition_present;
    vg_policy_rule_mode_t applied_rule_mode;
    vg_safety_reason_code_t reason_code;
    vg_source_mode_t source_mode;
    vg_data_quality_t input_quality;
} vg_prestart_decision_t;

static inline const char *vg_safety_policy_scope_note(void)
{
    return "virtual pre-start demonstration policy only";
}

static inline const char *vg_safety_policy_hazard_note(void)
{
    return "not a physical starter interlock or certified vessel safety rule";
}

static inline bool vg_policy_rule_mode_is_known(vg_policy_rule_mode_t mode)
{
    return mode == VG_POLICY_RULE_DISABLED ||
           mode == VG_POLICY_RULE_ALERT_ONLY ||
           mode == VG_POLICY_RULE_BLOCK;
}

static inline bool vg_prestart_policy_config_is_consistent(
    const vg_prestart_policy_config_t *config)
{
    return config != NULL &&
           vg_policy_rule_mode_is_known(config->hatch_rule_mode) &&
           vg_policy_rule_mode_is_known(config->fuel_vapor_rule_mode);
}

static inline bool vg_safety_reason_is_hatch(vg_safety_reason_code_t reason)
{
    return reason == VG_SAFETY_REASON_HATCH_CLOSED ||
           reason == VG_SAFETY_REASON_HATCH_NOT_CURRENT;
}

static inline bool vg_safety_reason_is_fuel_vapor(vg_safety_reason_code_t reason)
{
    return reason == VG_SAFETY_REASON_FUEL_VAPOR_ALARM ||
           reason == VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT;
}

static inline bool vg_safety_reason_is_known_condition(
    vg_safety_reason_code_t reason)
{
    return vg_safety_reason_is_hatch(reason) ||
           vg_safety_reason_is_fuel_vapor(reason);
}

static inline bool vg_prestart_decision_is_consistent(
    const vg_prestart_decision_t *decision)
{
    if (decision == NULL || !decision->evaluated ||
        !vg_policy_rule_mode_is_known(decision->applied_rule_mode) ||
        !vg_provider_source_is_phase4_supported(decision->source_mode) ||
        !vg_provider_quality_is_known(decision->input_quality)) {
        return false;
    }

    if (!decision->condition_present) {
        return decision->start_permitted &&
               decision->reason_code == VG_SAFETY_REASON_NONE;
    }

    if (!vg_safety_reason_is_known_condition(decision->reason_code)) {
        return false;
    }

    if (decision->applied_rule_mode == VG_POLICY_RULE_BLOCK) {
        return !decision->start_permitted;
    }

    if (decision->applied_rule_mode == VG_POLICY_RULE_ALERT_ONLY) {
        return decision->start_permitted;
    }

    /* Disabled rules must not surface a condition. */
    return false;
}

static inline bool vg_prestart_evaluate_hatch(
    const vg_prestart_policy_config_t *config,
    const vg_door_sample_t *door,
    vg_prestart_decision_t *out)
{
    if (!vg_prestart_policy_config_is_consistent(config) ||
        door == NULL || out == NULL ||
        !vg_door_sample_is_consistent(door)) {
        return false;
    }

    vg_prestart_decision_t decision = {
        .evaluated = true,
        .start_permitted = true,
        .condition_present = false,
        .applied_rule_mode = config->hatch_rule_mode,
        .reason_code = VG_SAFETY_REASON_NONE,
        .source_mode = door->meta.source_mode,
        .input_quality = door->meta.quality
    };

    if (config->hatch_rule_mode == VG_POLICY_RULE_DISABLED) {
        if (!vg_prestart_decision_is_consistent(&decision)) {
            return false;
        }
        *out = decision;
        return true;
    }

    if (!vg_door_sample_is_current(door)) {
        decision.condition_present = true;
        decision.reason_code = VG_SAFETY_REASON_HATCH_NOT_CURRENT;
    } else if (door->state == VG_DOOR_STATE_CLOSED) {
        decision.condition_present = true;
        decision.reason_code = VG_SAFETY_REASON_HATCH_CLOSED;
    }

    if (decision.condition_present &&
        config->hatch_rule_mode == VG_POLICY_RULE_BLOCK) {
        decision.start_permitted = false;
    }

    if (!vg_prestart_decision_is_consistent(&decision)) {
        return false;
    }

    *out = decision;
    return true;
}

static inline bool vg_prestart_evaluate_fuel_vapor(
    const vg_prestart_policy_config_t *config,
    const vg_fuel_vapor_sample_t *fuel_vapor,
    vg_prestart_decision_t *out)
{
    if (!vg_prestart_policy_config_is_consistent(config) ||
        fuel_vapor == NULL || out == NULL ||
        !vg_fuel_vapor_sample_is_consistent(fuel_vapor)) {
        return false;
    }

    vg_prestart_decision_t decision = {
        .evaluated = true,
        .start_permitted = true,
        .condition_present = false,
        .applied_rule_mode = config->fuel_vapor_rule_mode,
        .reason_code = VG_SAFETY_REASON_NONE,
        .source_mode = fuel_vapor->meta.source_mode,
        .input_quality = fuel_vapor->meta.quality
    };

    if (config->fuel_vapor_rule_mode == VG_POLICY_RULE_DISABLED) {
        if (!vg_prestart_decision_is_consistent(&decision)) {
            return false;
        }
        *out = decision;
        return true;
    }

    /* Any non-current fuel-vapor sample is fail-safe, never NORMAL/safe. */
    if (!vg_fuel_vapor_sample_is_current(fuel_vapor)) {
        decision.condition_present = true;
        decision.reason_code = VG_SAFETY_REASON_FUEL_VAPOR_NOT_CURRENT;
    } else if (fuel_vapor->state == VG_FUEL_VAPOR_ALARM) {
        decision.condition_present = true;
        decision.reason_code = VG_SAFETY_REASON_FUEL_VAPOR_ALARM;
    }

    if (decision.condition_present &&
        config->fuel_vapor_rule_mode == VG_POLICY_RULE_BLOCK) {
        decision.start_permitted = false;
    }

    if (!vg_prestart_decision_is_consistent(&decision)) {
        return false;
    }

    *out = decision;
    return true;
}

#endif /* VG_SAFETY_POLICY_H */
