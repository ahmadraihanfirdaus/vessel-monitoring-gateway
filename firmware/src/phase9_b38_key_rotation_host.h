#ifndef PHASE9_B38_KEY_ROTATION_HOST_H
#define PHASE9_B38_KEY_ROTATION_HOST_H
/* HOST POLICY PREFILTER ONLY. No HMAC, persistent keyring, or authenticated cutover.
 * C99 PASS_NO_AUTH never permits an ACK to be committed or published. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "phase9_b37_hmac_receipt_host.h"
typedef struct vg_b38_policy {
    uint64_t active_key_id;
    uint64_t retired_key_id;
    uint64_t activation_epoch;
    uint64_t exclusive_epoch_floor;
} vg_b38_policy;
static inline bool vg_b38_precheck_rotation(const uint8_t *sealed,size_t sealed_len,
    const uint8_t *wire,size_t wire_len,const vg_b38_policy *policy,
    uint64_t *observed_epoch) {
    vg_b31_region a,b,c,d;
    if(!sealed || !wire || !policy || !observed_epoch ||
       !vg_b31_region_of(sealed,sealed_len,&a) ||
       !vg_b31_region_of(wire,wire_len,&b) ||
       !vg_b31_region_of(policy,sizeof(*policy),&c) ||
       !vg_b31_region_of(observed_epoch,sizeof(*observed_epoch),&d) ||
       vg_b31_overlaps(a,b)||vg_b31_overlaps(a,c)||vg_b31_overlaps(a,d)||
       vg_b31_overlaps(b,c)||vg_b31_overlaps(b,d)||vg_b31_overlaps(c,d))return false;
    if(policy->active_key_id==0u || policy->retired_key_id==policy->active_key_id ||
       policy->activation_epoch==0u ||
       policy->exclusive_epoch_floor==UINT64_MAX)return false;
    uint64_t key_id=0u,epoch=0u;
    if(!vg_b37_peek_untrusted(sealed,sealed_len,wire,wire_len,&key_id,&epoch))return false;
    if(key_id!=policy->active_key_id || key_id==policy->retired_key_id ||
       epoch<policy->activation_epoch || epoch<=policy->exclusive_epoch_floor)return false;
    *observed_epoch=epoch;
    return true;
}
#endif
