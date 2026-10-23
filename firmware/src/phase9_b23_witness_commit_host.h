#ifndef PHASE9_B23_WITNESS_COMMIT_HOST_H
#define PHASE9_B23_WITNESS_COMMIT_HOST_H
/* HOST ONLY: an exact external witness is INPUT, never authenticated/stored
 * here. Caller MUST persist an authenticated witness independently. CRC is
 * integrity only, not cryptographic proof. No NVS/disk durability claim. */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "phase9_b22_guarded_restore_host.h"
typedef struct {
    uint32_t generation;
    uint32_t confirmed_ack;
} vg_b23_witness;
/* Exactly match a witnessed (generation, ACK) tuple. If a newer valid
 * candidate was written but its witness update did not complete, restore
 * the OLD witnessed slot conservatively, never its unconfirmed ACK.
 * All outputs are unchanged on failure. */
static inline bool vg_b23_restore_witnessed(const vg_b20_slot slots[2],
    uint32_t tag,const vg_b23_witness *w,
    vg_b19_restored *out,bool *unwitnessed_newer)
{
    if(!slots || !tag || !w || !w->generation || !out || !unwitnessed_newer)
        return false;
    vg_b19_restored a,b;
    bool av=vg_b19_decode(slots[0].bytes,slots[0].len,tag,&a);
    bool bv=vg_b19_decode(slots[1].bytes,slots[1].len,tag,&b);
    if(av && bv && a.generation==b.generation &&
       (slots[0].len!=slots[1].len ||
        memcmp(slots[0].bytes,slots[1].bytes,slots[0].len)!=0))return false;
    bool am=av && a.generation==w->generation &&
        a.ack.last_accepted_sequence==w->confirmed_ack;
    bool bm=bv && b.generation==w->generation &&
        b.ack.last_accepted_sequence==w->confirmed_ack;
    if(!am && !bm)return false;
    vg_b19_restored selected=am?a:b;
    if(selected.ack.pending || selected.ack.pending_sequence ||
       selected.ack.pending_correlation)return false;
    bool newer=(av && a.generation>w->generation) ||
               (bv && b.generation>w->generation);
    *out=selected;
    *unwitnessed_newer=newer;
    return true;
}
/* Do not start another write when an un-witnessed newer candidate exists.
 * Keep the witness stable until the caller completes durable readback AND
 * separately commits a trustworthy new external witness. */
static inline bool vg_b23_prepare_witnessed(const vg_b20_slot slots[2],
    uint32_t tag,const vg_b23_witness *w,
    const net002_host_offline_store *store,const phase9_b8_ack_window *ack,
    uint8_t *out,size_t cap,size_t *out_len,unsigned *target,uint32_t *next)
{
    vg_b19_restored prior;
    bool newer=false;
    if(!vg_b23_restore_witnessed(slots,tag,w,&prior,&newer) || newer ||
       !ack || !out || !out_len || !target || !next ||
       w->generation==UINT32_MAX ||
       ack->last_accepted_sequence<prior.ack.last_accepted_sequence)return false;
    uint8_t temp[VG_B19_SLOT_MAX];size_t n=0u;unsigned t=0u;
    uint32_t g=0u;
    if(!vg_b20_prepare(slots,tag,store,ack,temp,cap,&n,&t,&g) ||
       g!=w->generation+1u)return false;
    memcpy(out,temp,n);*out_len=n;*target=t;*next=g;return true;
}
/* Pure host readback gate: do not advance external witness until every
 * byte and unchanged other slot have been checked. The proposed witness is
 * a VALUE TO BE PERSISTED by caller, NOT a claim persistence succeeded. */
static inline bool vg_b23_propose_after_readback(const vg_b20_slot before[2],
    const vg_b20_slot after[2],uint32_t tag,const vg_b23_witness *old,
    const uint8_t *expected,size_t size,unsigned target,uint32_t generation,
    uint32_t ack,vg_b23_witness *proposal)
{
    if(!before || !after || !tag || !old || !proposal || !expected ||
       target>1u || !old->generation || old->generation==UINT32_MAX ||
       generation!=old->generation+1u || ack<old->confirmed_ack ||
       size==0u || size>VG_B19_SLOT_MAX)return false;
    vg_b19_restored prior;bool pending=false;
    if(!vg_b23_restore_witnessed(before,tag,old,&prior,&pending) || pending)
        return false;
    unsigned other=1u-target;
    if(before[other].len!=after[other].len ||
       before[other].len>VG_B19_SLOT_MAX ||
       memcmp(before[other].bytes,after[other].bytes,before[other].len)!=0)
        return false;
    vg_b19_restored preserved;
    if(!vg_b19_decode(after[other].bytes,after[other].len,tag,&preserved) ||
       preserved.generation!=old->generation ||
       preserved.ack.last_accepted_sequence!=old->confirmed_ack ||
       preserved.ack.pending)return false;
    if(after[target].len!=size ||
       !vg_b20_verify_readback(expected,size,after[target].bytes,
                               after[target].len,tag,generation,ack))return false;
    vg_b19_restored selected;bool degraded=false;
    if(!vg_b19_select(after[0].bytes,after[0].len,
       after[1].bytes,after[1].len,tag,&selected,&degraded) ||
       selected.generation!=generation ||
       selected.ack.last_accepted_sequence!=ack)return false;
    vg_b23_witness local={generation,ack};*proposal=local;return true;
}
#endif
