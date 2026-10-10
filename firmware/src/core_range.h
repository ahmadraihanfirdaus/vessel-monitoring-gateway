#ifndef VG_CORE_RANGE_H
#define VG_CORE_RANGE_H

#include <stdbool.h>
#include <stddef.h>
#include <math.h>

#include "core_measurement.h"

/*
 * Integrated Vessel Monitoring & Diagnostic Gateway
 *
 * Configurable numeric measurement range.
 *
 * Development prototype only.
 *
 * This model validates numeric acceptance ranges.
 * It does not define alarm or safety thresholds.
 *
 * No physical sensor limits are assumed.
 * No physical vessel integration is authorized.
 */

/*
 * A zero-initialized range is unconfigured.
 *
 * Every range must be explicitly configured before use.
 * Minimum and maximum bounds are inclusive.
 */

typedef struct {
    bool configured;
    float minimum;
    float maximum;
} vg_measurement_range_t;

/*
 * Read a measurement only when:
 *
 * 1. Measurement metadata is valid.
 * 2. The measurement value is finite.
 * 3. The range configuration exists.
 * 4. The range is explicitly configured.
 * 5. Both boundaries are finite.
 * 6. Minimum is not greater than maximum.
 * 7. The measurement is within the inclusive range.
 *
 * Return false without modifying out_value otherwise.
 *
 * This is not a sensor calibration function,
 * alarm evaluator, or physical safety policy.
 */

static inline bool vg_measurement_try_get_in_range(
    const vg_measurement_t *measurement,
    const vg_measurement_range_t *range,
    float *out_value
)
{
    if (range == NULL || out_value == NULL) {
        return false;
    }

    if (!range->configured) {
        return false;
    }

    if (!isfinite(range->minimum) ||
        !isfinite(range->maximum)) {
        return false;
    }

    if (range->minimum > range->maximum) {
        return false;
    }

    float candidate = 0.0f;

    if (!vg_measurement_try_get_current_value(
            measurement,
            &candidate)) {
        return false;
    }

    if (candidate < range->minimum ||
        candidate > range->maximum) {
        return false;
    }

    *out_value = candidate;
    return true;
}

#endif /* VG_CORE_RANGE_H */
