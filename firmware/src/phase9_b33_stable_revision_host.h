#ifndef PHASE9_B33_STABLE_REVISION_HOST_H
#define PHASE9_B33_STABLE_REVISION_HOST_H
/* C99 HOST policy: reject revision drift observed across validation. Input
 * copies are taken before probes; no publish result is exposed until the
 * second revision read and source-byte stability checks have passed.
 * A callback is NOT a persistent CAS, an authenticated witness, a mutex,
 * atomic publication for concurrent readers, or ESP32/NVS durability. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b32_input_provenance_host.h"

typedef bool (*vg_b33_revision_probe)(void *context,uint64_t *observed);
static inline bool vg_b33_finalize_stable_revision(
    const vg_b30_pending *pending,
    const vg_b29_cas_receipt *cas,
    const vg_b30_readback_receipt *rr,
    const uint8_t *readback,size_t readback_len,
    uint64_t externally_expected_after_revision,
    vg_b33_revision_probe probe,void *probe_context,
    vg_b26_dual_guard *published_guard,
    vg_b28_fence *published_fence,
    vg_b19_restored *published_state,bool *committed)
{
    if(!pending || !cas || !rr || !readback || !probe || !probe_context ||
       !published_guard || !published_fence || !published_state ||
       !committed || !readback_len || readback_len>VG_B19_SLOT_MAX ||
       !externally_expected_after_revision)return false;
    vg_b31_region inputs[4],outputs[4];
    if(!vg_b31_region_of(pending,sizeof(*pending),&inputs[0]) ||
       !vg_b31_region_of(cas,sizeof(*cas),&inputs[1]) ||
       !vg_b31_region_of(rr,sizeof(*rr),&inputs[2]) ||
       !vg_b31_region_of(readback,readback_len,&inputs[3]) ||
       !vg_b31_region_of(published_guard,sizeof(*published_guard),&outputs[0]) ||
       !vg_b31_region_of(published_fence,sizeof(*published_fence),&outputs[1]) ||
       !vg_b31_region_of(published_state,sizeof(*published_state),&outputs[2]) ||
       !vg_b31_region_of(committed,sizeof(*committed),&outputs[3]))return false;
    for(unsigned i=0u;i<4u;i++){
        for(unsigned j=i+1u;j<4u;j++)
            if(vg_b31_overlaps(inputs[i],inputs[j]))return false;
        for(unsigned j=0u;j<4u;j++)
            if(vg_b31_overlaps(outputs[i],inputs[j]))return false;
        for(unsigned j=i+1u;j<4u;j++)
            if(vg_b31_overlaps(outputs[i],outputs[j]))return false;
    }
    /* Copy controls once. Any mutation from sequential fixture callbacks
     * causes denial; calling code must ensure data-race freedom itself. */
    vg_b30_pending held_pending=*pending;
    vg_b29_cas_receipt held_cas=*cas;
    vg_b30_readback_receipt held_rr=*rr;
    uint8_t held_readback[VG_B19_SLOT_MAX];
    memcpy(held_readback,readback,readback_len);
    uint64_t before=0u,after=0u;
    if(!probe(probe_context,&before) ||
       before!=externally_expected_after_revision)return false;
    if(memcmp(pending,&held_pending,sizeof(held_pending)) ||
       memcmp(cas,&held_cas,sizeof(held_cas)) ||
       memcmp(rr,&held_rr,sizeof(held_rr)) ||
       memcmp(readback,held_readback,readback_len))return false;
    vg_b26_dual_guard candidate_guard;
    vg_b28_fence candidate_fence;
    vg_b19_restored candidate_state;
    bool candidate_committed=false;
    if(!vg_b32_finalize_separated_inputs(&held_pending,&held_cas,&held_rr,
        held_readback,readback_len,externally_expected_after_revision,
        &candidate_guard,&candidate_fence,&candidate_state,
        &candidate_committed) || !candidate_committed)return false;
    if(!probe(probe_context,&after) ||
       after!=before || after!=externally_expected_after_revision)return false;
    if(memcmp(pending,&held_pending,sizeof(held_pending)) ||
       memcmp(cas,&held_cas,sizeof(held_cas)) ||
       memcmp(rr,&held_rr,sizeof(held_rr)) ||
       memcmp(readback,held_readback,readback_len))return false;
    /* Outputs never written on rejection. Four assignments are sequential,
     * NOT a lock-free atomic multi-field publish to concurrent observers. */
    *published_guard=candidate_guard;
    *published_fence=candidate_fence;
    *published_state=candidate_state;
    *committed=true;
    return true;
}
#endif
