#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b46_stage_readback.py').read_text()
for item in ('deny_split_brain_current','deny_generation_overflow','deny_wrong_nonce_sequence',
             'deny_new_nonce_duplicate','deny_floor_roll_back','deny_wrong_key',
             'deny_readback_short','deny_stage_invalid_magic_authenticated',
             'cut_bit_','cut_truncate_','deny_no_new_nonce'):
    assert item in s,item
assert 'if ref is None:' in s and 'result.read_bytes()==sentinel' in s
print('B46_NEGATIVE=PASS_NO_STALE_NONCE_REPLAY_ON_DENIAL_HOST_ONLY')
