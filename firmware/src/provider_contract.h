#ifndef VG_PROVIDER_CONTRACT_H
#define VG_PROVIDER_CONTRACT_H

#include <stdbool.h>
#include <stdint.h>

#include "core_types.h"

/*
 * Integrated Vessel Monitoring & Diagnostic Gateway
 * Phase 4 provider contract foundation.
 *
 * Development prototype only.
 *
 * This contract is limited to software simulation and controlled bench-test
 * provenance. VG_SOURCE_PHYSICAL remains recognized by the global source-mode
 * model but is deliberately rejected here because no authorized physical
 * provider exists in Phase 4.
 *
 * A provider sample carries explicit source, quality, monotonic sample time,
 * and a non-zero per-provider sequence number. No wall-clock/RTC meaning is
 * implied by sampled_at_ms.
 */

typedef struct {
    vg_source_mode_t source_mode;
    vg_data_quality_t quality;
    uint64_t sampled_at_ms;
    uint32_t sequence;
} vg_provider_meta_t;

static inline bool vg_provider_source_is_phase4_supported(
    vg_source_mode_t source_mode
)
{
    return source_mode == VG_SOURCE_SIMULATION ||
           source_mode == VG_SOURCE_BENCH_TEST;
}

static inline bool vg_provider_quality_is_known(
    vg_data_quality_t quality
)
{
    switch (quality) {
        case VG_QUALITY_UNKNOWN:
        case VG_QUALITY_VALID:
        case VG_QUALITY_INVALID:
        case VG_QUALITY_MISSING:
        case VG_QUALITY_STALE:
            return true;

        default:
            return false;
    }
}

static inline bool vg_provider_meta_is_consistent(
    const vg_provider_meta_t *meta
)
{
    if (meta == NULL) {
        return false;
    }

    if (!vg_provider_source_is_phase4_supported(meta->source_mode)) {
        return false;
    }

    if (!vg_provider_quality_is_known(meta->quality)) {
        return false;
    }

    if (meta->sequence == 0u) {
        return false;
    }

    return true;
}

static inline bool vg_provider_meta_init(
    vg_provider_meta_t *out,
    vg_source_mode_t source_mode,
    vg_data_quality_t quality,
    uint64_t sampled_at_ms,
    uint32_t sequence
)
{
    if (out == NULL) {
        return false;
    }

    vg_provider_meta_t candidate = {
        .source_mode = source_mode,
        .quality = quality,
        .sampled_at_ms = sampled_at_ms,
        .sequence = sequence
    };

    if (!vg_provider_meta_is_consistent(&candidate)) {
        return false;
    }

    *out = candidate;
    return true;
}

#endif /* VG_PROVIDER_CONTRACT_H */
