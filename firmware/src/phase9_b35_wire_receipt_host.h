#ifndef PHASE9_B35_WIRE_RECEIPT_HOST_H
#define PHASE9_B35_WIRE_RECEIPT_HOST_H
/* HOST-ONLY canonical metadata receipt: not complete checkpoint storage.
 * CRC32 is not authentication. The independently validated envelope and
 * readback bytes MUST come from trusted external policy before verification.
 * Does not implement durable CAS, cryptographic signatures, NVS or concurrency. */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "phase9_b34_publish_envelope_host.h"
#define VG_B35_WIRE_LENGTH 72u
#define VG_B35_WIRE_VERSION 1u

typedef struct {
    uint32_t device_tag,primary_domain,secondary_domain;
    uint32_t checkpoint_generation,last_accepted_sequence,checkpoint_crc32;
    uint64_t confirmed_revision,accepted_round,primary_epoch,secondary_epoch;
} vg_b35_receipt;

static inline void vg_b35_w64(vg_b18_writer *w,uint64_t v) {
    for(unsigned i=0u;i<8u;i++)vg_b18_w8(w,(uint8_t)(v>>(8u*i)));
}
static inline uint64_t vg_b35_r64(vg_b18_reader *r) {
    uint64_t value=0u;
    for(unsigned i=0u;i<8u;i++)value|=(uint64_t)vg_b18_r8(r)<<(8u*i);
    return value;
}
/* Cross-check every metadata projection before touching caller output. */
static inline bool vg_b35_project(const vg_b34_envelope *e,
    const uint8_t *snapshot,size_t snapshot_len,vg_b35_receipt *receipt) {
    if(!e || !snapshot || !receipt || !snapshot_len ||
       snapshot_len>VG_B19_SLOT_MAX ||
       e->version!=VG_B34_ENVELOPE_VERSION ||
       e->valid_marker!=VG_B34_ENVELOPE_VALID ||
       !e->fence.device_tag || !e->fence.primary_domain ||
       !e->fence.secondary_domain ||
       e->fence.primary_domain==e->fence.secondary_domain ||
       !e->checkpoint_generation || !e->last_accepted_sequence ||
       !e->externally_confirmed_revision ||
       !e->fence.accepted_round || !e->fence.primary_epoch ||
       !e->fence.secondary_epoch ||
       e->checkpoint_generation!=e->state.generation ||
       e->last_accepted_sequence!=e->state.ack.last_accepted_sequence ||
       e->state.ack.pending ||
       e->checkpoint_generation!=e->fence.last_witness.generation ||
       e->last_accepted_sequence!=e->fence.last_witness.confirmed_ack ||
       e->guard.accepted_round!=e->fence.accepted_round ||
       e->guard.primary.device_tag!=e->fence.device_tag ||
       e->guard.secondary.device_tag!=e->fence.device_tag ||
       e->guard.primary.source_domain!=e->fence.primary_domain ||
       e->guard.secondary.source_domain!=e->fence.secondary_domain ||
       e->guard.primary.last_observation_epoch!=e->fence.primary_epoch ||
       e->guard.secondary.last_observation_epoch!=e->fence.secondary_epoch ||
       e->guard.primary.last_witness.generation!=e->checkpoint_generation ||
       e->guard.secondary.last_witness.generation!=e->checkpoint_generation ||
       e->guard.primary.last_witness.confirmed_ack!=e->last_accepted_sequence ||
       e->guard.secondary.last_witness.confirmed_ack!=e->last_accepted_sequence ||
       e->externally_confirmed_revision!=e->fence.revision ||
       e->checkpoint_crc32!=vg_b18_crc32(snapshot,snapshot_len))return false;
    vg_b35_receipt temporary={0};
    temporary.device_tag=e->fence.device_tag;
    temporary.primary_domain=e->fence.primary_domain;
    temporary.secondary_domain=e->fence.secondary_domain;
    temporary.checkpoint_generation=e->checkpoint_generation;
    temporary.last_accepted_sequence=e->last_accepted_sequence;
    temporary.checkpoint_crc32=e->checkpoint_crc32;
    temporary.confirmed_revision=e->externally_confirmed_revision;
    temporary.accepted_round=e->fence.accepted_round;
    temporary.primary_epoch=e->fence.primary_epoch;
    temporary.secondary_epoch=e->fence.secondary_epoch;
    *receipt=temporary;
    return true;
}
/* Writes only exact 72-byte little-endian canonical format (never struct copy).
 * Caller output and length stay unchanged on any failure. */
