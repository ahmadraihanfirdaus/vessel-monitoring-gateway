#ifndef VG_CORE_DIAGNOSTICS_H
#define VG_CORE_DIAGNOSTICS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <limits.h>

#include "core_measurement.h"

/* Single-channel health classifier, development-only. Does not measure
 * sensor freshness, generate alarms/events, or authorize physical sources.
 */
typedef enum {
    VG_DIAG_UNKNOWN = 0,
    VG_DIAG_HEALTHY,
    VG_DIAG_FAULT
} vg_diag_health_t;

typedef enum {
    VG_DIAG_REJECTED = 0,
    VG_DIAG_GOOD,
    VG_DIAG_FAULT_STARTED,
    VG_DIAG_FAULT_CONTINUING,
    VG_DIAG_RECOVERED
} vg_diag_result_t;

typedef struct {
    vg_diag_health_t health;
    vg_source_mode_t source_mode;
    vg_data_quality_t last_quality;
    bool has_observation;
    uint64_t last_observed_ms;
    uint32_t consecutive_failures;
} vg_diagnostic_t;

/* Validate provenance, monotonic time, and numeric quality. A FAULT is a
 * health classification, not an approved reason/severity code. The caller
 * must separately derive event and alarm policy from approved conditions.
 */
static inline vg_diag_result_t vg_diagnostic_observe(
    vg_diagnostic_t *d, const vg_measurement_t *m, uint64_t now_ms)
{
    if (d == NULL || m == NULL ||
        (m->source_mode != VG_SOURCE_SIMULATION &&
         m->source_mode != VG_SOURCE_BENCH_TEST) ||
        (d->health != VG_DIAG_UNKNOWN &&
         d->health != VG_DIAG_HEALTHY && d->health != VG_DIAG_FAULT) ||
        (d->has_observation && (now_ms < d->last_observed_ms ||
         d->source_mode != m->source_mode))) {
        return VG_DIAG_REJECTED;
    }
    float value = 0.0f;
    bool valid = vg_measurement_try_get_current_value(m, &value);
    vg_diag_health_t previous = d->health;
    d->health = valid ? VG_DIAG_HEALTHY : VG_DIAG_FAULT;
    d->source_mode = m->source_mode;
    d->last_quality = m->quality;
    d->last_observed_ms = now_ms;
    d->has_observation = true;
    if (valid) {
        d->consecutive_failures = 0;
        return previous == VG_DIAG_FAULT ? VG_DIAG_RECOVERED : VG_DIAG_GOOD;
    }
    if (d->consecutive_failures < UINT32_MAX) ++d->consecutive_failures;
    return previous == VG_DIAG_FAULT ? VG_DIAG_FAULT_CONTINUING : VG_DIAG_FAULT_STARTED;
}

#endif /* VG_CORE_DIAGNOSTICS_H */
