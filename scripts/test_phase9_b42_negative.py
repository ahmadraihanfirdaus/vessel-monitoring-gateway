#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b42_challenge_bound.py').read_text()
for marker in ('different_issued_nonce','different_echo_nonce','all_zero_nonce',
    'nonce_flip_', 'proof_flip_', 'sealed_flip_', 'proof_wrong_context_',
    'wrong_after_policy','old_key_after_cutover','revision_change_after_auth',
    'source_mismatch','purpose_mismatch','device_mismatch','output_alias_before',
    'assert (result==\'B42_CHALLENGE=ACCEPT_TEST_ONLY\')==expected'):
    assert marker in s,marker
h=(r/'firmware/src/phase9_b42_challenge_bound_host.h').read_text()
assert h.index('vg_b41_verify_rotation_fence(') < h.index('vg_b40_hmac(')
assert h.index('vg_b40_ct_eq32(')<h.index('*verified_epoch=candidate_epoch;')
print('B42_NEGATIVE=PASS_CHALLENGE_REPLAY_TAG_CONTEXT_ROTATION_AND_UNCHANGED_OUTPUT')
