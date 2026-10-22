#ifndef PHASE9_TEL003_DEDUP_HOST_WINDOW_H
#define PHASE9_TEL003_DEDUP_HOST_WINDOW_H
/* TEL-003 development-only in-memory replay classification.
 * Capacity is fixture-only, no eviction and NO MySQL-backed idempotency.
 * SIM-014/formal backend duplicate verification remains NOT_RUN. */
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include "telemetry_contract.h"
#define TEL003_HOST_WINDOW_CAP 3u
typedef enum {
    TEL003_HOST_INVALID=0, TEL003_HOST_NEW, TEL003_HOST_REPLAY,
    TEL003_HOST_CONFLICT, TEL003_HOST_FULL
} tel003_host_admission;
typedef struct {
    vg_telemetry_payload_t item[TEL003_HOST_WINDOW_CAP];
    size_t count;
} tel003_host_window;
static inline void tel003_host_init(tel003_host_window *w) {
    if (w) memset(w,0,sizeof(*w));
}
static inline tel003_host_admission tel003_host_admit(
    tel003_host_window *w,const vg_telemetry_payload_t *payload)
{
    if (!w || !payload || w->count>TEL003_HOST_WINDOW_CAP ||
        !vg_tel_payload_is_consistent(payload))return TEL003_HOST_INVALID;
    for(size_t i=0u;i<w->count;i++) {
        vg_telemetry_duplicate_result_t r=
            vg_tel_classify_duplicate(&w->item[i],payload);
        if(r==VG_TEL_DUPLICATE_INVALID)return TEL003_HOST_INVALID;
        if(r==VG_TEL_DUPLICATE_IDENTICAL)return TEL003_HOST_REPLAY;
        if(r==VG_TEL_DUPLICATE_CONFLICTING)return TEL003_HOST_CONFLICT;
    }
    if(w->count==TEL003_HOST_WINDOW_CAP)return TEL003_HOST_FULL;
    w->item[w->count++]=*payload;
    return TEL003_HOST_NEW;
}
#endif
