#ifndef VG_CORE_ALARM_H
#define VG_CORE_ALARM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "core_source_mode.h"

/*
 * Development-only local alarm lifecycle model.
 * ALM-001/002 foundation; NOT a certified marine alert system.
 * No GPIO, buzzer, backend, event persistence, or physical integration.
 * The source-mode guard permits SIMULATION and BENCH_TEST only.
 * Caller timestamps MUST share one monotonic time domain within a boot;
 * the physical unit, clock source and UTC conversion are NOT established.
 */
typedef enum {
    VG_ALARM_STATE_UNKNOWN = 0,
    VG_ALARM_STATE_ACTIVE_UNACK = 1,
    VG_ALARM_STATE_ACTIVE_ACK = 2,
    VG_ALARM_STATE_CLEARED = 3
} vg_alarm_state_t;

/* Priority and reason are opaque nonzero codes pending an approved ADR. */
typedef struct {
    /* Unique only for the lifetime of this allocator (one gateway boot). */
    uint64_t next_id;
} vg_alarm_id_allocator_t;

typedef struct {
    uint64_t id;
    uint32_t source_id;
    vg_source_mode_t source_mode;
    uint32_t priority_code;
    uint32_t reason_code;
    vg_alarm_state_t state;
    bool condition_active;
    bool acknowledged;
    uint64_t raised_at;
    uint64_t acknowledged_at;
    uint64_t cleared_at;
    bool has_acknowledged_at;
    bool has_cleared_at;
} vg_alarm_t;

static inline void vg_alarm_id_allocator_init(vg_alarm_id_allocator_t *allocator)
{
    if (allocator != NULL) {
        allocator->next_id = 1;
    }
}

/* Prevent invalid combinations from being treated as usable alarm records. */
static inline bool vg_alarm_is_consistent(const vg_alarm_t *alarm)
{
    if (alarm == NULL || alarm->id == 0 || alarm->source_id == 0 ||
        alarm->priority_code == 0 || alarm->reason_code == 0 ||
        !vg_source_mode_is_known(alarm->source_mode) ||
        alarm->source_mode == VG_SOURCE_PHYSICAL) {
        return false;
    }

    if (alarm->state == VG_ALARM_STATE_ACTIVE_UNACK) {
        return alarm->condition_active && !alarm->acknowledged &&
               !alarm->has_acknowledged_at && !alarm->has_cleared_at;
    }
    if (alarm->state == VG_ALARM_STATE_ACTIVE_ACK) {
        return alarm->condition_active && alarm->acknowledged &&
               alarm->has_acknowledged_at && !alarm->has_cleared_at &&
               alarm->acknowledged_at >= alarm->raised_at;
    }
    if (alarm->state == VG_ALARM_STATE_CLEARED) {
        return !alarm->condition_active && alarm->has_cleared_at &&
               alarm->cleared_at >= alarm->raised_at &&
               alarm->acknowledged == alarm->has_acknowledged_at &&
               (!alarm->acknowledged ||
                (alarm->acknowledged_at >= alarm->raised_at &&
                 alarm->cleared_at >= alarm->acknowledged_at));
    }
    return false;
}

/* Caller supplies an explicitly zero-initialized record and allocator. */
static inline bool vg_alarm_try_raise(
    vg_alarm_id_allocator_t *allocator,
    vg_alarm_t *alarm,
    uint32_t source_id,
    vg_source_mode_t source_mode,
    uint32_t priority_code,
    uint32_t reason_code,
    uint64_t raised_at)
{
    if (allocator == NULL || alarm == NULL || allocator->next_id == 0 ||
        allocator->next_id == UINT64_MAX || alarm->id != 0 ||
        alarm->state != VG_ALARM_STATE_UNKNOWN || alarm->condition_active ||
        alarm->acknowledged || alarm->has_acknowledged_at ||
        alarm->has_cleared_at || source_id == 0 || priority_code == 0 ||
        reason_code == 0 || !vg_source_mode_is_known(source_mode) ||
        source_mode == VG_SOURCE_PHYSICAL) {
        return false;
    }

    vg_alarm_t result = {0};
    result.id = allocator->next_id;
    result.source_id = source_id;
    result.source_mode = source_mode;
    result.priority_code = priority_code;
    result.reason_code = reason_code;
    result.state = VG_ALARM_STATE_ACTIVE_UNACK;
    result.condition_active = true;
    result.raised_at = raised_at;
    *alarm = result;
    allocator->next_id++;
    return true;
}

/* Acknowledge a live condition; NEVER clear the underlying condition. */
static inline bool vg_alarm_try_acknowledge(
    vg_alarm_t *alarm, uint64_t acknowledged_at)
{
    if (!vg_alarm_is_consistent(alarm) ||
        alarm->state != VG_ALARM_STATE_ACTIVE_UNACK ||
        acknowledged_at < alarm->raised_at) {
        return false;
    }
    alarm->state = VG_ALARM_STATE_ACTIVE_ACK;
    alarm->acknowledged = true;
    alarm->has_acknowledged_at = true;
    alarm->acknowledged_at = acknowledged_at;
    return true;
}

/* Only a separate condition evaluator may request this transition. */
static inline bool vg_alarm_try_clear_condition(
    vg_alarm_t *alarm, uint64_t cleared_at)
{
    if (!vg_alarm_is_consistent(alarm) ||
        (alarm->state != VG_ALARM_STATE_ACTIVE_UNACK &&
         alarm->state != VG_ALARM_STATE_ACTIVE_ACK) ||
        cleared_at < alarm->raised_at ||
        (alarm->acknowledged && cleared_at < alarm->acknowledged_at)) {
        return false;
    }
    alarm->state = VG_ALARM_STATE_CLEARED;
    alarm->condition_active = false;
    alarm->has_cleared_at = true;
    alarm->cleared_at = cleared_at;
    return true;
}

#endif /* VG_CORE_ALARM_H */
