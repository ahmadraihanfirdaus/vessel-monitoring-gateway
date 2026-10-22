#ifndef PHASE9_B7_SOURCE_ADMISSION_H
#define PHASE9_B7_SOURCE_ADMISSION_H
/* SYS-002 synthetic host boundary: labels NEVER prove physical origin. */
#include <stdbool.h>
#include <string.h>
#include "phase9_sys002_telemetry_provenance_host.h"
static inline bool phase9_b7_source_admit(const vg_telemetry_payload_t *p,
                                           const char *label)
{
    if (!p || !label || !p->device_id[0] || !p->boot_id[0]) return false;
    if (p->source_mode != VG_SOURCE_SIMULATION &&
        p->source_mode != VG_SOURCE_BENCH_TEST) return false;
    return sys002_host_safe_payload_label(p,label);
}
#endif
