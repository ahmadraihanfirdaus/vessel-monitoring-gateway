#ifndef PHASE9_B31_PUBLISH_ISOLATION_HOST_H
#define PHASE9_B31_PUBLISH_ISOLATION_HOST_H
/* HOST C99 publish boundary: prevent writable result buffers from aliasing
 * immutable pending, independently supplied readback, or receipts.
 * This is address-space isolation only; it is NOT memory protection, storage
 * durability, receipt authentication, cryptographic validation or ESP NVS. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "phase9_b30_exact_readback_host.h"

typedef struct { uintptr_t begin; uintptr_t end; } vg_b31_region;

static inline bool vg_b31_region_of(const void *p,size_t len,vg_b31_region *out){
    if(!p || !out || !len || len>UINTPTR_MAX)return false;
    uintptr_t start=(uintptr_t)p;
    if(start>UINTPTR_MAX-(uintptr_t)len)return false;
    out->begin=start;out->end=start+(uintptr_t)len;
    return true;
}
static inline bool vg_b31_overlaps(vg_b31_region a,vg_b31_region b){
    return a.begin<b.end && b.begin<a.end;
}

/* Explicitly reject a caller who supplies its pending image as independent
 * storage readback, or supplies outputs that overlap any inputs or each other.
 * Successful inputs are still validated by the full B30/B29 C99 guards.
 * Denials leave every output and input byte unchanged. */
static inline bool vg_b31_finalize_isolated(
    const vg_b30_pending *pending,
    const vg_b29_cas_receipt *cas,
    const vg_b30_readback_receipt *readback_receipt,
    const uint8_t *readback,size_t readback_len,
    uint64_t externally_verified_after_revision,
    vg_b26_dual_guard *published_guard,
    vg_b28_fence *published_fence,
    vg_b19_restored *published_state,bool *committed)
{
    if(!pending || !cas || !readback_receipt || !readback ||
       !published_guard || !published_fence || !published_state ||
       !committed || !readback_len || readback_len>VG_B19_SLOT_MAX)return false;
    vg_b31_region inputs[4],outputs[4];
    if(!vg_b31_region_of(pending,sizeof(*pending),&inputs[0]) ||
       !vg_b31_region_of(cas,sizeof(*cas),&inputs[1]) ||
       !vg_b31_region_of(readback_receipt,sizeof(*readback_receipt),&inputs[2]) ||
       !vg_b31_region_of(readback,readback_len,&inputs[3]) ||
       !vg_b31_region_of(published_guard,sizeof(*published_guard),&outputs[0]) ||
       !vg_b31_region_of(published_fence,sizeof(*published_fence),&outputs[1]) ||
       !vg_b31_region_of(published_state,sizeof(*published_state),&outputs[2]) ||
       !vg_b31_region_of(committed,sizeof(*committed),&outputs[3]))return false;
    /* The readback and immutable sources must themselves be independent.
     * This does not establish trustworthy origin of the supplied bytes. */
    for(unsigned i=0u;i<3u;i++)
        if(vg_b31_overlaps(inputs[i],inputs[3]))return false;
    for(unsigned i=0u;i<4u;i++){
        for(unsigned j=0u;j<4u;j++)
            if(vg_b31_overlaps(outputs[i],inputs[j]))return false;
        for(unsigned j=i+1u;j<4u;j++)
            if(vg_b31_overlaps(outputs[i],outputs[j]))return false;
    }
    return vg_b30_finalize_exact(pending,cas,readback_receipt,
        readback,readback_len,externally_verified_after_revision,
        published_guard,published_fence,published_state,committed);
}
#endif
