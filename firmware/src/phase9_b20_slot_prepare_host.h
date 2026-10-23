#ifndef PHASE9_B20_SLOT_PREPARE_HOST_H
#define PHASE9_B20_SLOT_PREPARE_HOST_H
/* Host-only two-slot update preparation. No filesystem/ESP NVS driver,
 * crash-atomic write guarantee, crypto attestation, or vessel-safety claim.
 * The caller MUST write only the selected older slot, then independently
 * read back and validate. The selected latest valid slot is never replaced. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b19_dual_slot_host.h"

typedef struct {
    uint8_t bytes[VG_B19_SLOT_MAX];
    size_t len;
} vg_b20_slot;

/* All caller output is unchanged on validation failure. A valid existing
 * checkpoint is mandatory: bootstrap/provisioning is separate and explicit.
 * No inferred 32-bit generation wrap or ACK sequence wrap is permitted. */
static inline bool vg_b20_prepare(const vg_b20_slot slots[2],uint32_t tag,
    const net002_host_offline_store *store,const phase9_b8_ack_window *ack,
    uint8_t *out,size_t capacity,size_t *out_len,unsigned *target,
    uint32_t *next_generation)
{
    if(!slots || !tag || !store || !ack || !out || !out_len || !target ||
       !next_generation || capacity<VG_B19_SLOT_OVERHEAD ||
       capacity>VG_B19_SLOT_MAX || !vg_b18_valid(store))return false;
    vg_b19_restored a,b,selected;
    bool va=vg_b19_decode(slots[0].bytes,slots[0].len,tag,&a);
    bool vb=vg_b19_decode(slots[1].bytes,slots[1].len,tag,&b);
    bool degraded=false;
    if(!vg_b19_select(slots[0].bytes,slots[0].len,
        slots[1].bytes,slots[1].len,tag,&selected,&degraded))return false;
    (void)degraded;
    /* Do not discard a confirmed ACK high-water mark on a new checkpoint. */
    if(ack->last_accepted_sequence<selected.ack.last_accepted_sequence)return false;
    uint32_t next=0u;
    if(!vg_b19_next_generation(selected.generation,&next))return false;
    unsigned chosen=0u;
    if(!va) chosen=0u;
    else if(!vb) chosen=1u;
    else if(a.generation>b.generation) chosen=1u;
    else if(b.generation>a.generation) chosen=0u;
    else chosen=1u; /* byte-identical equal-generation slots only */
    uint8_t candidate[VG_B19_SLOT_MAX];size_t size=0u;
    if(!vg_b19_wrap(store,ack,tag,next,candidate,capacity,&size))return false;
    vg_b19_restored check;
    if(!vg_b19_decode(candidate,size,tag,&check) ||
       check.generation!=next ||
       check.ack.last_accepted_sequence!=ack->last_accepted_sequence ||
       check.ack.pending)return false;
    memcpy(out,candidate,size);
    *out_len=size;*target=chosen;*next_generation=next;
    return true;
}

/* Call only AFTER write/readback; rejects partial writes and bit flips.
 * This is an integrity check, not a durable flush guarantee. */
static inline bool vg_b20_verify_readback(const uint8_t *expected,size_t expected_n,
    const uint8_t *actual,size_t actual_n,uint32_t tag,uint32_t generation,
    uint32_t confirmed_ack)
{
    if(!expected || !actual || !tag || !generation ||
       expected_n==0u || expected_n!=actual_n ||
       expected_n>VG_B19_SLOT_MAX ||
       memcmp(expected,actual,expected_n)!=0)return false;
    vg_b19_restored restored;
    return vg_b19_decode(actual,actual_n,tag,&restored) &&
        restored.generation==generation &&
        restored.ack.last_accepted_sequence==confirmed_ack &&
        !restored.ack.pending && !restored.ack.pending_correlation &&
        !restored.ack.pending_sequence;
}
#endif
