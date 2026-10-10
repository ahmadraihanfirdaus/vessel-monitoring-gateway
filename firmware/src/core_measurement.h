#ifndef VG_CORE_MEASUREMENT_H
#define VG_CORE_MEASUREMENT_H

#include <stdbool.h>
#include <stddef.h>
#include <math.h>

#include "core_types.h"
#include "core_quality.h"
#include "core_source_mode.h"

/*
 * Integrated Vessel Monitoring & Diagnostic Gateway
 *
 * Core numeric measurement model.
 * Development prototype only.
 *
 * SYS-002:
 * Every measurement explicitly carries its source mode.
 *
 * TEL-002 foundation:
 * An invalid, missing, stale, or unknown measurement
 * must not be returned as a current valid value.
 *
 * NaN and positive/negative infinity must not be
 * returned as current valid numeric measurements.
 *
 * Zero-initialization produces:
 * - source_mode = VG_SOURCE_UNKNOWN
 * - quality     = VG_QUALITY_UNKNOWN
 * - has_value   = false
 *
 * The numeric value field must not be interpreted
 * independently from source_mode, quality, and has_value.
 *
 * No physical acquisition is implemented or authorized.
 */

typedef struct {
    vg_source_mode_t source_mode;
    vg_data_quality_t quality;
    bool has_value;
    float value;
} vg_measurement_t;

/*
 * Read a current numeric value only when:
 *
 * 1. Both pointers are non-NULL.
 * 2. The source mode is recognized.
 * 3. The quality is VALID.
 * 4. A value is explicitly present.
 * 5. The numeric value is finite.
 *
 * Return false without modifying out_value otherwise.
 *
 * This function validates metadata consistency and
 * numeric finiteness only.
 *
 * It does not authenticate the claimed source mode,
 * validate sensor-specific ranges, or serialize telemetry.
 */

static inline bool vg_measurement_try_get_current_value(
    const vg_measurement_t *measurement,
    float *out_value
)
{
    if (measurement == NULL || out_value == NULL) {
        return false;
    }

    if (!vg_source_mode_is_known(measurement->source_mode)) {
        return false;
    }

    if (!vg_measurement_is_current_valid(
            measurement->quality,
            measurement->has_value)) {
        return false;
    }

    if (!isfinite(measurement->value)) {
        return false;
    }

    *out_value = measurement->value;
    return true;
}

#endif /* VG_CORE_MEASUREMENT_H */
