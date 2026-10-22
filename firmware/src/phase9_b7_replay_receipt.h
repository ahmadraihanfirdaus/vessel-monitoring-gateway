#ifndef PHASE9_B7_REPLAY_RECEIPT_H
#define PHASE9_B7_REPLAY_RECEIPT_H
/* NET-002: no ACK after failed local step, source, or read-only gate.
 * Claimed 'verified' flag is TEST INJECTION, not real authenticated server proof.
 * No flash/NVS persistence, no HTTP, no replay removal. */
#include <stdbool.h>
#include <stdint.h>
#include "phase9_b6_receipt_gate.h"
static inline bool phase9_b7_replay_ack_guard(
    const net002_host_offline_store *store,net002_host_replay_cursor *cursor,
    phase9_b6_host_receipt receipt,uint32_t correlation,
    bool local_safety_ran,bool source_admitted,bool readonly_boundary)
{
    if (!local_safety_ran || !source_admitted || !readonly_boundary)
        return false;
    return phase9_b6_replay_accept(store,cursor,receipt,correlation);
}
#endif
