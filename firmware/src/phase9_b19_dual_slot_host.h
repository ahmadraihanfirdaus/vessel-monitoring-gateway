#ifndef PHASE9_B19_DUAL_SLOT_HOST_H
#define PHASE9_B19_DUAL_SLOT_HOST_H
/* HOST development only. This bounded dual-slot envelope is not crash-atomic
 * disk IO, NVS flash integration, cryptographic authentication or certified
 * device storage. A bad newest slot may replay conservative older ACK data.
 * Device tag is fixture identity, NOT cryptographic proof. */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "phase9_b18_checkpoint_host.h"
#define VG_B19_SLOT_MAX 800u
#define VG_B19_SLOT_VERSION 1u
#define VG_B19_SLOT_HEAD 15u
#define VG_B19_SLOT_OVERHEAD 19u

typedef struct {
    net002_host_offline_store store;
    phase9_b8_ack_window ack;
    uint32_t generation;
} vg_b19_restored;

/* Output and size are unchanged on every validation failure. */
static inline bool vg_b19_wrap(const net002_host_offline_store *store,
    const phase9_b8_ack_window *ack,uint32_t device_tag,uint32_t generation,
    uint8_t *out,size_t cap,size_t *written) {
    if (!store || !ack || !out || !written || !device_tag || !generation ||
        cap>VG_B19_SLOT_MAX || cap<VG_B19_SLOT_OVERHEAD) return false;
    uint8_t snapshot[VG_B18_SNAPSHOT_MAX];size_t payload_size=0u;
    if (!vg_b18_pack(store,ack,device_tag,snapshot,sizeof(snapshot),&payload_size) ||
        payload_size>UINT16_MAX || payload_size>cap-VG_B19_SLOT_OVERHEAD) return false;
    uint8_t temp[VG_B19_SLOT_MAX]={0};
    vg_b18_writer w={temp,cap,0u,true};
    vg_b18_w8(&w,'V');vg_b18_w8(&w,'G');vg_b18_w8(&w,'1');vg_b18_w8(&w,'9');
    vg_b18_w8(&w,VG_B19_SLOT_VERSION);
    vg_b18_w32(&w,device_tag);vg_b18_w32(&w,generation);
    vg_b18_w8(&w,(uint8_t)(payload_size & 0xffu));
    vg_b18_w8(&w,(uint8_t)(payload_size >> 8u));
    for(size_t i=0u;i<payload_size;++i)vg_b18_w8(&w,snapshot[i]);
    if(!w.ok || cap-w.pos<4u)return false;
    vg_b18_w32(&w,vg_b18_crc32(temp,w.pos));
    if(!w.ok)return false;
    memcpy(out,temp,w.pos);*written=w.pos;return true;
}

/* Decode checks the complete envelope and embedded B18 snapshot CRC/identity.
 * Untrusted bytes never modify destination on failure. */
static inline bool vg_b19_decode(const uint8_t *raw,size_t n,
    uint32_t expected_device,vg_b19_restored *dest) {
    if (!raw || !dest || !expected_device ||
        n<VG_B19_SLOT_OVERHEAD+27u || n>VG_B19_SLOT_MAX) return false;
    vg_b18_reader r={raw,n-4u,0u,true};
    if(vg_b18_r8(&r)!='V'||vg_b18_r8(&r)!='G'||
       vg_b18_r8(&r)!='1'||vg_b18_r8(&r)!='9'||
       vg_b18_r8(&r)!=VG_B19_SLOT_VERSION||
       vg_b18_r32(&r)!=expected_device)return false;
    uint32_t generation=vg_b18_r32(&r);
    uint32_t count=(uint32_t)vg_b18_r8(&r);
    count|=(uint32_t)vg_b18_r8(&r)<<8u;
    if(!r.ok||!generation||count<27u ||
        count!=r.len-r.pos)return false;
    uint32_t expected_crc=(uint32_t)raw[n-4u]|
        ((uint32_t)raw[n-3u]<<8u)|((uint32_t)raw[n-2u]<<16u)|
        ((uint32_t)raw[n-1u]<<24u);
    if (expected_crc!=vg_b18_crc32(raw,n-4u)) return false;
    vg_b19_restored temp;
    memset(&temp,0,sizeof(temp));
    if(!vg_b18_unpack(raw+r.pos,(size_t)count,expected_device,
        &temp.store,&temp.ack)) return false;
    temp.generation=generation;*dest=temp;return true;
}

/* Pick highest valid generation, fail closed on ambiguous same-generation
 * but non-identical snapshots. Fallback NEVER promotes older pending ACKs.
 * May conservatively re-send already delivered entries (backend dedup needed).
 * A clock/sequence rollover must be decided externally, never guessed here. */
static inline bool vg_b19_select(const uint8_t *slot_a,size_t len_a,
    const uint8_t *slot_b,size_t len_b,uint32_t device_tag,
    vg_b19_restored *destination,bool *degraded) {
    if(!destination || !degraded || !device_tag)return false;
    vg_b19_restored a,b;
    bool av=vg_b19_decode(slot_a,len_a,device_tag,&a);
    bool bv=vg_b19_decode(slot_b,len_b,device_tag,&b);
    if(!av && !bv)return false;
    if(av && bv && a.generation==b.generation) {
        if(len_a!=len_b || memcmp(slot_a,slot_b,len_a)!=0)return false;
    }
    *destination=(!bv || (av && a.generation>=b.generation)) ? a:b;
    *degraded=!(av && bv);
    return true;
}
static inline bool vg_b19_next_generation(uint32_t previous,uint32_t *next) {
    if(!next || previous==UINT32_MAX)return false;
    *next=previous+1u;return true;
}
#endif
