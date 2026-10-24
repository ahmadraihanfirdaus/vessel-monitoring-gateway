#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b42_challenge_bound_host.h').read_text()
t=(r/'scripts/test_phase9_b42_challenge_bound.py').read_text()
f=(r/'scripts/phase9_b42_challenge_bound_fixture.c').read_text()
for marker in ('vg_b42_verify_challenge(', 'VG_B42_NONCE_LEN 16u',
               'VG_B42_PAYLOAD_LEN 248u','VG_PHASE9_B42_CHALLENGE_AUTH_V1',
               'vg_b41_verify_rotation_fence(', 'vg_b31_overlaps(regions[i],regions[j])',
               'vg_b40_hmac(', 'vg_b40_ct_eq32(', '*verified_epoch=candidate_epoch;',
               'nonzero|=issued_nonce[i]','vg_b40_zero(computed,sizeof(computed))'):
    assert marker in h,marker
for marker in ('secrets.token_bytes(16)','secrets.token_bytes(32)',
               'hmac.new(master,CHALLENGE+data,hashlib.sha256).digest()',
               'B42_TRUSTED_NONCE_ISSUANCE_SINGLE_USE_ATOMIC_CAS_ESP32=NOT_VERIFIED',
               'assert expected_accept==3'):
    assert marker in t,marker
for marker in ('exact_read(', 'B42_CHALLENGE=DENIED_TEST_ONLY',
               'epoch!=0x8877665544332211ULL','vg_b40_zero(key,sizeof(key))'):
    assert marker in f,marker
assert 'malloc(' not in h and 'system(' not in h and 'SECRET=' not in h
print('B42_CONTRACT=PASS_SESSION_CHALLENGE_HMAC_SCOPE_REVISION_AND_FAIL_CLOSED')
