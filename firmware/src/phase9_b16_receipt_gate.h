#ifndef PHASE9_B16_RECEIPT_GATE_H
#define PHASE9_B16_RECEIPT_GATE_H
/* Host integration development only. The result tag MUST come from a separately
 * verified authenticated HTTP JSON decoder, not caller-supplied wire data.
 * This helper does not implement network/TLS/JSON parsing or durable storage. */
#include <stdbool.h>
#include <stdint.h>
#include "phase9_b8_ack_window.h"
typedef enum {
    VG_B16_UNKNOWN=0,
    VG_B16_TELEMETRY_CREATED,
    VG_B16_TELEMETRY_IDENTICAL,
    VG_B16_EVENT_PERSISTED,
    VG_B16_EVENT_IDENTICAL,
    VG_B16_CONFLICT,
    VG_B16_DEPENDENCY_UNAVAILABLE,
    VG_B16_UNAUTHORIZED
} vg_b16_result_t;
typedef struct {
    uint16_t http_status;
    vg_b16_result_t decoded_result;
    uint32_t sequence;
    uint32_t correlation;
    bool authenticated_response_verified; /* injected only in host fixture */
    bool local_safety_pass;
} vg_b16_receipt_t;
static inline bool vg_b16_application_accept(uint16_t status,vg_b16_result_t tag){
    if(status==201u)
        return tag==VG_B16_TELEMETRY_CREATED || tag==VG_B16_EVENT_PERSISTED;
    if(status==200u)
        return tag==VG_B16_TELEMETRY_IDENTICAL || tag==VG_B16_EVENT_IDENTICAL;
    return false;
}
static inline bool vg_b16_commit_receipt(phase9_b8_ack_window *window,vg_b16_receipt_t r){
    if(!r.authenticated_response_verified || !r.local_safety_pass ||
        !vg_b16_application_accept(r.http_status,r.decoded_result)) return false;
    return phase9_b8_ack_commit(window,r.sequence,r.correlation,true,true,true);
}
#endif
