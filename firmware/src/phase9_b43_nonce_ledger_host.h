#ifndef PHASE9_B43_NONCE_LEDGER_HOST_H
#define PHASE9_B43_NONCE_LEDGER_HOST_H
/* HOST-ONLY bounded in-memory nonce ledger. Strictly no eviction on exhaustion.
 * NOT persistent, atomic, thread safe, authoritative, or an ESP32 implementation.
 * A trusted session issuer, durable atomic nonce store and external serialization
 * are required to prevent replay after restart or across processes. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b42_challenge_bound_host.h"
#define VG_B43_NONCE_CAPACITY 8u
#define VG_B43_MAGIC UINT32_C(0x43343339)
typedef struct {
    uint32_t magic;
    uint32_t count;
    uint8_t used[VG_B43_NONCE_CAPACITY][VG_B42_NONCE_LEN];
} vg_b43_nonce_ledger;
static inline void vg_b43_ledger_init(vg_b43_nonce_ledger *ledger){
    if(!ledger)return;
    memset(ledger,0,sizeof(*ledger));
    ledger->magic=VG_B43_MAGIC;
}
static inline bool vg_b43_ledger_valid(const vg_b43_nonce_ledger *ledger){
    if(!ledger||ledger->magic!=VG_B43_MAGIC||ledger->count>VG_B43_NONCE_CAPACITY)
        return false;
    for(size_t i=0u;i<VG_B43_NONCE_CAPACITY;++i){
        uint8_t nonzero=0u;
        for(size_t k=0u;k<VG_B42_NONCE_LEN;++k)nonzero|=ledger->used[i][k];
        if((i<(size_t)ledger->count&&!nonzero)||
           (i>=(size_t)ledger->count&&nonzero))return false;
        if(i<(size_t)ledger->count){
            for(size_t j=0u;j<i;++j){
                uint8_t difference=0u;
                for(size_t k=0u;k<VG_B42_NONCE_LEN;++k)
                    difference|=(uint8_t)(ledger->used[i][k]^ledger->used[j][k]);
                if(!difference)return false;
            }
        }
    }
    return true;
}
static inline bool vg_b43_verify_once(
    const uint8_t *sealed,size_t sealed_len,const uint8_t *wire,size_t wire_len,
    const vg_b41_observation *before,const vg_b41_observation *after,
    uint64_t minimum_revision,uint64_t expected_source_id,
    uint32_t purpose,uint32_t device_tag,const uint8_t *master,size_t master_len,
    const uint8_t *issued_nonce,size_t issued_len,
    const uint8_t *received_nonce,size_t received_len,
    const uint8_t *received_proof,size_t proof_len,
    vg_b43_nonce_ledger *ledger,uint64_t *verified_epoch){
    vg_b31_region ledger_region,other_region;
    const void *ptrs[9]={sealed,wire,before,after,master,issued_nonce,
                         received_nonce,received_proof,verified_epoch};
    const size_t lens[9]={sealed_len,wire_len,sizeof(*before),sizeof(*after),
                          master_len,issued_len,received_len,proof_len,
                          sizeof(*verified_epoch)};
    if(!ledger||!verified_epoch||!vg_b43_ledger_valid(ledger)||
       ledger->count>=VG_B43_NONCE_CAPACITY||
       !vg_b31_region_of(ledger,sizeof(*ledger),&ledger_region))return false;
    for(size_t i=0u;i<9u;++i){
        if(!ptrs[i]||!vg_b31_region_of(ptrs[i],lens[i],&other_region)||
           vg_b31_overlaps(ledger_region,other_region))return false;
    }
    /* Reject same nonce in any prior scope: fail closed and never evict entries. */
    uint8_t reused=0u;
    for(size_t i=0u;i<(size_t)ledger->count;++i){
        uint8_t diff=0u;
        for(size_t j=0u;j<VG_B42_NONCE_LEN;++j)
            diff|=(uint8_t)(ledger->used[i][j]^issued_nonce[j]);
        reused|=(uint8_t)(diff==0u);
    }
    if(reused)return false;
    uint64_t candidate_epoch=0u;
    if(!vg_b42_verify_challenge(sealed,sealed_len,wire,wire_len,before,after,
         minimum_revision,expected_source_id,purpose,device_tag,master,master_len,
         issued_nonce,issued_len,received_nonce,received_len,
         received_proof,proof_len,&candidate_epoch))return false;
    /* Single-process host fixture only: NOT an atomic multi-thread/CAS commit. */
    memcpy(ledger->used[ledger->count],issued_nonce,VG_B42_NONCE_LEN);
    ++ledger->count;
    *verified_epoch=candidate_epoch;
    return true;
}
#endif
