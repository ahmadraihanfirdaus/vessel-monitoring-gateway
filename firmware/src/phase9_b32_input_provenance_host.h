#ifndef PHASE9_B32_INPUT_PROVENANCE_HOST_H
#define PHASE9_B32_INPUT_PROVENANCE_HOST_H
/* C99 HOST-ONLY: require all four immutable publication inputs to occupy
 * separate byte ranges. Fail before decoding/dereferencing any input.
 * This is address-space separation, NOT actual provenance, authentication,
 * CAS persistence, ESP memory protection, or power-failure durability. */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "phase9_b31_publish_isolation_host.h"

static inline bool vg_b32_finalize_separated_inputs(
    const vg_b30_pending *pending,
    const vg_b29_cas_receipt *cas,
    const vg_b30_readback_receipt *rr,
    const uint8_t *readback,size_t readback_len,
    uint64_t externally_verified_after_revision,
    vg_b26_dual_guard *published_guard,
    vg_b28_fence *published_fence,
    vg_b19_restored *published_state,bool *committed)
{
    if(!pending || !cas || !rr || !readback || !readback_len ||
       readback_len>VG_B19_SLOT_MAX || !published_guard ||
       !published_fence || !published_state || !committed)return false;
    vg_b31_region sources[4];
    if(!vg_b31_region_of(pending,sizeof(*pending),&sources[0]) ||
       !vg_b31_region_of(cas,sizeof(*cas),&sources[1]) ||
       !vg_b31_region_of(rr,sizeof(*rr),&sources[2]) ||
       !vg_b31_region_of(readback,readback_len,&sources[3]))return false;
    for(unsigned i=0u;i<4u;i++)
        for(unsigned j=i+1u;j<4u;j++)
            if(vg_b31_overlaps(sources[i],sources[j]))return false;
    /* B31 separately verifies every writable output does not overlap
     * any input, or another output; B30 checks exact readback contents. */
    return vg_b31_finalize_isolated(pending,cas,rr,readback,readback_len,
        externally_verified_after_revision,published_guard,
        published_fence,published_state,committed);
}
#endif
