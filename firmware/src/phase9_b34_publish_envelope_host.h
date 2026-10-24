#ifndef PHASE9_B34_PUBLISH_ENVELOPE_HOST_H
#define PHASE9_B34_PUBLISH_ENVELOPE_HOST_H
/* HOST ONLY: single result envelope composed from B33 guarded finalization.
 * No hardware durability, trusted CAS, cryptographic authentication, thread
 * safety, lock-free atomics, or direct firmware runtime wiring is provided.
 * Caller controls and serializes revision probe and destination lifetime. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "phase9_b33_stable_revision_host.h"
#define VG_B34_ENVELOPE_VERSION 1u
#define VG_B34_ENVELOPE_VALID 0xB340C0DEu
typedef struct {
    uint32_t version;
    uint32_t valid_marker;
    uint32_t checkpoint_generation;
    uint32_t last_accepted_sequence;
    uint32_t checkpoint_crc32; /* corruption detector only, NOT a MAC */
    uint64_t externally_confirmed_revision;
    vg_b26_dual_guard guard;
    vg_b28_fence fence;
    vg_b19_restored state;
} vg_b34_envelope;
static inline bool vg_b34_finalize_envelope(
    const vg_b30_pending *pending,
    const vg_b29_cas_receipt *cas,
    const vg_b30_readback_receipt *rr,
    const uint8_t *readback,size_t readback_len,
    uint64_t externally_expected_after_revision,
    vg_b33_revision_probe probe,void *probe_context,
    vg_b34_envelope *published)
{
    if(!pending || !cas || !rr || !readback || !probe || !probe_context ||
       !published || !readback_len || readback_len>VG_B19_SLOT_MAX ||
       !externally_expected_after_revision)return false;
    vg_b31_region inputs[4],target;
    if(!vg_b31_region_of(pending,sizeof(*pending),&inputs[0]) ||
       !vg_b31_region_of(cas,sizeof(*cas),&inputs[1]) ||
       !vg_b31_region_of(rr,sizeof(*rr),&inputs[2]) ||
       !vg_b31_region_of(readback,readback_len,&inputs[3]) ||
       !vg_b31_region_of(published,sizeof(*published),&target))return false;
    for(unsigned i=0u;i<4u;i++){
        if(vg_b31_overlaps(target,inputs[i]))return false;
        for(unsigned j=i+1u;j<4u;j++)
            if(vg_b31_overlaps(inputs[i],inputs[j]))return false;
    }
    /* Construct in private scratch. No write to caller's envelope on reject. */
    vg_b34_envelope candidate={0};
    bool committed=false;
    if(!vg_b33_finalize_stable_revision(pending,cas,rr,readback,readback_len,
          externally_expected_after_revision,probe,probe_context,
          &candidate.guard,&candidate.fence,&candidate.state,&committed) ||
       !committed)return false;
    if(candidate.fence.revision!=externally_expected_after_revision ||
       candidate.state.generation!=pending->base.next_state.generation ||
       candidate.state.ack.last_accepted_sequence!=
          pending->base.next_state.ack.last_accepted_sequence ||
       candidate.state.ack.last_accepted_sequence!=
          candidate.guard.primary.last_witness.confirmed_ack ||
       pending->image_len!=readback_len)return false;
    candidate.version=VG_B34_ENVELOPE_VERSION;
    candidate.checkpoint_generation=candidate.state.generation;
    candidate.last_accepted_sequence=candidate.state.ack.last_accepted_sequence;
    candidate.checkpoint_crc32=vg_b18_crc32(readback,readback_len);
    candidate.externally_confirmed_revision=candidate.fence.revision;
    candidate.valid_marker=VG_B34_ENVELOPE_VALID;
    /* Single struct assignment simplifies sequential consumers; it is NOT an
     * atomic publication for concurrent readers, CPUs or power loss. */
    *published=candidate;
    return true;
}
#endif
