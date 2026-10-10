
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
 * PHYSICAL is reserved for future authorized providers.
 * Its presence does not indicate physical data acquisition.
 */
typedef enum {
    VG_SOURCE_SIMULATION = 0,
    VG_SOURCE_BENCH_TEST,
    VG_SOURCE_PHYSICAL
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