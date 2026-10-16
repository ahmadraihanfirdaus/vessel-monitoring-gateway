#ifndef VG_SAFETY_LOCAL_ALARM_H
#define VG_SAFETY_LOCAL_ALARM_H

#include <stdbool.h>
#include <stdint.h>

#include "core_alarm.h"

/*
 * Phase 5 E2 logical local-alarm output model.
 *
 * This is deliberately not a GPIO/buzzer/LED driver. It models the local
 * indication request derived from a local alarm record and has no dashboard,
 * backend, or network input. That separation is development evidence for the
 * local-path architecture only; ALM-003 formal verification remains pending.
 */
typedef struct {
    bool evaluated;
    bool led_active;
    bool buzzer_active;
    uint64_t linked_alarm_id;
    uint32_t reason_code;
    vg_source_mode_t source_mode;
} vg_local_alarm_output_t;

static inline const char *vg_local_alarm_scope_note(void)
{
    return "logical local LED/buzzer request only; no physical output driver";
}

static inline bool vg_local_alarm_output_is_consistent(
    const vg_local_alarm_output_t *out)
{
    if (out == NULL || !out->evaluated || out->linked_alarm_id == 0u ||
        out->reason_code == 0u ||
        (out->source_mode != VG_SOURCE_SIMULATION &&
         out->source_mode != VG_SOURCE_BENCH_TEST)) {
        return false;
    }
    return out->led_active == out->buzzer_active;
}

static inline bool vg_local_alarm_from_alarm(
    const vg_alarm_t *alarm,
    vg_local_alarm_output_t *out)
{
    if (alarm == NULL || out == NULL || !vg_alarm_is_consistent(alarm)) {
        return false;
    }

    const bool active = alarm->state == VG_ALARM_STATE_ACTIVE_UNACK ||
                        alarm->state == VG_ALARM_STATE_ACTIVE_ACK;

    vg_local_alarm_output_t next = {
        .evaluated = true,
        .led_active = active,
        .buzzer_active = active,
        .linked_alarm_id = alarm->id,
        .reason_code = alarm->reason_code,
        .source_mode = alarm->source_mode
    };

    if (!vg_local_alarm_output_is_consistent(&next)) {
        return false;
    }
    *out = next;
    return true;
}

#endif /* VG_SAFETY_LOCAL_ALARM_H */
