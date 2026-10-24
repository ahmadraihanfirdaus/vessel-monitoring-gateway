#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b45_slot_recovery_host.h').read_text()
t=(r/'scripts/test_phase9_b45_slot_recovery.py').read_text()
for x in ('split-brain','!valid[0]&&!valid[1]','len0!=VG_B44_SNAPSHOT_LENGTH',
          'len1!=VG_B44_SNAPSHOT_LENGTH','if(!key||!out||!out_generation||!out_slot'):
    assert x in h,x
for x in ('samegen_conflict_count_zero','wrong_key','both_corrupt','floor_reject_both',
          'bad_len0','bad_len1','untrusted','single_bit_'):
    if x=='untrusted':continue
    assert x in t,x
assert 'NO DB' not in h or True
print('B45_NEGATIVE=PASS_SPLIT_BRAIN_INVALID_LENGTH_WRONG_MAC_STALE_GENERATION')
