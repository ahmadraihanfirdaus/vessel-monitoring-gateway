#ifndef PHASE9_B28_REVISION_FENCE_HOST_H
#define PHASE9_B28_REVISION_FENCE_HOST_H
/* Host C99 compare-and-swap policy only. The externally observed revision
 * MUST be authenticated and durable by the caller. This code implements
 * neither a storage CAS nor device authentication. No ESP32/NVS claim. */
#include <stdbool.h>
#include <stdint.h>
#include "phase9_b27_quorum_sequence_host.h"

typedef struct {
    uint32_t device_tag;
    uint32_t primary_domain;
    uint32_t secondary_domain;
    uint64_t revision;
    uint64_t accepted_round;
    uint64_t primary_epoch;
    uint64_t secondary_epoch;
    vg_b23_witness last_witness;
} vg_b28_fence;

/* Snapshot trusted external state only. Reject inconsistent guard / source
 * histories instead of trying to repair them. Output unchanged on denial. */
static inline bool vg_b28_seed_fence(const vg_b26_dual_guard *guard,
    uint64_t trusted_revision,vg_b28_fence *out)
{
    if(!guard || !out || !trusted_revision ||
       trusted_revision==UINT64_MAX ||
       !guard->primary.device_tag ||
       guard->primary.device_tag!=guard->secondary.device_tag ||
       !guard->primary.source_domain || !guard->secondary.source_domain ||
       guard->primary.source_domain==guard->secondary.source_domain ||
       !guard->primary.last_observation_epoch ||
       !guard->secondary.last_observation_epoch ||
       !guard->primary.last_witness.generation ||
       guard->primary.last_witness.generation!=guard->secondary.last_witness.generation ||
       guard->primary.last_witness.confirmed_ack!=guard->secondary.last_witness.confirmed_ack)
       return false;
    vg_b28_fence candidate;
    candidate.device_tag=guard->primary.device_tag;
    candidate.primary_domain=guard->primary.source_domain;
    candidate.secondary_domain=guard->secondary.source_domain;
    candidate.revision=trusted_revision;
    candidate.accepted_round=guard->accepted_round;
    candidate.primary_epoch=guard->primary.last_observation_epoch;
    candidate.secondary_epoch=guard->secondary.last_observation_epoch;
    candidate.last_witness=guard->primary.last_witness;
    *out=candidate;
    return true;
}

/* Caller must hold a trusted serialized CAS/fence through observation and
 * publication. An adversary able to roll back BOTH guard and trusted_revision
 * can replay. No positive trust claim is made for an in-memory fence.
 * Every denial leaves guard, fence, restored and committed unchanged. */
static inline bool vg_b28_confirm_with_fence(
    const vg_b20_slot before[2],const vg_b20_slot middle[2],
    const vg_b20_slot after[2],uint32_t tag,
    uint32_t primary_domain,uint32_t secondary_domain,
    const vg_b26_dual_guard *guard,const vg_b28_fence *fence,
    uint64_t externally_verified_revision,
    const vg_b24_ticket tickets[2],
    const uint8_t *const expected[2],const size_t sizes[2],
    const vg_b27_votes votes[2],
    vg_b26_dual_guard *next_guard,vg_b28_fence *next_fence,
    vg_b19_restored *restored,bool *committed)
{
    if(!guard || !fence || !next_guard || !next_fence || !restored ||
       !committed || next_guard==guard || next_fence==fence ||
       !fence->revision || fence->revision==UINT64_MAX ||
       externally_verified_revision!=fence->revision ||
       fence->device_tag!=tag || fence->primary_domain!=primary_domain ||
       fence->secondary_domain!=secondary_domain ||
       primary_domain==secondary_domain ||
       guard->accepted_round!=fence->accepted_round ||
       guard->primary.device_tag!=tag || guard->secondary.device_tag!=tag ||
       guard->primary.source_domain!=primary_domain ||
       guard->secondary.source_domain!=secondary_domain ||
       guard->primary.last_observation_epoch!=fence->primary_epoch ||
       guard->secondary.last_observation_epoch!=fence->secondary_epoch ||
       guard->primary.last_witness.generation!=fence->last_witness.generation ||
       guard->secondary.last_witness.generation!=fence->last_witness.generation ||
       guard->primary.last_witness.confirmed_ack!=fence->last_witness.confirmed_ack ||
       guard->secondary.last_witness.confirmed_ack!=fence->last_witness.confirmed_ack)
       return false;
    vg_b26_dual_guard proposed_guard;
    vg_b19_restored proposed_state;
    bool proposed_committed=false;
    if(!vg_b27_confirm_sequence(before,middle,after,tag,
        primary_domain,secondary_domain,guard,tickets,expected,sizes,votes,
        &proposed_guard,&proposed_state,&proposed_committed) ||
       !proposed_committed ||
       proposed_guard.accepted_round!=fence->accepted_round+UINT64_C(2) ||
       proposed_guard.primary.last_observation_epoch!=fence->primary_epoch+UINT64_C(2) ||
       proposed_guard.secondary.last_observation_epoch!=fence->secondary_epoch+UINT64_C(2) ||
       proposed_guard.primary.last_witness.generation!=proposed_state.generation ||
       proposed_guard.primary.last_witness.confirmed_ack!=proposed_state.ack.last_accepted_sequence ||
       proposed_guard.secondary.last_witness.generation!=proposed_state.generation ||
       proposed_guard.secondary.last_witness.confirmed_ack!=proposed_state.ack.last_accepted_sequence)
       return false;
    vg_b28_fence proposed_fence;
    if(!vg_b28_seed_fence(&proposed_guard,fence->revision+UINT64_C(1),
                          &proposed_fence))return false;
    *next_guard=proposed_guard;
    *next_fence=proposed_fence;
    *restored=proposed_state;
    *committed=true;
    return true;
}
#endif
