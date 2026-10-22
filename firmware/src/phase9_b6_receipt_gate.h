#ifndef PHASE9_B6_RECEIPT_GATE_H
#define PHASE9_B6_RECEIPT_GATE_H
/* NET-002: host-only injected receipt; verification flag is NOT real server auth. */
#include <stdbool.h>
#include <stdint.h>
#include "phase9_b5_replay_ack_guard.h"
typedef struct {
    bool connected;
    bool response_verified; /* supplied by fake host driver */
    bool application_ack_eligible;
    uint32_t event_id;
    uint32_t correlation_id;
} phase9_b6_host_receipt;
static inline bool phase9_b6_replay_accept(
   const net002_host_offline_store *store,net002_host_replay_cursor *cursor,
   phase9_b6_host_receipt receipt,uint32_t expected_correlation_id)
{
    if (expected_correlation_id==0u || receipt.correlation_id!=expected_correlation_id ||
        !receipt.connected || !receipt.response_verified || !receipt.application_ack_eligible ||
        receipt.event_id==0u) return false;
    phase9_b5_ack_claims prior={receipt.connected,receipt.response_verified,receipt.event_id};
    return phase9_b5_replay_commit_ack(store,cursor,prior);
}
#endif
