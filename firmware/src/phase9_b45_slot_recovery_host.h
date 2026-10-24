#ifndef PHASE9_B45_SLOT_RECOVERY_HOST_H
#define PHASE9_B45_SLOT_RECOVERY_HOST_H
/* HOST ONLY: choose a HMAC-verified B44 snapshot among two supplied readbacks.
 * Both image slots, trusted floor, source ID and 32-byte key are CALLER inputs;
 * no I/O, persistence, concurrency, fsync, durability or ESP32 NVS support.
 * DENY split-brain with equal generations and different authenticated bytes.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b44_nonce_snapshot_host.h"

static inline bool vg_b45_region_ok(const void *p,size_t n,vg_b31_region *r){
    return p&&n>0u&&vg_b31_region_of(p,n,r);
}
static inline bool vg_b45_select_two_slot(const uint8_t *slot0,size_t len0,
    const uint8_t *slot1,size_t len1,uint64_t trusted_generation_floor,
    uint64_t source_id,const uint8_t *key,size_t key_len,
    vg_b43_nonce_ledger *out,uint64_t *out_generation,uint8_t *out_slot){
    vg_b31_region regions[6];
    const void *ptrs[6]={slot0,slot1,key,out,out_generation,out_slot};
    const size_t sizes[6]={len0,len1,key_len,sizeof(*out),
                              sizeof(*out_generation),sizeof(*out_slot)};
    if(!key||!out||!out_generation||!out_slot||key_len!=32u||
       !trusted_generation_floor||!source_id||
       (len0!=0u&&len0!=VG_B44_SNAPSHOT_LENGTH)||
       (len1!=0u&&len1!=VG_B44_SNAPSHOT_LENGTH)||
       (len0==0u&&len1==0u))return false;
    for(size_t i=0u;i<6u;++i){
        if(i<2u&&sizes[i]==0u){
            if(ptrs[i])return false; /* absence is explicit NULL/zero only */
            continue;
        }
        if(!vg_b45_region_ok(ptrs[i],sizes[i],&regions[i]))return false;
        for(size_t j=0u;j<i;++j){
            if(j<2u&&sizes[j]==0u)continue;
            if(vg_b31_overlaps(regions[i],regions[j]))return false;
        }
    }
    vg_b43_nonce_ledger candidates[2];
    uint64_t generations[2]={0u,0u};
    bool valid[2]={false,false};
    if(len0==VG_B44_SNAPSHOT_LENGTH){
        valid[0]=vg_b44_restore_nonce_ledger(slot0,len0,trusted_generation_floor,
                   source_id,key,key_len,&candidates[0],&generations[0]);
    }
    if(len1==VG_B44_SNAPSHOT_LENGTH){
        valid[1]=vg_b44_restore_nonce_ledger(slot1,len1,trusted_generation_floor,
                   source_id,key,key_len,&candidates[1],&generations[1]);
    }
    if(!valid[0]&&!valid[1]){
        vg_b40_zero(candidates,sizeof(candidates));return false;
    }
    if(valid[0]&&valid[1]&&generations[0]==generations[1]&&
       memcmp(slot0,slot1,VG_B44_SNAPSHOT_LENGTH)!=0){
        vg_b40_zero(candidates,sizeof(candidates));return false;
    }
    unsigned int chosen=valid[0]&&(!valid[1]||generations[0]>=generations[1])?0u:1u;
    memcpy(out,&candidates[chosen],sizeof(*out));
    *out_generation=generations[chosen];
    *out_slot=(uint8_t)chosen;
    vg_b40_zero(candidates,sizeof(candidates));return true;
}
#endif
