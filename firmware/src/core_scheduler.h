#ifndef VG_CORE_SCHEDULER_H
#define VG_CORE_SCHEDULER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Pure, cooperative due-time arithmetic; NOT a running sampling loop.
 * Time is caller-provided monotonic milliseconds within ONE boot.
 * No RTOS task, timer hardware, callback, delay, or network dependency.
 */
typedef enum {
    VG_SCHED_INVALID = 0,
    VG_SCHED_WAIT,
    VG_SCHED_DUE,
    VG_SCHED_TIME_REGRESSION,
    VG_SCHED_EXHAUSTED
} vg_schedule_result_t;

typedef struct {
    bool initialized;
    bool exhausted;
    bool has_last_now;
    uint64_t interval_ms;
    uint64_t next_due_ms;
    uint64_t last_now_ms;
} vg_scheduler_t;

static inline bool vg_scheduler_init(vg_scheduler_t *s,
                                     uint64_t interval_ms,
                                     uint64_t first_due_ms)
{
    if (s == NULL || interval_ms == 0) return false;
    *s = (vg_scheduler_t){0};
    s->initialized = true;
    s->interval_ms = interval_ms;
    s->next_due_ms = first_due_ms;
    return true;
}

/* skipped_periods counts due intervals MISSED after the one delivered.
 * Reject backwards time without mutating state; avoid overflow.
 * Returns DUE once even when the next deadline cannot be represented;
 * following polls then return EXHAUSTED and require reinitialization.
 */
static inline vg_schedule_result_t vg_scheduler_poll(
    vg_scheduler_t *s, uint64_t now_ms, uint64_t *skipped_periods)
{
    if (s == NULL || skipped_periods == NULL || !s->initialized ||
        s->interval_ms == 0) return VG_SCHED_INVALID;
    if (s->has_last_now && now_ms < s->last_now_ms)
        return VG_SCHED_TIME_REGRESSION;
    if (s->exhausted) return VG_SCHED_EXHAUSTED;
    s->has_last_now = true;
    s->last_now_ms = now_ms;
    if (now_ms < s->next_due_ms) {
        *skipped_periods = 0;
        return VG_SCHED_WAIT;
    }
    uint64_t skipped = (now_ms - s->next_due_ms) / s->interval_ms;
    *skipped_periods = skipped;
    if (skipped == UINT64_MAX ||
        skipped + 1 > (UINT64_MAX - s->next_due_ms) / s->interval_ms) {
        s->exhausted = true;
        return VG_SCHED_DUE;
    }
    s->next_due_ms += (skipped + 1) * s->interval_ms;
    return VG_SCHED_DUE;
}

#endif /* VG_CORE_SCHEDULER_H */
