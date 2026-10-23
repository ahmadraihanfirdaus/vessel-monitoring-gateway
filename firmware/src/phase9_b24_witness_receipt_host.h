#ifndef PHASE9_B24_WITNESS_RECEIPT_HOST_H
#define PHASE9_B24_WITNESS_RECEIPT_HOST_H
/* C99 HOST TEST POLICY ONLY. No external witness storage or authentication.
 * A caller MUST verify that an observation is fresh, trustworthy and durable.
 * CRC32 below is an accidental-corruption check; NOT an authenticator. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b23_witness_commit_host.h"

typedef struct {
    uint32_t device_tag;
    vg_b23_witness previous;
    vg_b23_witness proposed;
    uint32_t candidate_crc32;
    size_t candidate_len;
    unsigned target_slot;
} vg_b24_ticket;

/* Issue a bounded ticket ONLY after B23 exact readback gate succeeds.
 * It is a proposal, never evidence of an external witness commit. */
static inline bool vg_b24_issue_ticket(const vg_b20_slot before[2],
    const vg_b20_slot after[2],uint32_t tag,const vg_b23_witness *previous,
    const uint8_t *expected,size_t size,unsigned target,uint32_t generation,
    uint32_t ack,vg_b24_ticket *out)
{
    if(!out || !expected || !size || size>VG_B19_SLOT_MAX || !previous)
        return false;
    vg_b23_witness proposal;
    if(!vg_b23_propose_after_readback(before,after,tag,previous,expected,
        size,target,generation,ack,&proposal))return false;
    vg_b24_ticket t;
    t.device_tag=tag;t.previous=*previous;t.proposed=proposal;
    t.candidate_crc32=vg_b18_crc32(expected,size);
    t.candidate_len=size;t.target_slot=target;
    *out=t;return true;
}

/* Resolve AFTER an independently retrieved trusted observation. If the
 * observation is old, restore the old slot and do not promote the new ACK.
 * If exactly new, restore the new slot. Missing/mismatched => fail-closed.
 * Outputs do not change on any failure. Nonce/auth/freshness are deliberately
 * NOT provided here; caller must enforce them outside this host policy. */
static inline bool vg_b24_resolve_observation(const vg_b20_slot before[2],
    const vg_b20_slot after[2],uint32_t tag,const vg_b24_ticket *ticket,
    const uint8_t *expected,size_t size,const vg_b23_witness *observed,
    vg_b19_restored *out,bool *committed)
{
    if(!before || !after || !tag || !ticket || !observed || !expected ||
       !out || !committed || !size || size>VG_B19_SLOT_MAX ||
       ticket->device_tag!=tag || ticket->candidate_len!=size ||
       ticket->target_slot>1u || !ticket->previous.generation ||
       ticket->previous.generation==UINT32_MAX ||
       ticket->proposed.generation!=ticket->previous.generation+1u ||
       ticket->proposed.confirmed_ack<ticket->previous.confirmed_ack ||
       ticket->candidate_crc32!=vg_b18_crc32(expected,size))return false;
    vg_b23_witness checked;
    if(!vg_b23_propose_after_readback(before,after,tag,&ticket->previous,
       expected,size,ticket->target_slot,ticket->proposed.generation,
       ticket->proposed.confirmed_ack,&checked) ||
       checked.generation!=ticket->proposed.generation ||
       checked.confirmed_ack!=ticket->proposed.confirmed_ack)return false;
    bool now_new=observed->generation==checked.generation &&
                 observed->confirmed_ack==checked.confirmed_ack;
    bool still_old=observed->generation==ticket->previous.generation &&
                   observed->confirmed_ack==ticket->previous.confirmed_ack;
    if(!now_new && !still_old)return false;
    vg_b19_restored recovered;bool newer=false;
    if(!vg_b23_restore_witnessed(after,tag,observed,&recovered,&newer) ||
       (now_new && newer) || (still_old && !newer) ||
       recovered.ack.pending || recovered.ack.pending_sequence ||
       recovered.ack.pending_correlation)return false;
    *out=recovered;*committed=now_new;return true;
}
#endif
