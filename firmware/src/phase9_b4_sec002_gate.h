#ifndef PHASE9_B4_SEC002_GATE_H
#define PHASE9_B4_SEC002_GATE_H
/* Fail-closed SEC-002 development contract. Boolean flags are fixture inputs,
 * NOT evidence TLS was performed or credentials checked. No real connection. */
#include <stdbool.h>
#include "core_source_mode.h"
typedef struct {
    bool endpoint_configured;
    bool tls_peer_verified;
    bool device_auth_context_present;
    bool credentials_outside_source;
} phase9_b4_transport_claims;
static inline bool phase9_b4_sec002_host_admit(phase9_b4_transport_claims p,
                                                vg_source_mode_t source)
{
    return p.endpoint_configured && p.tls_peer_verified &&
           p.device_auth_context_present && p.credentials_outside_source &&
           (source==VG_SOURCE_SIMULATION || source==VG_SOURCE_BENCH_TEST);
}
#endif
