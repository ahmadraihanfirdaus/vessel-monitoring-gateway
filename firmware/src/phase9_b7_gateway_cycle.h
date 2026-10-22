#ifndef PHASE9_B7_GATEWAY_CYCLE_H
#define PHASE9_B7_GATEWAY_CYCLE_H
/* TST-001: deterministic composition of four scope guards, HOST TEST ONLY.
 * Callbacks are injected, real-time safety/physical auth are NOT verified. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "phase9_b7_source_admission.h"
#include "phase9_b7_safety_priority.h"
#include "phase9_b7_readonly_boundary.h"
#include "phase9_b7_replay_receipt.h"
typedef struct {
    sys003_local_driver local;
    net001_host_adapter *network;
    const vg_telemetry_payload_t *telemetry;
    const char *declared_source;
    const char *topic;
    const void *query_body;
    size_t query_len;
    net002_host_offline_store *journal;
    net002_host_replay_cursor *cursor;
    phase9_b6_host_receipt receipt;
    uint32_t correlation_id;
    uint32_t tick_ms;
} phase9_b7_gateway_request;
typedef struct {
    bool safety_ran;
    bool network_attempted;
    bool source_admitted;
    bool readonly_allowed;
    bool replay_advanced;
    net001_host_state link_state;
} phase9_b7_gateway_result;
static inline phase9_b7_gateway_result phase9_b7_gateway_step(
    const phase9_b7_gateway_request *req)
{
    phase9_b7_gateway_result r={false,false,false,false,false,NET001_HOST_IDLE};
    if (!req) return r;
    sys003_host_cycle_result local=phase9_b7_safety_priority(
        req->local,req->network,req->tick_ms);
    r.safety_ran=local.local_ok;
    r.network_attempted=local.network_attempted;
    r.link_state=local.link_state;
    if (!r.safety_ran) return r;
    r.source_admitted=phase9_b7_source_admit(req->telemetry,req->declared_source);
    r.readonly_allowed=phase9_b7_readonly_allow(req->topic,req->query_body,req->query_len);
    if (r.link_state==NET001_HOST_READY && req->journal && req->cursor) {
        r.replay_advanced=phase9_b7_replay_ack_guard(
           req->journal,req->cursor,req->receipt,req->correlation_id,
           r.safety_ran,r.source_admitted,r.readonly_allowed);
    }
    return r;
}
#endif
