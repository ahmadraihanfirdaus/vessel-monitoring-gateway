#ifndef PHASE9_B46_STAGE_READBACK_HOST_H
#define PHASE9_B46_STAGE_READBACK_HOST_H
/* Host-only publication ADMISSION for a simulated two-slot nonce-ledger update.
 * External code supplies current slots, proposed signed bytes AND independent
 * readback; this function does no writes, IO, fsync, NVS, CAS or key provisioning.
 * Requires (1) selected current B45 signed image, (2) next generation exactly
 * current+1, (3) exactly one new nonce appended to the ledger, (4) exact signed
 * byte readback of staged candidate, (5) target is inactive slot, and (6)
 * readback selected as unique winner under B45 authenticated recovery rules.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b45_slot_recovery_host.h"

static inline bool vg_b46_admit_staged_readback(
    const uint8_t *slot0,size_t len0,const uint8_t *slot1,size_t len1,
    const uint8_t *staged,size_t staged_len,
    const uint8_t *readback,size_t readback_len,
    uint64_t trusted_floor,uint64_t source_id,
    const uint8_t *key,size_t key_len,
    vg_b43_nonce_ledger *out,uint64_t *out_generation,uint8_t *out_slot){
    const void *ptrs[8]={slot0,slot1,staged,readback,key,out,out_generation,out_slot};
    size_t sizes[8]={len0,len1,staged_len,readback_len,key_len,
                      sizeof(*out),sizeof(*out_generation),sizeof(*out_slot)};
    vg_b31_region regions[8];
    if(!staged||!readback||!key||!out||!out_generation||!out_slot||
       !trusted_floor||!source_id||key_len!=32u||
       staged_len!=VG_B44_SNAPSHOT_LENGTH||readback_len!=VG_B44_SNAPSHOT_LENGTH||
       (len0!=0u&&len0!=VG_B44_SNAPSHOT_LENGTH)||
       (len1!=0u&&len1!=VG_B44_SNAPSHOT_LENGTH)||
       (len0==0u&&len1==0u))return false;
    for(size_t i=0u;i<8u;++i){
        if(i<2u&&sizes[i]==0u){if(ptrs[i])return false;continue;}
        if(!vg_b45_region_ok(ptrs[i],sizes[i],&regions[i]))return false;
        for(size_t j=0u;j<i;++j){
            if(j<2u&&sizes[j]==0u)continue;
            if(vg_b31_overlaps(regions[i],regions[j]))return false;
        }
    }
    vg_b43_nonce_ledger current,planned,verified;
    memset(&current,0,sizeof(current));memset(&planned,0,sizeof(planned));
    memset(&verified,0,sizeof(verified));
    uint64_t current_gen=0u,proposed_gen=0u,verified_gen=0u;
    uint8_t active_slot=0u;
    bool accepted=false;
    do{
        if(!vg_b45_select_two_slot(slot0,len0,slot1,len1,trusted_floor,
             source_id,key,key_len,&current,&current_gen,&active_slot))break;
        if(current_gen==UINT64_MAX||current.count>=8u)break;
        if(!vg_b44_restore_nonce_ledger(staged,staged_len,trusted_floor,
             source_id,key,key_len,&planned,&proposed_gen))break;
        if(proposed_gen!=current_gen+UINT64_C(1)||
           planned.count!=current.count+1u||
           memcmp(planned.used,current.used,(size_t)current.count*16u)!=0)break;
        /* Host fixture simulates read-after-write; no external writes here. */
        if(memcmp(staged,readback,VG_B44_SNAPSHOT_LENGTH)!=0)break;
        if(!vg_b44_restore_nonce_ledger(readback,readback_len,trusted_floor,
             source_id,key,key_len,&verified,&verified_gen))break;
        if(verified_gen!=proposed_gen||
           memcmp(&verified,&planned,sizeof(verified))!=0)break;
        /* Simulate replacing only the INACTIVE slot in a temporary view. */
        const uint8_t *new0=(active_slot==0u)?slot0:readback;
        const uint8_t *new1=(active_slot==1u)?slot1:readback;
        size_t n0=(active_slot==0u)?len0:readback_len;
        size_t n1=(active_slot==1u)?len1:readback_len;
        vg_b43_nonce_ledger selected;uint64_t g=0u;uint8_t index=0u;
        if(!vg_b45_select_two_slot(new0,n0,new1,n1,trusted_floor,source_id,
              key,key_len,&selected,&g,&index))break;
        bool good=(g==proposed_gen&&index==(uint8_t)(1u-active_slot)&&
                   memcmp(&selected,&planned,sizeof(selected))==0);
        vg_b40_zero(&selected,sizeof(selected));
        if(!good)break;
        memcpy(out,&verified,sizeof(verified));
        *out_generation=verified_gen;
        *out_slot=index;
        accepted=true;
    }while(false);
    vg_b40_zero(&current,sizeof(current));
    vg_b40_zero(&planned,sizeof(planned));
    vg_b40_zero(&verified,sizeof(verified));
    return accepted;
}
#endif