static inline bool vg_b35_encode(const vg_b34_envelope *e,
    const uint8_t *snapshot,size_t snapshot_len,
    uint8_t *out,size_t capacity,size_t *written) {
    if(!e || !snapshot || !out || !written ||
       capacity<VG_B35_WIRE_LENGTH)return false;
    vg_b31_region a,b,c,d;
    if(!vg_b31_region_of(e,sizeof(*e),&a) ||
       !vg_b31_region_of(snapshot,snapshot_len,&b) ||
       !vg_b31_region_of(out,VG_B35_WIRE_LENGTH,&c) ||
       !vg_b31_region_of(written,sizeof(*written),&d) ||
       vg_b31_overlaps(a,b) || vg_b31_overlaps(a,c) ||
       vg_b31_overlaps(a,d) || vg_b31_overlaps(b,c) ||
       vg_b31_overlaps(b,d) || vg_b31_overlaps(c,d))return false;
    vg_b35_receipt r;
    if(!vg_b35_project(e,snapshot,snapshot_len,&r))return false;
    uint8_t temp[VG_B35_WIRE_LENGTH]={0};
    vg_b18_writer w={temp,sizeof(temp),0u,true};
    vg_b18_w8(&w,'V');vg_b18_w8(&w,'G');
    vg_b18_w8(&w,'3');vg_b18_w8(&w,'5');
    vg_b18_w32(&w,VG_B35_WIRE_VERSION);
    vg_b18_w32(&w,VG_B35_WIRE_LENGTH);
    vg_b18_w32(&w,r.device_tag);
    vg_b18_w32(&w,r.primary_domain);
    vg_b18_w32(&w,r.secondary_domain);
    vg_b18_w32(&w,r.checkpoint_generation);
    vg_b18_w32(&w,r.last_accepted_sequence);
    vg_b18_w32(&w,r.checkpoint_crc32);
    vg_b35_w64(&w,r.confirmed_revision);
    vg_b35_w64(&w,r.accepted_round);
    vg_b35_w64(&w,r.primary_epoch);
    vg_b35_w64(&w,r.secondary_epoch);
    if(!w.ok || w.pos!=VG_B35_WIRE_LENGTH-4u)return false;
    vg_b18_w32(&w,vg_b18_crc32(temp,w.pos));
    if(!w.ok || w.pos!=VG_B35_WIRE_LENGTH)return false;
    memcpy(out,temp,sizeof(temp));*written=sizeof(temp);
    return true;
}
/* Independently revalidated B34 envelope is a REQUIRED comparator. A
 * forged receipt with recomputed CRC still cannot bypass disagreement with
 * the trusted envelope, but this does not authenticate that envelope. */
static inline bool vg_b35_verify(const uint8_t *raw,size_t len,
    const vg_b34_envelope *trusted,const uint8_t *snapshot,
    size_t snapshot_len,vg_b35_receipt *verified) {
    if(!raw || !trusted || !snapshot || !verified ||
       len!=VG_B35_WIRE_LENGTH)return false;
    vg_b31_region a,b,c,d;
    if(!vg_b31_region_of(raw,len,&a) ||
       !vg_b31_region_of(trusted,sizeof(*trusted),&b) ||
       !vg_b31_region_of(snapshot,snapshot_len,&c) ||
       !vg_b31_region_of(verified,sizeof(*verified),&d) ||
       vg_b31_overlaps(a,b) || vg_b31_overlaps(a,c) ||
       vg_b31_overlaps(a,d) || vg_b31_overlaps(b,c) ||
       vg_b31_overlaps(b,d) || vg_b31_overlaps(c,d))return false;
    vg_b35_receipt expected;
    if(!vg_b35_project(trusted,snapshot,snapshot_len,&expected))return false;
    uint32_t footer=(uint32_t)raw[68u]|((uint32_t)raw[69u]<<8u)|
       ((uint32_t)raw[70u]<<16u)|((uint32_t)raw[71u]<<24u);
    if(footer!=vg_b18_crc32(raw,VG_B35_WIRE_LENGTH-4u))return false;
    vg_b18_reader r={raw,VG_B35_WIRE_LENGTH-4u,0u,true};
    if(vg_b18_r8(&r)!='V' || vg_b18_r8(&r)!='G' ||
       vg_b18_r8(&r)!='3' || vg_b18_r8(&r)!='5' ||
       vg_b18_r32(&r)!=VG_B35_WIRE_VERSION ||
       vg_b18_r32(&r)!=VG_B35_WIRE_LENGTH)return false;
    vg_b35_receipt got={0};
    got.device_tag=vg_b18_r32(&r);
    got.primary_domain=vg_b18_r32(&r);
    got.secondary_domain=vg_b18_r32(&r);
    got.checkpoint_generation=vg_b18_r32(&r);
    got.last_accepted_sequence=vg_b18_r32(&r);
    got.checkpoint_crc32=vg_b18_r32(&r);
    got.confirmed_revision=vg_b35_r64(&r);
    got.accepted_round=vg_b35_r64(&r);
    got.primary_epoch=vg_b35_r64(&r);
    got.secondary_epoch=vg_b35_r64(&r);
    if(!r.ok || r.pos!=VG_B35_WIRE_LENGTH-4u ||
       got.device_tag!=expected.device_tag ||
       got.primary_domain!=expected.primary_domain ||
       got.secondary_domain!=expected.secondary_domain ||
       got.checkpoint_generation!=expected.checkpoint_generation ||
       got.last_accepted_sequence!=expected.last_accepted_sequence ||
       got.checkpoint_crc32!=expected.checkpoint_crc32 ||
       got.confirmed_revision!=expected.confirmed_revision ||
       got.accepted_round!=expected.accepted_round ||
       got.primary_epoch!=expected.primary_epoch ||
       got.secondary_epoch!=expected.secondary_epoch)return false;
    *verified=got;return true;
}
#endif
