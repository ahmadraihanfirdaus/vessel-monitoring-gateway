
#ifndef VG_CORE_QUALITY_H
#define VG_CORE_QUALITY_H

#include <stdbool.h>

#include "core_types.h"

/*
 * Integrated Vessel Monitoring & Diagnostic Gateway
 *
 * Core data-quality validation.
 *
 * TEL-002: Missing or invalid values must not be
 * silently converted into valid numeric readings.
 *
 * This function checks only whether a measurement
 * is eligible for use as a current valid reading.
 * It does not implement telemetry serialization,
 * sensor acquisition, or alarm evaluation.
 */

static inline bool vg_measurement_is_current_valid(
    vg_data_quality_t quality,
    bool has_value
)
{
    return has_value && (quality == VG_QUALITY_VALID);
}

#endif /* VG_CORE_QUALITY_H */