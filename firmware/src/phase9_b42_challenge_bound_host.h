#ifndef PHASE9_B42_CHALLENGE_BOUND_HOST_H
#define PHASE9_B42_CHALLENGE_BOUND_HOST_H
/* HOST-ONLY test helper. The caller supplies both challenge values and two
 * authority observations: freshness, non-reuse and atomicity are EXTERNAL.
 * Never use this alone to authorize ACK or a durable checkpoint. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b41_rotation_fence_host.h"
#define VG_B42_NONCE_LEN 16u
#define VG_B42_PROOF_LEN 32u
#define VG_B42_PAYLOAD_LEN 248u
static inline bool vg_b42_verify_challenge(
    const uint8_t *sealed,size_t sealed_len,const uint8_t *wire,size_t wire_len,
    const vg_b41_observation *before,const vg_b41_observation *after,
    uint64_t minimum_revision,uint64_t expected_source_id,
    uint32_t purpose,uint32_t device_tag,const uint8_t *master,size_t master_len,
    const uint8_t *issued_nonce,size_t issued_len,
    const uint8_t *received_nonce,size_t received_len,
    const uint8_t *received_proof,size_t proof_len,
    uint64_t *verified_epoch) {
    static const uint8_t domain[]="VG_PHASE9_B42_CHALLENGE_AUTH_V1";
    vg_b31_region regions[9];
    const void *pointers[9]={sealed,wire,before,after,master,issued_nonce,
                              received_nonce,received_proof,verified_epoch};
    const size_t lens[9]={sealed_len,wire_len,sizeof(*before),sizeof(*after),
                          master_len,issued_len,received_len,proof_len,
                          sizeof(*verified_epoch)};
    if(!sealed||!wire||!before||!after||!master||!issued_nonce||
       !received_nonce||!received_proof||!verified_epoch||
       sealed_len!=128u||wire_len!=72u||master_len!=32u||
       issued_len!=VG_B42_NONCE_LEN||received_len!=VG_B42_NONCE_LEN||
       proof_len!=VG_B42_PROOF_LEN)return false;
    for(size_t i=0u;i<9u;++i)
        if(!vg_b31_region_of(pointers[i],lens[i],&regions[i]))return false;
    for(size_t i=0u;i<9u;++i)
        for(size_t j=i+1u;j<9u;++j)
            if(vg_b31_overlaps(regions[i],regions[j]))return false;
    /* Constant-time comparison; reject the all-zero test nonce. */
    uint8_t difference=0u,nonzero=0u;
    for(size_t i=0u;i<VG_B42_NONCE_LEN;++i){
        difference|=(uint8_t)(issued_nonce[i]^received_nonce[i]);
        nonzero|=issued_nonce[i];
    }
    if(difference||!nonzero)return false;
    uint64_t candidate_epoch=0u;
    if(!vg_b41_verify_rotation_fence(sealed,sealed_len,wire,wire_len,before,after,
            minimum_revision,expected_source_id,purpose,device_tag,
            master,master_len,&candidate_epoch))return false;
    uint8_t payload[VG_B42_PAYLOAD_LEN],computed[32];
    size_t offset=0u;
    memcpy(payload+offset,issued_nonce,16u);offset+=16u;
    memcpy(payload+offset,sealed,128u);offset+=128u;
    memcpy(payload+offset,wire,72u);offset+=72u;
    vg_b40_put_le64(payload+offset,before->authority_revision);offset+=8u;
    vg_b40_put_le64(payload+offset,expected_source_id);offset+=8u;
    vg_b40_put_le32(payload+offset,purpose);offset+=4u;
    vg_b40_put_le32(payload+offset,device_tag);offset+=4u;
    vg_b40_put_le64(payload+offset,candidate_epoch);offset+=8u;
    if(offset!=VG_B42_PAYLOAD_LEN){vg_b40_zero(payload,sizeof(payload));return false;}
    bool success=vg_b40_hmac(master,master_len,domain,sizeof(domain),
                             payload,sizeof(payload),computed) &&
                 vg_b40_ct_eq32(computed,received_proof);
    vg_b40_zero(payload,sizeof(payload));vg_b40_zero(computed,sizeof(computed));
    if(!success)return false;
    *verified_epoch=candidate_epoch;
    return true;
}
#endif
