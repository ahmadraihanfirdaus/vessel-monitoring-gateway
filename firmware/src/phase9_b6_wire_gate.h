#ifndef PHASE9_B6_WIRE_GATE_H
#define PHASE9_B6_WIRE_GATE_H
/* TEL-001/TEL-002 synthetic host wire gate. No ESP link, HTTP, or physical data claim. */
#include <stdbool.h>
#include <stddef.h>
#include "phase9_b4_tel001_wire.h"
#include "phase9_b4_tel002_quality.h"
static inline bool phase9_b6_wire_export(const vg_telemetry_payload_t *p,char *out,size_t cap)
{
    if (!out || !cap) return false;
    out[0]='\0';
    if (!p || !phase9_b4_tel002_safe_payload(p) ||
        !phase9_b4_tel001_export(p,out,cap)) { out[0]='\0';return false; }
    return true;
}
#endif
