#ifndef PHASE9_B39_DOMAIN_SCOPE_HOST_H
#define PHASE9_B39_DOMAIN_SCOPE_HOST_H
/* HOST structural-only scope guard. No HMAC, master secret, or authorization.
 * This precheck must NEVER permit an ACK, checkpoint or key promotion by itself.
 * Trusted purpose/device bindings and signing keys are external dependencies. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "phase9_b38_key_rotation_host.h"

typedef struct vg_b39_scope_policy {
    vg_b38_policy rotation;
    uint32_t purpose_id;
    uint32_t device_tag;
} vg_b39_scope_policy;

#define VG_B39_PURPOSE_RESTORE 1u
#define VG_B39_PURPOSE_PUBLISH 2u

static inline bool vg_b39_precheck_untrusted_scope(
    const uint8_t *sealed,size_t sealed_len,
    const uint8_t *expected_wire,size_t wire_len,
    const vg_b39_scope_policy *policy,uint32_t caller_purpose,
    uint32_t caller_device_tag,uint64_t *observed_epoch) {
    vg_b31_region a,b,c,d;
    if (!sealed || !expected_wire || !policy || !observed_epoch ||
        !vg_b31_region_of(sealed,sealed_len,&a) ||
        !vg_b31_region_of(expected_wire,wire_len,&b) ||
        !vg_b31_region_of(policy,sizeof(*policy),&c) ||
        !vg_b31_region_of(observed_epoch,sizeof(*observed_epoch),&d) ||
        vg_b31_overlaps(a,b) || vg_b31_overlaps(a,c) || vg_b31_overlaps(a,d) ||
        vg_b31_overlaps(b,c) || vg_b31_overlaps(b,d) || vg_b31_overlaps(c,d))return false;
    if ((caller_purpose!=VG_B39_PURPOSE_RESTORE && caller_purpose!=VG_B39_PURPOSE_PUBLISH) ||
        caller_purpose!=policy->purpose_id || !caller_device_tag ||
        caller_device_tag!=policy->device_tag ||
        wire_len!=VG_B37_INNER_LENGTH ||
        vg_b36_get32(expected_wire+12u)!=caller_device_tag)return false;
    uint64_t local_epoch=0u;
    if(!vg_b38_precheck_rotation(sealed,sealed_len,expected_wire,wire_len,
            &policy->rotation,&local_epoch))return false;
    *observed_epoch=local_epoch;
    return true;
}
#endif
