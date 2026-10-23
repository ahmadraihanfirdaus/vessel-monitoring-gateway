#ifndef PHASE9_B21_CUT_MATRIX_HOST_H
#define PHASE9_B21_CUT_MATRIX_HOST_H
/* HOST-ONLY deterministic torn-write model. Not a disk/flash crash-safety
 * promise. Never write the most recently valid slot during an update. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b20_slot_prepare_host.h"

/* Simulate a prefix of a candidate replacing the older slot. Optionally
 * retain the old slot's unwritten suffix as a model for in-place writes.
 * The target slot is the only one modified. No I/O or effects outside caller. */
static inline bool vg_b21_inject_prefix(const vg_b20_slot *older,
    const uint8_t *candidate,size_t candidate_len,size_t written,
    bool retain_tail,vg_b20_slot *out)
{
    if(!older || !candidate || !out || !candidate_len ||
       candidate_len>VG_B19_SLOT_MAX || older->len>VG_B19_SLOT_MAX ||
       written>candidate_len)return false;
    vg_b20_slot temp=*older;
    if(!retain_tail){
        memset(temp.bytes,0,sizeof(temp.bytes));
        temp.len=written;
    } else if(written>temp.len)temp.len=written;
    if(written)memcpy(temp.bytes,candidate,written);
    *out=temp;
    return true;
}
/* Require an old conservative winner; ACK pending may not be restored.
 * This is a host invariant, not a guarantee for arbitrary storage devices. */
static inline bool vg_b21_fallback_is_conservative(const vg_b20_slot *altered,
    const vg_b20_slot *latest,uint32_t tag,uint32_t expected_gen,
    uint32_t expected_ack)
{
    if(!altered || !latest)return false;
    vg_b19_restored result;bool degraded=false;
    if(!vg_b19_select(altered->bytes,altered->len,
        latest->bytes,latest->len,tag,&result,&degraded))return false;
    return result.generation==expected_gen &&
        result.ack.last_accepted_sequence==expected_ack &&
        !result.ack.pending && !result.ack.pending_sequence &&
        !result.ack.pending_correlation;
}
#endif
