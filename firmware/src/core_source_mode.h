
#ifndef VG_CORE_SOURCE_MODE_H
#define VG_CORE_SOURCE_MODE_H

#include <stdbool.h>
#include <stddef.h>

#include "core_types.h"

/*
 * Integrated Vessel Monitoring & Diagnostic Gateway
 *
 * SYS-002: Source mode identification.
 *
 * Recognizing the PHYSICAL label does not authorize
 * physical sensor acquisition or vessel integration.
 *
 * This module only maps and validates source labels.
 * It does not enforce complete data provenance.
 */

static inline const char *vg_source_mode_to_string(
    vg_source_mode_t mode
)
{
    switch (mode) {
        case VG_SOURCE_SIMULATION:
            return "simulation";

        case VG_SOURCE_BENCH_TEST:
            return "bench_test";

        case VG_SOURCE_PHYSICAL:
            return "physical";

        default:
            return NULL;
    }
}

static inline bool vg_source_mode_is_known(
    vg_source_mode_t mode
)
{
    return vg_source_mode_to_string(mode) != NULL;
}

#endif /* VG_CORE_SOURCE_MODE_H */
