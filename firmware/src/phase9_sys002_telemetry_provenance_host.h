#ifndef PHASE9_SYS002_TELEMETRY_PROVENANCE_HOST_H
#define PHASE9_SYS002_TELEMETRY_PROVENANCE_HOST_H
/* SYS-002 host-only provenance gate. Physical-labelled payloads may be
 * represented by contracts but are NOT authorized for uplink here.
 * An input label never substitutes for independently verified origin. */
#include <stdbool.h>
#include <string.h>
#include "sys002_source_provenance_host.h"
#include "telemetry_contract.h"
static inline bool sys002_host_safe_payload_label(
    const vg_telemetry_payload_t *payload, const char *declared_label)
{
    sys002_source_mode parsed;
    if (!payload || !sys002_parse_source(declared_label,&parsed) ||
        parsed==SYS002_PHYSICAL || !vg_tel_payload_is_consistent(payload))
        return false;
    return (parsed==SYS002_SIMULATION &&
            payload->source_mode==VG_SOURCE_SIMULATION) ||
           (parsed==SYS002_BENCH_TEST &&
            payload->source_mode==VG_SOURCE_BENCH_TEST);
}
#endif
