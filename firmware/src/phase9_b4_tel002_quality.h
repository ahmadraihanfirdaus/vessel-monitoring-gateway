#ifndef PHASE9_B4_TEL002_QUALITY_H
#define PHASE9_B4_TEL002_QUALITY_H
/* TEL-002 host gate. Missing/invalid/unknown MUST serialize to null,
 * never substitute numeric zero. Stale may carry an explicitly real value. */
#include <stdbool.h>
#include "telemetry_contract.h"
static inline bool phase9_b4_tel002_safe_channel(const vg_telemetry_channel_t *c)
{
    if (!vg_tel_channel_is_consistent(c)) return false;
    if ((c->quality==VG_QUALITY_INVALID || c->quality==VG_QUALITY_MISSING ||
         c->quality==VG_QUALITY_UNKNOWN) && c->has_value) return false;
    return true;
}
static inline bool phase9_b4_tel002_safe_payload(const vg_telemetry_payload_t *p)
{
    if (!vg_tel_payload_is_consistent(p)) return false;
    for(size_t i=0u;i<p->channel_count;i++)
        if(!phase9_b4_tel002_safe_channel(&p->channels[i]))return false;
    return true;
}
#endif
