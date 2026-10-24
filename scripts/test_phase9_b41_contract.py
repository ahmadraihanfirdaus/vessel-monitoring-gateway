#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b41_rotation_fence_host.h').read_text()
t=(r/'scripts/test_phase9_b41_rotation_fence.py').read_text()
f=(r/'scripts/phase9_b41_rotation_fence_fixture.c').read_text()
for marker in ('vg_b41_verify_rotation_fence(', 'vg_b41_same_scope(',
               'before->authority_revision!=after->authority_revision',
               'before->source_id!=expected_source_id',
               'vg_b31_overlaps(regions[i],regions[j])',
               'vg_b40_verify_host_hmac(', '*verified_epoch=epoch;',
               'minimum_revision==UINT64_MAX'):
    assert marker in h,marker
for marker in ('secrets.token_bytes(32)','hmac.new(derived,AUTH+ctx+msg',
               'B41_ROTATION_FENCE=PASS_52_CASES_3_ACCEPT_49_DENY_NO_DB',
               'B41_EXTERNAL_TRUSTED_REVISION_ATOMIC_CAS_ESP32=NOT_VERIFIED'):
    assert marker in t,marker
for marker in ('exact_read(', 'before.authority_revision=pre_rev',
               'after.authority_revision=post_rev','B41_ROTATION_FENCE=DENIED_TEST_ONLY'):
    assert marker in f,marker
assert 'malloc(' not in h and 'system(' not in h and 'SECRET=' not in h
print('B41_CONTRACT=PASS_ROTATION_OBSERVATION_REVISION_SOURCE_AND_DENY_UNCHANGED')
