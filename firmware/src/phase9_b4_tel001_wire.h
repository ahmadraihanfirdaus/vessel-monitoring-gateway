#ifndef PHASE9_B4_TEL001_WIRE_H
#define PHASE9_B4_TEL001_WIRE_H
/* Host-only TEL-001 exporter; no endpoint, authentication or real hardware. */
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include "telemetry_contract.h"
static inline bool phase9_b4_tel001_export(const vg_telemetry_payload_t *payload,
                                           char *output, size_t size)
{
    if (!payload || !output || size==0u || size>VG_TELEMETRY_JSON_MAX ||
        !vg_tel_payload_is_consistent(payload)) return false;
    /* Fail closed: physical origin cannot be established in this host harness. */
    if (payload->source_mode!=VG_SOURCE_SIMULATION &&
        payload->source_mode!=VG_SOURCE_BENCH_TEST) return false;
    output[0]='\0';
    return vg_tel_serialize_json(payload,output,size);
}
#endif
