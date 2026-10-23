#ifndef PHASE9_B27_QUORUM_SEQUENCE_HOST_H
#define PHASE9_B27_QUORUM_SEQUENCE_HOST_H
/* C99 HOST POLICY ONLY. Repeated quorum must be externally authenticated,
 * observed, durable and independently bound to both domains. This module
 * implements none of those trust properties. No ESP32/NVS/power loss claim. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "phase9_b26_dual_witness_host.h"

typedef struct {
    vg_b23_witness primary;
    vg_b23_witness secondary;
    uint64_t primary_epoch;
    uint64_t secondary_epoch;
} vg_b27_votes;

/* Two sequential readback-and-quorum authorizations, committed atomically to
 * CALLER-VISIBLE OUTPUTS. First step must actually promote; second uses the
 * first guard/ACK state and must promote too. The intermediate slots are the
 * same bytes for the first 'after' and second 'before' by construction.
 * Any denial (including second-step denial) leaves ALL outputs untouched.
 * This is not a disk transaction and does not persist a quorum witness. */
static inline bool vg_b27_confirm_sequence(
    const vg_b20_slot before[2],const vg_b20_slot middle[2],
    const vg_b20_slot after[2],uint32_t tag,
    uint32_t primary_domain,uint32_t secondary_domain,
    const vg_b26_dual_guard *guard,const vg_b24_ticket tickets[2],
    const uint8_t *const expected[2],const size_t sizes[2],
    const vg_b27_votes votes[2],vg_b26_dual_guard *next,
    vg_b19_restored *restored,bool *committed)
{
    if(!before || !middle || !after || !tag || !primary_domain ||
       !secondary_domain || primary_domain==secondary_domain || !guard ||
       !tickets || !expected || !sizes || !votes || !next ||
       !restored || !committed || next==guard ||
       !expected[0] || !expected[1] || !sizes[0] || !sizes[1] ||
       sizes[0]>VG_B19_SLOT_MAX || sizes[1]>VG_B19_SLOT_MAX ||
       tickets[0].device_tag!=tag || tickets[1].device_tag!=tag ||
       tickets[0].proposed.generation!=tickets[1].previous.generation ||
       tickets[0].proposed.confirmed_ack!=tickets[1].previous.confirmed_ack ||
       tickets[0].proposed.generation==UINT32_MAX ||
       guard->accepted_round>UINT64_MAX-2u)return false;
    vg_b26_dual_guard intermediate,final_guard;
    vg_b19_restored first,second;
    bool first_committed=false,second_committed=false;
    if(!vg_b26_confirm(before,middle,tag,guard,&tickets[0],
          expected[0],sizes[0],primary_domain,&votes[0].primary,
          votes[0].primary_epoch,secondary_domain,&votes[0].secondary,
          votes[0].secondary_epoch,&intermediate,&first,&first_committed) ||
       !first_committed || first.generation!=tickets[0].proposed.generation ||
       first.ack.last_accepted_sequence!=tickets[0].proposed.confirmed_ack)
       return false;
    if(!vg_b26_confirm(middle,after,tag,&intermediate,&tickets[1],
          expected[1],sizes[1],primary_domain,&votes[1].primary,
          votes[1].primary_epoch,secondary_domain,&votes[1].secondary,
          votes[1].secondary_epoch,&final_guard,&second,&second_committed) ||
       !second_committed || final_guard.accepted_round!=guard->accepted_round+2u ||
       second.generation!=tickets[1].proposed.generation ||
       second.ack.last_accepted_sequence!=tickets[1].proposed.confirmed_ack ||
       second.ack.pending || second.ack.pending_sequence ||
       second.ack.pending_correlation)return false;
    *next=final_guard;
    *restored=second;
    *committed=true;
    return true;
}
#endif
