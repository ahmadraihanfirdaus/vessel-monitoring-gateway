#ifndef PHASE9_B5_REPLAY_ACK_GUARD_H
#define PHASE9_B5_REPLAY_ACK_GUARD_H
/* NET-002 host-only caller-supplied acknowledgement proof, not a verified server response.
 * Wrong/stale acknowledgement MUST NOT advance replay; no durable storage. */
#include <stdbool.h>
#include <stdint.h>
#include "phase9_net002_replay_cursor_host.h"
typedef struct {
    bool connected;
    bool response_verified; /* strictly external, fake driver in host tests */
    uint32_t acknowledged_event_id;
} phase9_b5_ack_claims;
static inline bool phase9_b5_replay_commit_ack(
    const net002_host_offline_store *store,
    net002_host_replay_cursor *cursor,phase9_b5_ack_claims p)
{
    if (!p.connected || !p.response_verified || p.acknowledged_event_id==0u) return false;
    return net002_replay_ack(store,cursor,p.acknowledged_event_id);
}
#endif
