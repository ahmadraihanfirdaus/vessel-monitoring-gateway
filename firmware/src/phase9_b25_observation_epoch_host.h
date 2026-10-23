#ifndef PHASE9_B25_OBSERVATION_EPOCH_HOST_H
#define PHASE9_B25_OBSERVATION_EPOCH_HOST_H
/* C99 HOST POLICY ONLY. Caller must independently authenticate and durably
 * enforce source_domain + observation_epoch before calling. This code neither
 * implements trusted persistence nor cryptographically verifies the source. */
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b24_witness_receipt_host.h"

typedef struct {
    uint32_t device_tag;
    uint32_t source_domain;
    uint64_t last_observation_epoch;
    vg_b23_witness last_witness;
} vg_b25_observation_guard;

/* Seed ONLY from an independently verified durable witness and monotonic
 * epoch. Zero tags and a witness without a generation are rejected. */
static inline bool vg_b25_guard_seed(uint32_t device_tag,uint32_t domain,
    uint64_t last_epoch,const vg_b23_witness *witness,
    vg_b25_observation_guard *out)
{
    if(!device_tag || !domain || !last_epoch ||
       last_epoch==UINT64_MAX || !witness || !out ||
       !witness->generation)return false;
    vg_b25_observation_guard result;
    result.device_tag=device_tag;
    result.source_domain=domain;
    result.last_observation_epoch=last_epoch;
    result.last_witness=*witness;
    *out=result;
    return true;
}

/* Accept exactly the next externally trusted observation epoch; neither a
 * repeated observation nor an epoch gap may trigger checkpoint promotion.
 * On old witness: keep previous ACK; on new witness: promote only after B24
 * readback validation. Rejects are output-atomic for all three outputs.
 * Epoch freshness/authenticity is an EXTERNAL precondition, not supplied by
 * this in-memory guard; restarting it without trusted state is unsafe. */
static inline bool vg_b25_observe(const vg_b20_slot before[2],
    const vg_b20_slot after[2],uint32_t tag,uint32_t domain,
    const vg_b25_observation_guard *guard,const vg_b24_ticket *ticket,
    const uint8_t *expected,size_t size,const vg_b23_witness *observed,
    uint64_t verified_epoch,vg_b25_observation_guard *next,
    vg_b19_restored *restored,bool *committed)
{
    if(!before || !after || !tag || !domain || !guard || !ticket ||
       !expected || !observed || !next || !restored || !committed ||
       !verified_epoch || !guard->last_observation_epoch ||
       guard->last_observation_epoch==UINT64_MAX ||
       verified_epoch!=guard->last_observation_epoch+UINT64_C(1) ||
       guard->device_tag!=tag || guard->source_domain!=domain ||
       ticket->device_tag!=tag ||
       ticket->previous.generation!=guard->last_witness.generation ||
       ticket->previous.confirmed_ack!=guard->last_witness.confirmed_ack)
       return false;
    vg_b19_restored candidate;bool candidate_committed=false;
    if(!vg_b24_resolve_observation(before,after,tag,ticket,expected,size,
       observed,&candidate,&candidate_committed))return false;
    vg_b25_observation_guard changed=*guard;
    changed.last_observation_epoch=verified_epoch;
    if(candidate_committed)changed.last_witness=ticket->proposed;
    if(changed.last_witness.generation!=candidate.generation ||
       changed.last_witness.confirmed_ack!=candidate.ack.last_accepted_sequence ||
       candidate.ack.pending || candidate.ack.pending_sequence ||
       candidate.ack.pending_correlation)return false;
    *next=changed;
    *restored=candidate;
    *committed=candidate_committed;
    return true;
}
#endif
