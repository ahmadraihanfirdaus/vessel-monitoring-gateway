#ifndef PHASE9_B26_DUAL_WITNESS_HOST_H
#define PHASE9_B26_DUAL_WITNESS_HOST_H
/* C99 HOST POLICY ONLY. Both observation sources, domain identifiers and
 * epochs MUST be authenticated, independent and durable EXTERNALLY.
 * Matching untrusted witnesses is NOT an authentication primitive. */
#include <stdbool.h>
#include <stdint.h>
#include "phase9_b25_observation_epoch_host.h"

typedef struct {
    vg_b25_observation_guard primary;
    vg_b25_observation_guard secondary;
    uint64_t accepted_round;
} vg_b26_dual_guard;

/* Seed only from two independently authenticated durable source states.
 * Caller guarantees each domain is independent and belongs to this device. */
static inline bool vg_b26_seed(uint32_t tag,uint32_t primary_domain,
    uint32_t secondary_domain,uint64_t primary_epoch,
    uint64_t secondary_epoch,const vg_b23_witness *previous,
    vg_b26_dual_guard *out)
{
    if(!tag || !primary_domain || !secondary_domain ||
       primary_domain==secondary_domain || !out || !previous)return false;
    vg_b26_dual_guard candidate;
    if(!vg_b25_guard_seed(tag,primary_domain,primary_epoch,previous,
                         &candidate.primary) ||
       !vg_b25_guard_seed(tag,secondary_domain,secondary_epoch,previous,
                         &candidate.secondary))return false;
    candidate.accepted_round=0u;
    *out=candidate;
    return true;
}

/* Both independently verified sources must agree exactly on generation+ACK,
 * with exactly-next epoch in their respective domains. No quorum fallback,
 * no timeout bypass and no single-source promotion. All outputs atomic on
 * failure, including when the second verification fails after the first.
 * The host policy does not implement trustworthy independent sources. */
static inline bool vg_b26_confirm(const vg_b20_slot before[2],
    const vg_b20_slot after[2],uint32_t tag,const vg_b26_dual_guard *guard,
    const vg_b24_ticket *ticket,const uint8_t *expected,size_t size,
    uint32_t primary_domain,const vg_b23_witness *primary_witness,
    uint64_t primary_epoch,uint32_t secondary_domain,
    const vg_b23_witness *secondary_witness,uint64_t secondary_epoch,
    vg_b26_dual_guard *next,vg_b19_restored *restored,bool *committed)
{
    if(!before || !after || !tag || !guard || !ticket || !expected ||
       !size || !primary_witness || !secondary_witness || !next ||
       !restored || !committed || !primary_domain || !secondary_domain ||
       primary_domain==secondary_domain ||
       guard->primary.device_tag!=tag || guard->secondary.device_tag!=tag ||
       guard->primary.source_domain!=primary_domain ||
       guard->secondary.source_domain!=secondary_domain ||
       !guard->primary.last_witness.generation ||
       guard->primary.last_witness.generation!=guard->secondary.last_witness.generation ||
       guard->primary.last_witness.confirmed_ack!=guard->secondary.last_witness.confirmed_ack ||
       guard->accepted_round==UINT64_MAX ||
       primary_witness->generation!=secondary_witness->generation ||
       primary_witness->confirmed_ack!=secondary_witness->confirmed_ack)
        return false;
    vg_b25_observation_guard pa,sa;
    vg_b19_restored pr,sr;
    bool pc=false,sc=false;
    if(!vg_b25_observe(before,after,tag,primary_domain,
       &guard->primary,ticket,expected,size,primary_witness,primary_epoch,
       &pa,&pr,&pc))return false;
    if(!vg_b25_observe(before,after,tag,secondary_domain,
       &guard->secondary,ticket,expected,size,secondary_witness,
       secondary_epoch,&sa,&sr,&sc))return false;
    if(pc!=sc || pr.generation!=sr.generation ||
       pr.ack.last_accepted_sequence!=sr.ack.last_accepted_sequence ||
       pr.ack.pending || sr.ack.pending ||
       pa.last_witness.generation!=sa.last_witness.generation ||
       pa.last_witness.confirmed_ack!=sa.last_witness.confirmed_ack)
        return false;
    vg_b26_dual_guard candidate=*guard;
    candidate.primary=pa;
    candidate.secondary=sa;
    candidate.accepted_round++;
    *next=candidate;
    *restored=pr;
    *committed=pc;
    return true;
}
#endif
