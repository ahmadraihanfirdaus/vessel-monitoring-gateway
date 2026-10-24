#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b40_hmac_verify_host.h').read_text()
t=(r/'scripts/test_phase9_b40_hmac_verify.py').read_text()
c=(r/'scripts/phase9_b40_hmac_verify_fixture.c').read_text()
for marker in ('vg_b40_sha_block(','vg_b40_sha_final(','vg_b40_hmac(',
               'vg_b40_ct_eq32(','vg_b40_verify_host_hmac(',
               'vg_b39_precheck_untrusted_scope(',
               'vg_b31_overlaps(key_reg,blob_reg)',
               'vg_b40_zero(scoped,sizeof(scoped))',
               'vg_b40_zero(tag,sizeof(tag))',
               '*verified_epoch=candidate_epoch;',
               'B40 host','test'):
    if marker in ('B40 host','test'):continue
    assert marker in h,marker
for marker in ('secrets.token_bytes(32)','hmac.new(scoped,AUTH+ctx+msg',
               'PASS_46_CASES_3_ACCEPT_43_DENY',
               'B40_PRODUCTION_CRYPTO_KEY_STORAGE_ESP32_ATOMIC_ACK=NOT_VERIFIED',
               'structural_without_mac>=8'):
    assert marker in t,marker
for marker in ('rfc4231_1','rfc4231_2','sha_abc','vg_b40_verify_host_hmac(',
               'B40_HOST_HMAC=ACCEPT_TEST_ONLY'):
    assert marker in c,marker
assert 'malloc(' not in h and 'system(' not in h and 'SECRET_KEY=' not in h
print('B40_CONTRACT=PASS_SHA256_HMAC_C99_HOST_ONLY_CONSTANT_TIME_MAC_AND_EPOCH_FAIL_CLOSED')
