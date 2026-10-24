#ifndef PHASE9_B37_HMAC_RECEIPT_HOST_H
#define PHASE9_B37_HMAC_RECEIPT_HOST_H
/* B37 HOST-ONLY UNAUTHENTICATED STRUCTURAL PRECHECK.
 * It intentionally does NOT verify HMAC. Only the independent Python
 * authentication stage may authorize a receipt. Do not interpret a
 * successful precheck as accepted ACK, external CAS, or ESP32 trust. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "phase9_b36_wire_interop_host.h"
#define VG_B37_SEALED_LENGTH 128u
#define VG_B37_PRELUDE_LENGTH 24u
#define VG_B37_INNER_LENGTH 72u
#define VG_B37_MAC_LENGTH 32u
static inline bool vg_b37_peek_untrusted(const uint8_t *raw,size_t len,
    const uint8_t *expected_wire,size_t wire_len,
    uint64_t *key_id,uint64_t *epoch) {
    if(!raw || !expected_wire || !key_id || !epoch ||
       len!=VG_B37_SEALED_LENGTH || wire_len!=VG_B37_INNER_LENGTH)return false;
    vg_b31_region ra,rb,rc,rd;
    if(!vg_b31_region_of(raw,len,&ra) ||
       !vg_b31_region_of(expected_wire,wire_len,&rb) ||
       !vg_b31_region_of(key_id,sizeof(*key_id),&rc) ||
       !vg_b31_region_of(epoch,sizeof(*epoch),&rd) ||
       vg_b31_overlaps(ra,rb) || vg_b31_overlaps(ra,rc) ||
       vg_b31_overlaps(ra,rd) || vg_b31_overlaps(rb,rc) ||
       vg_b31_overlaps(rb,rd) || vg_b31_overlaps(rc,rd))return false;
    if(raw[0]!='V' || raw[1]!='G' || raw[2]!='3' || raw[3]!='7' ||
       vg_b36_get32(raw+4u)!=1u)return false;
    uint64_t k=vg_b36_get64(raw+8u),e=vg_b36_get64(raw+16u);
    if(!k || !e || memcmp(raw+VG_B37_PRELUDE_LENGTH,expected_wire,wire_len))return false;
    vg_b35_receipt receipt;
    if(!vg_b36_reference_decode(raw+VG_B37_PRELUDE_LENGTH,wire_len,&receipt))return false;
    *key_id=k;*epoch=e;
    return true;
}
#endif
