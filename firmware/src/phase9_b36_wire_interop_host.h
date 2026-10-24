#ifndef PHASE9_B36_WIRE_INTEROP_HOST_H
#define PHASE9_B36_WIRE_INTEROP_HOST_H
/* Test-only independent B35 canonical reference: no DB, keys, NVS or transport.
 * Manual indexed stores intentionally avoid B35 stream writer and reader.
 * CRC32 detects errors but does not authenticate any record. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b35_wire_receipt_host.h"
#define VG_B36_EXPECTED_WIRE_LENGTH 72u
static inline void vg_b36_put32(uint8_t *p,uint32_t v){
    for(unsigned i=0u;i<4u;i++)p[i]=(uint8_t)(v>>(8u*i));
}
static inline void vg_b36_put64(uint8_t *p,uint64_t v){
    for(unsigned i=0u;i<8u;i++)p[i]=(uint8_t)(v>>(8u*i));
}
static inline uint32_t vg_b36_get32(const uint8_t *p){
    uint32_t v=0u;for(unsigned i=0u;i<4u;i++)v|=(uint32_t)p[i]<<(8u*i);return v;
}
static inline uint64_t vg_b36_get64(const uint8_t *p){
    uint64_t v=0u;for(unsigned i=0u;i<8u;i++)v|=(uint64_t)p[i]<<(8u*i);return v;
}
static inline bool vg_b36_reference_encode(const vg_b35_receipt *r,uint8_t *out,size_t len){
    if(!r || !out || len!=VG_B36_EXPECTED_WIRE_LENGTH || !r->device_tag ||
       !r->primary_domain || !r->secondary_domain ||
       r->primary_domain==r->secondary_domain ||
       !r->checkpoint_generation || !r->last_accepted_sequence ||
       !r->confirmed_revision || !r->accepted_round ||
       !r->primary_epoch || !r->secondary_epoch)return false;
    uint8_t local[VG_B36_EXPECTED_WIRE_LENGTH]={0};
    local[0]='V';local[1]='G';local[2]='3';local[3]='5';
    vg_b36_put32(local+4u,1u);vg_b36_put32(local+8u,72u);
    vg_b36_put32(local+12u,r->device_tag);
    vg_b36_put32(local+16u,r->primary_domain);
    vg_b36_put32(local+20u,r->secondary_domain);
    vg_b36_put32(local+24u,r->checkpoint_generation);
    vg_b36_put32(local+28u,r->last_accepted_sequence);
    vg_b36_put32(local+32u,r->checkpoint_crc32);
    vg_b36_put64(local+36u,r->confirmed_revision);
    vg_b36_put64(local+44u,r->accepted_round);
    vg_b36_put64(local+52u,r->primary_epoch);
    vg_b36_put64(local+60u,r->secondary_epoch);
    vg_b36_put32(local+68u,vg_b18_crc32(local,68u));
    memcpy(out,local,sizeof(local));return true;
}
static inline bool vg_b36_reference_decode(const uint8_t *raw,size_t len,vg_b35_receipt *out){
    if(!raw || !out || len!=VG_B36_EXPECTED_WIRE_LENGTH ||
       raw[0]!='V' || raw[1]!='G' || raw[2]!='3' || raw[3]!='5' ||
       vg_b36_get32(raw+4u)!=1u || vg_b36_get32(raw+8u)!=72u ||
       vg_b36_get32(raw+68u)!=vg_b18_crc32(raw,68u))return false;
    vg_b35_receipt temporary={0};
    temporary.device_tag=vg_b36_get32(raw+12u);
    temporary.primary_domain=vg_b36_get32(raw+16u);
    temporary.secondary_domain=vg_b36_get32(raw+20u);
    temporary.checkpoint_generation=vg_b36_get32(raw+24u);
    temporary.last_accepted_sequence=vg_b36_get32(raw+28u);
    temporary.checkpoint_crc32=vg_b36_get32(raw+32u);
    temporary.confirmed_revision=vg_b36_get64(raw+36u);
    temporary.accepted_round=vg_b36_get64(raw+44u);
    temporary.primary_epoch=vg_b36_get64(raw+52u);
    temporary.secondary_epoch=vg_b36_get64(raw+60u);
    if(!temporary.device_tag || !temporary.primary_domain ||
       !temporary.secondary_domain ||
       temporary.primary_domain==temporary.secondary_domain ||
       !temporary.checkpoint_generation || !temporary.last_accepted_sequence ||
       !temporary.confirmed_revision || !temporary.accepted_round ||
       !temporary.primary_epoch || !temporary.secondary_epoch)return false;
    *out=temporary;return true;
}
#endif
