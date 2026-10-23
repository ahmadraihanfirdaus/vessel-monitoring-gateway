#ifndef PHASE9_B18_CHECKPOINT_HOST_H
#define PHASE9_B18_CHECKPOINT_HOST_H
/* Phase 9 B18 HOST-ONLY deterministic snapshot codec for testing restart.
 * NOT crash-durable, authenticated, encrypted, atomic-file, ESP32 NVS, or
 * a substitute for local alarm operation. File IO is supplied by the host
 * test harness. Never trust a checksum as device attestation. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "net002_offline_host_store.h"
#include "phase9_b8_ack_window.h"

#define VG_B18_SNAPSHOT_MAX 768u
#define VG_B18_SNAPSHOT_VERSION 1u
#define VG_B18_DEVICE_TAG 0xB18005F1u /* host fixture identity only */

typedef struct { uint8_t *data; size_t cap, pos; bool ok; } vg_b18_writer;
typedef struct { const uint8_t *data; size_t len, pos; bool ok; } vg_b18_reader;

static inline void vg_b18_w8(vg_b18_writer *w, uint8_t value) {
    if (!w->ok || w->pos >= w->cap) { w->ok=false; return; }
    w->data[w->pos++] = value;
}
static inline void vg_b18_w32(vg_b18_writer *w, uint32_t v) {
    for (unsigned i=0u; i<4u; ++i) vg_b18_w8(w,(uint8_t)(v>>(8u*i)));
}
static inline uint8_t vg_b18_r8(vg_b18_reader *r) {
    if (!r->ok || r->pos >= r->len) { r->ok=false; return 0u; }
    return r->data[r->pos++];
}
static inline uint32_t vg_b18_r32(vg_b18_reader *r) {
    uint32_t v=0u;
    for (unsigned i=0u; i<4u; ++i) v |= ((uint32_t)vg_b18_r8(r)) << (8u*i);
    return v;
}
static inline uint32_t vg_b18_crc32(const uint8_t *buf,size_t n) {
    uint32_t crc=UINT32_MAX;
    for (size_t i=0u;i<n;++i) {
        crc^=(uint32_t)buf[i];
        for (unsigned bit=0u;bit<8u;++bit)
            crc = (crc>>1u) ^ ((crc & 1u) ? UINT32_C(0xEDB88320) : 0u);
    }
    return ~crc;
}
static inline bool vg_b18_valid(const net002_host_offline_store *s) {
    if (!s || s->count>NET002_HOST_JOURNAL_CAP ||
        s->start>=NET002_HOST_JOURNAL_CAP ||
        s->latest_len>NET002_HOST_LATEST_MAX ||
        (s->has_latest ? s->latest_len==0u : s->latest_len!=0u)) return false;
    for (size_t i=0u;i<s->count;++i) {
        net002_host_critical_event e;
        if (!net002_host_get_event(s,i,&e) || e.event_id==0u) return false;
        size_t text_len=0u;
        while(text_len<NET002_HOST_EVENT_TEXT_MAX && e.text[text_len]) ++text_len;
        if (text_len==0u || text_len==NET002_HOST_EVENT_TEXT_MAX) return false;
    }
    return true;
}
/* Snapshot of last CONFIRMED ACK only; the pending request is never persisted.
 * A pending ACK at process death MUST be independently reconciled/replayed. */
