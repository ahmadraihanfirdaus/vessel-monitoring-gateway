#ifndef PHASE9_B30_EXACT_READBACK_HOST_H
#define PHASE9_B30_EXACT_READBACK_HOST_H
/* HOST-ONLY immutable checkpoint content binding. This compares exact bytes
 * and decodes a canonical image. It does NOT authenticate a caller-supplied
 * receipt, perform storage CAS, provide persistent atomicity or use ESP32 NVS.
 * Trusted readback and receipt must be supplied by an independent adapter. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b29_publish_barrier_host.h"

typedef struct {
    bool ready;
    unsigned slot_index;
    size_t image_len;
    uint8_t image[VG_B19_SLOT_MAX];
    vg_b29_pending base;
} vg_b30_pending;

typedef struct {
    bool external_readback_verified; /* NOT validated or issued by this code */
    uint32_t device_tag;
    unsigned slot_index;
    uint64_t revision;
    size_t image_len;
    uint32_t image_crc32; /* integrity metadata, NOT authentication */
} vg_b30_readback_receipt;

/* Re-serialize reconstructed checkpoint to ensure journal and telemetry bytes,
 * not merely generation/ACK metadata, remain the same as the candidate.
 * Only canonical images are accepted. */
static inline bool vg_b30_canonical_state(const vg_b29_pending *base,
    const uint8_t *candidate, size_t candidate_len)
{
    if(!base || !candidate || !base->ready || !base->device_tag ||
       candidate_len<VG_B19_SLOT_OVERHEAD+27u ||
       candidate_len>VG_B19_SLOT_MAX ||
       base->next_state.ack.pending || base->next_state.ack.pending_sequence ||
       base->next_state.ack.pending_correlation)return false;
    uint8_t encoded[VG_B19_SLOT_MAX];size_t n=0u;
    if(!vg_b19_wrap(&base->next_state.store,&base->next_state.ack,
        base->device_tag,base->next_state.generation,
        encoded,sizeof(encoded),&n))return false;
    return n==candidate_len && memcmp(encoded,candidate,n)==0;
}

static inline bool vg_b30_prepare_exact(
    const vg_b20_slot before[2],const vg_b20_slot middle[2],
    const vg_b20_slot after[2],uint32_t tag,
    uint32_t primary_domain,uint32_t secondary_domain,
    const vg_b26_dual_guard *guard,const vg_b28_fence *fence,
    uint64_t externally_verified_before_revision,
    const vg_b24_ticket tickets[2],
    const uint8_t *const expected[2],const size_t sizes[2],
    const vg_b27_votes votes[2],vg_b30_pending *pending)
{
    if(!before || !middle || !after || !pending)return false;
    vg_b29_pending proposed;
    if(!vg_b29_prepare(before,middle,after,tag,primary_domain,
        secondary_domain,guard,fence,externally_verified_before_revision,
        tickets,expected,sizes,votes,&proposed))return false;
    unsigned found=2u;
    for(unsigned i=0u;i<2u;i++){
        vg_b19_restored decoded;
        if(after[i].len>VG_B19_SLOT_MAX ||
           !vg_b19_decode(after[i].bytes,after[i].len,tag,&decoded))continue;
        if(decoded.generation==proposed.next_state.generation &&
           decoded.ack.last_accepted_sequence==
             proposed.next_state.ack.last_accepted_sequence &&
           vg_b30_canonical_state(&proposed,after[i].bytes,after[i].len)){
            if(found!=2u)return false; /* ambiguously duplicated candidate */
            found=i;
        }
    }
    if(found==2u)return false;
    vg_b30_pending tmp={0};
    tmp.ready=true;tmp.base=proposed;tmp.slot_index=found;
    tmp.image_len=after[found].len;
    memcpy(tmp.image,after[found].bytes,tmp.image_len);
    *pending=tmp;return true;
}

/* External adapter must authenticate BOTH receipt sources independently,
 * verify stored revision, and supply real readback from selected slot.
 * On all denials, every caller output remains byte-for-byte unchanged. */
static inline bool vg_b30_finalize_exact(
    const vg_b30_pending *pending,
    const vg_b29_cas_receipt *cas,
    const vg_b30_readback_receipt *readback_receipt,
    const uint8_t *readback,size_t readback_len,
    uint64_t externally_verified_after_revision,
    vg_b26_dual_guard *published_guard,
    vg_b28_fence *published_fence,
    vg_b19_restored *published_state,bool *committed)
{
    if(!pending || !pending->ready || !cas || !readback_receipt ||
       !readback || !published_guard || !published_fence ||
       !published_state || !committed ||
       !readback_receipt->external_readback_verified ||
       pending->slot_index>=2u ||
       pending->image_len<VG_B19_SLOT_OVERHEAD+27u ||
       pending->image_len>VG_B19_SLOT_MAX ||
       readback_len!=pending->image_len ||
       readback_receipt->image_len!=pending->image_len ||
       readback_receipt->slot_index!=pending->slot_index ||
       readback_receipt->device_tag!=pending->base.device_tag ||
       readback_receipt->revision!=pending->base.next_fence.revision ||
       readback_receipt->image_crc32!=
           vg_b18_crc32(pending->image,pending->image_len) ||
       memcmp(readback,pending->image,readback_len)!=0 ||
       !vg_b30_canonical_state(&pending->base,pending->image,
                               pending->image_len))return false;
    vg_b19_restored restored;
    if(!vg_b19_decode(readback,readback_len,pending->base.device_tag,
                      &restored) ||
       restored.generation!=pending->base.next_state.generation ||
       restored.ack.last_accepted_sequence!=
          pending->base.next_state.ack.last_accepted_sequence ||
       restored.ack.pending || restored.ack.pending_sequence ||
       restored.ack.pending_correlation)return false;
    vg_b26_dual_guard tmp_guard;vg_b28_fence tmp_fence;
    vg_b19_restored tmp_state;bool tmp_committed=false;
    if(!vg_b29_finalize(&pending->base,cas,
        externally_verified_after_revision,&tmp_guard,&tmp_fence,
        &tmp_state,&tmp_committed) || !tmp_committed)return false;
    *published_guard=tmp_guard;*published_fence=tmp_fence;
    *published_state=tmp_state;*committed=true;return true;
}
#endif
