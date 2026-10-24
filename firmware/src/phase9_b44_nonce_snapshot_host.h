#ifndef PHASE9_B44_NONCE_SNAPSHOT_HOST_H
#define PHASE9_B44_NONCE_SNAPSHOT_HOST_H
/* HOST-ONLY HMAC-sealed, deterministic bounded nonce-ledger serialization.
 * Restoring this snapshot after restart is conditional on trusted generation
 * floor and key provenance. NOT crash-atomic storage, trusted monotonic counter,
 * secure key provisioning, cross-thread CAS, or ESP32/NVS integration. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b43_nonce_ledger_host.h"
#define VG_B44_SNAPSHOT_LENGTH 192u
#define VG_B44_BODY_LENGTH 160u
#define VG_B44_VERSION 1u
static inline uint32_t vg_b44_get32(const uint8_t *p){
    uint32_t v=0u;for(unsigned int i=0u;i<4u;++i)v|=(uint32_t)p[i]<<(8u*i);return v;
}
static inline uint64_t vg_b44_get64(const uint8_t *p){
    uint64_t v=0u;for(unsigned int i=0u;i<8u;++i)v|=(uint64_t)p[i]<<(8u*i);return v;
}
static inline bool vg_b44_region(const void *p,size_t len,vg_b31_region *out){
    return p&&vg_b31_region_of(p,len,out);
}
static inline bool vg_b44_disjoint4(const void *a,size_t alen,
    const void *b,size_t blen,const void *c,size_t clen,
    const void *d,size_t dlen){
    vg_b31_region regions[4];
    if(!vg_b44_region(a,alen,&regions[0])||!vg_b44_region(b,blen,&regions[1])||
       !vg_b44_region(c,clen,&regions[2])||!vg_b44_region(d,dlen,&regions[3]))return false;
    for(size_t i=0u;i<4u;++i)for(size_t j=0u;j<i;++j)
        if(vg_b31_overlaps(regions[i],regions[j]))return false;
    return true;
}
static inline bool vg_b44_seal_nonce_ledger(const vg_b43_nonce_ledger *ledger,
    uint64_t generation,uint64_t source_id,const uint8_t *key,size_t key_len,
    uint8_t *output,size_t output_len){
    static const uint8_t domain[]="VG_PHASE9_B44_LEDGER_SNAPSHOT_HMAC_V1";
    if(!ledger||!key||!output||generation==0u||source_id==0u||
       key_len!=32u||output_len!=VG_B44_SNAPSHOT_LENGTH||
       !vg_b43_ledger_valid(ledger)||
       !vg_b44_disjoint4(ledger,sizeof(*ledger),key,key_len,output,output_len,
                         &generation,sizeof(generation)))return false;
    uint8_t temporary[VG_B44_SNAPSHOT_LENGTH];memset(temporary,0,sizeof(temporary));
    memcpy(temporary,"VG44",4u);
    vg_b40_put_le32(temporary+4u,VG_B44_VERSION);
    vg_b40_put_le64(temporary+8u,generation);
    vg_b40_put_le64(temporary+16u,source_id);
    vg_b40_put_le32(temporary+24u,ledger->count);
    memcpy(temporary+32u,ledger->used,sizeof(ledger->used));
    bool good=vg_b40_hmac(key,key_len,domain,sizeof(domain),temporary,
                          VG_B44_BODY_LENGTH,temporary+VG_B44_BODY_LENGTH);
    if(good)memcpy(output,temporary,sizeof(temporary));
    vg_b40_zero(temporary,sizeof(temporary));return good;
}
static inline bool vg_b44_restore_nonce_ledger(const uint8_t *serialized,
    size_t serialized_len,uint64_t trusted_min_generation,
    uint64_t expected_source_id,const uint8_t *key,size_t key_len,
    vg_b43_nonce_ledger *output,uint64_t *accepted_generation){
    static const uint8_t domain[]="VG_PHASE9_B44_LEDGER_SNAPSHOT_HMAC_V1";
    if(!serialized||!key||!output||!accepted_generation||
       serialized_len!=VG_B44_SNAPSHOT_LENGTH||key_len!=32u||
       trusted_min_generation==0u||expected_source_id==0u||
       !vg_b44_disjoint4(serialized,serialized_len,key,key_len,
            output,sizeof(*output),accepted_generation,sizeof(*accepted_generation)))return false;
    /* Authenticate before inspecting semantic contents or modifying output. */
    uint8_t tag[32];
    bool computed=vg_b40_hmac(key,key_len,domain,sizeof(domain),serialized,
                              VG_B44_BODY_LENGTH,tag);
    bool authenticated=computed&&vg_b40_ct_eq32(tag,serialized+VG_B44_BODY_LENGTH);
    vg_b40_zero(tag,sizeof(tag));if(!authenticated)return false;
    if(memcmp(serialized,"VG44",4u)||vg_b44_get32(serialized+4u)!=VG_B44_VERSION||
       vg_b44_get32(serialized+28u)!=0u||
       vg_b44_get64(serialized+8u)<trusted_min_generation||
       vg_b44_get64(serialized+16u)!=expected_source_id)return false;
    vg_b43_nonce_ledger candidate;vg_b43_ledger_init(&candidate);
    candidate.count=vg_b44_get32(serialized+24u);
    memcpy(candidate.used,serialized+32u,sizeof(candidate.used));
    bool valid=vg_b43_ledger_valid(&candidate);
    if(!valid){vg_b40_zero(&candidate,sizeof(candidate));return false;}
    uint64_t generation=vg_b44_get64(serialized+8u);
    memcpy(output,&candidate,sizeof(candidate));
    *accepted_generation=generation;
    vg_b40_zero(&candidate,sizeof(candidate));return true;
}
#endif
