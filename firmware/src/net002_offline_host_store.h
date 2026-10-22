#ifndef NET002_OFFLINE_HOST_STORE_H
#define NET002_OFFLINE_HOST_STORE_H
/* Phase 9 NET-002 HOST development scope ONLY. No ESP flash/NVS integration,
 * power-loss persistence, capacity approval, or production-ready offline claim.
 * Fixed demo/test maxima below are implementation limits, not ship policy. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#define NET002_HOST_LATEST_MAX 256u
#define NET002_HOST_JOURNAL_CAP 8u
#define NET002_HOST_EVENT_TEXT_MAX 40u

typedef struct {
    uint32_t event_id;
    uint32_t monotonic_ms;
    char text[NET002_HOST_EVENT_TEXT_MAX];
} net002_host_critical_event;
typedef struct {
    uint8_t latest[NET002_HOST_LATEST_MAX];
    size_t latest_len;
    bool has_latest;
    net002_host_critical_event journal[NET002_HOST_JOURNAL_CAP];
    size_t start;
    size_t count;
    uint32_t evicted_count;
} net002_host_offline_store;
static inline void net002_host_init(net002_host_offline_store *s) {
    if (s) memset(s, 0, sizeof(*s));
}
/* Atomic on failure: refuse NULL, zero or oversized data; old state retained. */
static inline bool net002_host_set_latest(net002_host_offline_store *s,
                                           const void *bytes,size_t len) {
    if (!s || !bytes || !len || len > NET002_HOST_LATEST_MAX) return false;
    memcpy(s->latest,bytes,len);
    if (len < NET002_HOST_LATEST_MAX) memset(s->latest+len,0,NET002_HOST_LATEST_MAX-len);
    s->latest_len=len;s->has_latest=true;return true;
}
/* Critical event overwrite never silent: evicted_count saturates at UINT32_MAX.
 * No string pointer retention; malformed entries fail without changing journal. */
static inline bool net002_host_add_critical(net002_host_offline_store *s,
                                      uint32_t id,uint32_t tick,const char *text) {
    size_t i,len=0,slot;
    if (!s || !text || id==0u) return false;
    while (len < NET002_HOST_EVENT_TEXT_MAX && text[len]) ++len;
    if (len == 0u || len == NET002_HOST_EVENT_TEXT_MAX) return false;
    if (s->count == NET002_HOST_JOURNAL_CAP) {
        slot=s->start;
        s->start=(s->start+1u)%NET002_HOST_JOURNAL_CAP;
        if (s->evicted_count != UINT32_MAX) s->evicted_count++;
    } else {
        slot=(s->start+s->count)%NET002_HOST_JOURNAL_CAP;
        s->count++;
    }
    s->journal[slot].event_id=id;s->journal[slot].monotonic_ms=tick;
    for(i=0u;i<=len;++i)s->journal[slot].text[i]=text[i];
    return true;
}
static inline bool net002_host_get_event(const net002_host_offline_store *s,
                                size_t index,net002_host_critical_event *out) {
    if (!s || !out || index>=s->count) return false;
    *out=s->journal[(s->start+index)%NET002_HOST_JOURNAL_CAP];return true;
}
#endif