static inline bool vg_b18_pack(const net002_host_offline_store *s,
    const phase9_b8_ack_window *ack,uint32_t device_tag,
    uint8_t *out,size_t cap,size_t *written)
{
    if (!out || !written || !ack || !vg_b18_valid(s) ||
        device_tag==0u || cap>VG_B18_SNAPSHOT_MAX) return false;
    uint8_t tmp[VG_B18_SNAPSHOT_MAX]={0};
    vg_b18_writer w={tmp,cap,0u,true};
    vg_b18_w8(&w,'V');vg_b18_w8(&w,'G');vg_b18_w8(&w,'1');vg_b18_w8(&w,'8');
    vg_b18_w8(&w,VG_B18_SNAPSHOT_VERSION);
    vg_b18_w32(&w,device_tag);
    vg_b18_w8(&w,s->has_latest ? 1u : 0u);
    vg_b18_w32(&w,(uint32_t)s->latest_len);
    vg_b18_w8(&w,(uint8_t)s->count);
    vg_b18_w32(&w,s->evicted_count);
    vg_b18_w32(&w,ack->last_accepted_sequence);
    for (size_t i=0u;i<s->latest_len;++i) vg_b18_w8(&w,s->latest[i]);
    for (size_t i=0u;i<s->count;++i) {
        net002_host_critical_event e;
        if (!net002_host_get_event(s,i,&e)) return false;
        size_t len=0u;
        while(len<NET002_HOST_EVENT_TEXT_MAX && e.text[len]) ++len;
        vg_b18_w32(&w,e.event_id);vg_b18_w32(&w,e.monotonic_ms);
        vg_b18_w8(&w,(uint8_t)len);
        for(size_t j=0u;j<len;++j) vg_b18_w8(&w,(uint8_t)e.text[j]);
    }
    if (!w.ok || cap-w.pos<4u) return false;
    uint32_t crc=vg_b18_crc32(tmp,w.pos);
    vg_b18_w32(&w,crc);
    if (!w.ok) return false;
    memcpy(out,tmp,w.pos);*written=w.pos;
    return true;
}
/* Atomic on validation failure: never modify either target; reject trailing,
 * truncated, cross-identity, corrupt, and over-capacity snapshots. */
static inline bool vg_b18_unpack(const uint8_t *raw,size_t n,
    uint32_t expected_device, net002_host_offline_store *out,
    phase9_b8_ack_window *ack)
{
    if (!raw || !out || !ack || expected_device==0u ||
        n<27u || n>VG_B18_SNAPSHOT_MAX) return false;
    vg_b18_reader r={raw,n-4u,0u,true};
    if (vg_b18_r8(&r)!='V' || vg_b18_r8(&r)!='G' ||
        vg_b18_r8(&r)!='1' || vg_b18_r8(&r)!='8' ||
        vg_b18_r8(&r)!=VG_B18_SNAPSHOT_VERSION ||
        vg_b18_r32(&r)!=expected_device) return false;
    uint8_t has_latest=vg_b18_r8(&r);
    uint32_t latest_len=vg_b18_r32(&r);
    uint8_t count=vg_b18_r8(&r);
    uint32_t evicted=vg_b18_r32(&r);
    uint32_t highwater=vg_b18_r32(&r);
    if (!r.ok || has_latest>1u || latest_len>NET002_HOST_LATEST_MAX ||
        count>NET002_HOST_JOURNAL_CAP ||
        (has_latest==0u && latest_len!=0u) ||
        (has_latest==1u && latest_len==0u)) return false;
    net002_host_offline_store temp;
    net002_host_init(&temp);
    for (uint32_t i=0u;i<latest_len;++i) temp.latest[i]=vg_b18_r8(&r);
    temp.latest_len=(size_t)latest_len;temp.has_latest=has_latest==1u;
    temp.evicted_count=evicted;
    for (uint8_t i=0u;i<count;++i) {
        uint32_t id=vg_b18_r32(&r);
        uint32_t tick=vg_b18_r32(&r);
        uint8_t len=vg_b18_r8(&r);
        char text[NET002_HOST_EVENT_TEXT_MAX]={0};
        if (!r.ok || id==0u || len==0u || len>=NET002_HOST_EVENT_TEXT_MAX ||
            (size_t)len>r.len-r.pos) return false;
        for (uint8_t j=0u;j<len;++j) {
            uint8_t ch=vg_b18_r8(&r);
            if (ch==0u) return false;
            text[j]=(char)ch;
        }
        if (!net002_host_add_critical(&temp,id,tick,text)) return false;
    }
    if (!r.ok || r.pos!=r.len || !vg_b18_valid(&temp)) return false;
    uint32_t stored_crc=(uint32_t)raw[n-4u] |
        ((uint32_t)raw[n-3u]<<8u) | ((uint32_t)raw[n-2u]<<16u) |
        ((uint32_t)raw[n-1u]<<24u);
    if (stored_crc!=vg_b18_crc32(raw,n-4u)) return false;
    phase9_b8_ack_window reset_ack;
    phase9_b8_ack_init(&reset_ack);
    reset_ack.last_accepted_sequence=highwater;
    *out=temp;
    *ack=reset_ack;
    return true;
}
#endif
