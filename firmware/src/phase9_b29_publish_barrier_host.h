#ifndef PHASE9_B29_PUBLISH_BARRIER_HOST_H
#define PHASE9_B29_PUBLISH_BARRIER_HOST_H
/* C99 host policy only. Two phase prepared result -> externally confirmed
 * durable CAS receipt -> publication. Neither authenticates the receipt nor
 * performs persistent storage CAS, disk sync, ESP32/NVS operations. Caller
 * MUST validate the receipt using an independent trusted store. */
#include <stdbool.h>
#include <stdint.h>
#include "phase9_b28_revision_fence_host.h"

typedef struct {
    bool ready;
    uint32_t device_tag;
    uint32_t primary_domain;
    uint32_t secondary_domain;
    uint64_t before_revision;
    vg_b26_dual_guard next_guard;
    vg_b28_fence next_fence;
    vg_b19_restored next_state;
} vg_b29_pending;

typedef struct {
    bool external_cas_confirmed; /* supplied by trusted external CAS adapter */
    uint32_t device_tag;
    uint32_t primary_domain;
    uint32_t secondary_domain;
    uint64_t before_revision;
    uint64_t after_revision;
    uint64_t accepted_round;
    uint64_t primary_epoch;
    uint64_t secondary_epoch;
    vg_b23_witness witness;
} vg_b29_cas_receipt;

/* PREPARE ONLY: proposed state is held as private pending material, never
 * returned as a committed runtime ACK. Caller must not expose pending state
 * as runtime state. All output bytes unchanged on any denial. */
static inline bool vg_b29_prepare(
    const vg_b20_slot before[2],const vg_b20_slot middle[2],
    const vg_b20_slot after[2],uint32_t tag,
    uint32_t primary_domain,uint32_t secondary_domain,
    const vg_b26_dual_guard *guard,const vg_b28_fence *fence,
    uint64_t externally_verified_before_revision,
    const vg_b24_ticket tickets[2],
    const uint8_t *const expected[2],const size_t sizes[2],
    const vg_b27_votes votes[2],vg_b29_pending *pending)
{
    if(!pending || !fence || !guard || !tag || !primary_domain ||
       !secondary_domain || primary_domain==secondary_domain ||
       !fence->revision || fence->revision>=UINT64_MAX-1u)
       return false;
    vg_b26_dual_guard temp_guard;
    vg_b28_fence temp_fence;
    vg_b19_restored temp_state;
    bool old_commit=false;
    if(!vg_b28_confirm_with_fence(before,middle,after,tag,
        primary_domain,secondary_domain,guard,fence,
        externally_verified_before_revision,tickets,expected,sizes,votes,
        &temp_guard,&temp_fence,&temp_state,&old_commit) || !old_commit ||
       temp_fence.revision!=fence->revision+UINT64_C(1) ||
       temp_fence.device_tag!=tag ||
       temp_fence.primary_domain!=primary_domain ||
       temp_fence.secondary_domain!=secondary_domain ||
       temp_state.generation!=temp_fence.last_witness.generation ||
       temp_state.ack.last_accepted_sequence!=temp_fence.last_witness.confirmed_ack ||
       temp_state.ack.pending || temp_state.ack.pending_sequence ||
       temp_state.ack.pending_correlation)return false;
    vg_b29_pending tmp={0};
    tmp.ready=true;
    tmp.device_tag=tag;
    tmp.primary_domain=primary_domain;
    tmp.secondary_domain=secondary_domain;
    tmp.before_revision=fence->revision;
    tmp.next_guard=temp_guard;
    tmp.next_fence=temp_fence;
    tmp.next_state=temp_state;
    *pending=tmp;
    return true;
}

/* PUBLISH ONLY AFTER EXTERNAL CAS: A receipt is not self-issued here. It
 * must prove (via caller trust) that expected revision was replaced with
 * exactly the candidate revision. Current verified external revision is a
 * separate input: disagreement means stale writer / replay / race. Denial
 * leaves guard, fence, state and committed outputs byte-for-byte intact. */
static inline bool vg_b29_finalize(
    const vg_b29_pending *pending,
    const vg_b29_cas_receipt *receipt,
    uint64_t externally_verified_after_revision,
    vg_b26_dual_guard *published_guard,
    vg_b28_fence *published_fence,
    vg_b19_restored *published_state,bool *committed)
{
    if(!pending || !receipt || !published_guard || !published_fence ||
       !published_state || !committed || !pending->ready ||
       !receipt->external_cas_confirmed ||
       !pending->device_tag || !pending->primary_domain ||
       !pending->secondary_domain ||
       pending->primary_domain==pending->secondary_domain ||
       !pending->before_revision || pending->before_revision>=UINT64_MAX-1u ||
       pending->next_fence.revision!=pending->before_revision+UINT64_C(1) ||
       externally_verified_after_revision!=pending->next_fence.revision ||
       receipt->before_revision!=pending->before_revision ||
       receipt->after_revision!=pending->next_fence.revision ||
       receipt->device_tag!=pending->device_tag ||
       receipt->primary_domain!=pending->primary_domain ||
       receipt->secondary_domain!=pending->secondary_domain ||
       receipt->accepted_round!=pending->next_fence.accepted_round ||
       receipt->primary_epoch!=pending->next_fence.primary_epoch ||
       receipt->secondary_epoch!=pending->next_fence.secondary_epoch ||
       receipt->witness.generation!=pending->next_fence.last_witness.generation ||
       receipt->witness.confirmed_ack!=pending->next_fence.last_witness.confirmed_ack ||
       pending->next_fence.device_tag!=pending->device_tag ||
       pending->next_fence.primary_domain!=pending->primary_domain ||
       pending->next_fence.secondary_domain!=pending->secondary_domain ||
       pending->next_guard.accepted_round!=pending->next_fence.accepted_round ||
       pending->next_guard.primary.last_observation_epoch!=pending->next_fence.primary_epoch ||
       pending->next_guard.secondary.last_observation_epoch!=pending->next_fence.secondary_epoch ||
       pending->next_guard.primary.last_witness.generation!=receipt->witness.generation ||
       pending->next_guard.secondary.last_witness.generation!=receipt->witness.generation ||
       pending->next_guard.primary.last_witness.confirmed_ack!=receipt->witness.confirmed_ack ||
       pending->next_guard.secondary.last_witness.confirmed_ack!=receipt->witness.confirmed_ack ||
       pending->next_state.generation!=receipt->witness.generation ||
       pending->next_state.ack.last_accepted_sequence!=receipt->witness.confirmed_ack ||
       pending->next_state.ack.pending ||
       pending->next_state.ack.pending_sequence ||
       pending->next_state.ack.pending_correlation)
       return false;
    *published_guard=pending->next_guard;
    *published_fence=pending->next_fence;
    *published_state=pending->next_state;
    *committed=true;
    return true;
}
#endif
