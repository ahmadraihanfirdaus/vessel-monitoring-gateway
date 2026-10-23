#ifndef PHASE9_B22_GUARDED_RESTORE_HOST_H
#define PHASE9_B22_GUARDED_RESTORE_HOST_H
/* HOST ONLY: caller-provided trusted high-water floor is external evidence,
 * not created, verified, or durably stored by this module. CRC != signature.
 * No guarantee for malicious replacement of BOTH the slots and the witness.
 * Never infer generation rollover, promote an ACK, or use in marine safety. */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "phase9_b20_slot_prepare_host.h"
typedef struct {
    uint32_t minimum_generation;
    uint32_t minimum_confirmed_ack;
} vg_b22_floor;
/* Reject rollback below an independently witnessed floor, split brain,
 * invalid identity, both-slot corruption, or stale confirmed ACK. Caller
 * destinations are not modified on any failure. Fallback allowed only when
 * its conservative state meets BOTH trusted lower bounds. */
static inline bool vg_b22_restore_guarded(const vg_b20_slot slots[2],
    uint32_t device_tag,const vg_b22_floor *floor,
    vg_b19_restored *out,bool *degraded)
{
    if(!slots || !device_tag || !floor || !out || !degraded ||
       !floor->minimum_generation)return false;
    vg_b19_restored local;bool local_degraded=false;
    if(!vg_b19_select(slots[0].bytes,slots[0].len,
        slots[1].bytes,slots[1].len,device_tag,&local,&local_degraded))return false;
    if(local.generation<floor->minimum_generation ||
       local.ack.last_accepted_sequence<floor->minimum_confirmed_ack ||
       local.ack.pending || local.ack.pending_sequence ||
       local.ack.pending_correlation)return false;
    *out=local;*degraded=local_degraded;return true;
}
/* Before a two-slot update check externally witnessed floor, then reuse
 * B20 older-slot selection/readback logic without relaxing any checks. */
static inline bool vg_b22_prepare_guarded(const vg_b20_slot slots[2],
    uint32_t tag,const vg_b22_floor *floor,
    const net002_host_offline_store *store,const phase9_b8_ack_window *ack,
    uint8_t *out,size_t cap,size_t *size,unsigned *target,uint32_t *generation)
{
    vg_b19_restored prior;bool degraded=false;
    if(!vg_b22_restore_guarded(slots,tag,floor,&prior,&degraded))return false;
    (void)degraded;
    if(!ack || ack->last_accepted_sequence<prior.ack.last_accepted_sequence)
        return false;
    return vg_b20_prepare(slots,tag,store,ack,out,cap,size,target,generation);
}
#endif
