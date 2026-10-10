
#ifndef VG_CORE_TYPES_H
#define VG_CORE_TYPES_H

/*
 * Integrated Vessel Monitoring & Diagnostic Gateway
 * Firmware core data types.
 *
 * Development prototype only.
 * No physical vessel integration is authorized.
 */

/*
 * SYS-002: Identify the provenance of monitoring data.
 *
 * UNKNOWN is zero so a zero-initialized field does not
 * falsely identify unassigned data as simulation data.
 *
 * PHYSICAL is reserved for future authorized providers.
 * Its presence does not indicate physical acquisition.
 *
 * Enum numeric values are internal firmware values,
 * not an approved telemetry wire-format contract.
 */
typedef enum {
    VG_SOURCE_UNKNOWN = 0,
    VG_SOURCE_SIMULATION = 1,
    VG_SOURCE_BENCH_TEST = 2,
    VG_SOURCE_PHYSICAL = 3
} vg_source_mode_t;

/*
 * Data quality foundation.
 *
 * UNKNOWN is zero to ensure a zero-initialized quality
 * field is never interpreted as VALID.
 *
 * Invalid or missing measurements must not be treated
 * as valid numeric zero.
 */
typedef enum {
    VG_QUALITY_UNKNOWN = 0,
    VG_QUALITY_VALID,
    VG_QUALITY_INVALID,
    VG_QUALITY_MISSING,
    VG_QUALITY_STALE
} vg_data_quality_t;

#endif /* VG_CORE_TYPES_H */
