#ifndef PHASE9_B41_ROTATION_FENCE_HOST_H
#define PHASE9_B41_ROTATION_FENCE_HOST_H
/* HOST TEST ONLY: external rotation-observation fence over B40's HMAC verifier.
 * The two observations are caller-provided. They do not prove that any trusted
 * store or atomic CAS exists. Do not use this API for production authorization. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "phase9_b40_hmac_verify_host.h"

typedef struct vg_b41_observation {
    vg_b39_scope_policy scope;
    uint64_t authority_revision;
    uint64_t source_id;
} vg_b41_observation;

static inline bool vg_b41_same_scope(const vg_b39_scope_policy *a,
                                      const vg_b39_scope_policy *b) {
    return a->rotation.active_key_id==b->rotation.active_key_id &&
           a->rotation.retired_key_id==b->rotation.retired_key_id &&
           a->rotation.activation_epoch==b->rotation.activation_epoch &&
           a->rotation.exclusive_epoch_floor==b->rotation.exclusive_epoch_floor &&
           a->purpose_id==b->purpose_id && a->device_tag==b->device_tag;
}

/* Non-overlap checks are performed before any reads or output writes.
 * On any rejection, *verified_epoch is unchanged. */
static inline bool vg_b41_verify_rotation_fence(
    const uint8_t *sealed,size_t sealed_len,const uint8_t *wire,size_t wire_len,
    const vg_b41_observation *before,const vg_b41_observation *after,
    uint64_t minimum_revision,uint64_t expected_source_id,
    uint32_t purpose,uint32_t device_tag,const uint8_t *master,size_t master_len,
    uint64_t *verified_epoch) {
    vg_b31_region blob,wire_reg,pre,post,key,out;
    if(!sealed||!wire||!before||!after||!master||!verified_epoch||
       sealed_len!=128u||wire_len!=72u||master_len!=32u||
       !vg_b31_region_of(sealed,sealed_len,&blob)||
       !vg_b31_region_of(wire,wire_len,&wire_reg)||
       !vg_b31_region_of(before,sizeof(*before),&pre)||
       !vg_b31_region_of(after,sizeof(*after),&post)||
       !vg_b31_region_of(master,master_len,&key)||
       !vg_b31_region_of(verified_epoch,sizeof(*verified_epoch),&out))return false;
    const vg_b31_region regions[]={blob,wire_reg,pre,post,key,out};
    for(size_t i=0;i<6u;i++)for(size_t j=i+1u;j<6u;j++)
        if(vg_b31_overlaps(regions[i],regions[j]))return false;
    if(minimum_revision==UINT64_MAX || !before->authority_revision ||
       before->authority_revision<=minimum_revision ||
       !expected_source_id || before->source_id!=expected_source_id ||
       !before->scope.rotation.active_key_id ||
       before->scope.rotation.retired_key_id==before->scope.rotation.active_key_id ||
       before->scope.purpose_id!=purpose || before->scope.device_tag!=device_tag)return false;
    uint64_t epoch=0u;
    if(!vg_b40_verify_host_hmac(sealed,sealed_len,wire,wire_len,&before->scope,
            purpose,device_tag,master,master_len,&epoch))return false;
    /* After HMAC, compare the caller-provided second authority observation.
     * A trusted store/callback with atomic CAS is NOT present here. */
    if(before->authority_revision!=after->authority_revision ||
       after->source_id!=expected_source_id ||
       !vg_b41_same_scope(&before->scope,&after->scope))return false;
    *verified_epoch=epoch;
    return true;
}
#endif
