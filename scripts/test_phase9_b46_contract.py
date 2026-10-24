#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b46_stage_readback_host.h').read_text()
f=(r/'scripts/phase9_b46_stage_readback_fixture.c').read_text()
t=(r/'scripts/test_phase9_b46_stage_readback.py').read_text()
for item in ('vg_b45_select_two_slot','vg_b44_restore_nonce_ledger','current_gen==UINT64_MAX',
             'planned.count!=current.count+1u','memcmp(staged,readback,VG_B44_SNAPSHOT_LENGTH)',
             'vg_b31_overlaps','vg_b40_zero','*out_slot=index','1u-active_slot'):
    assert item in h,item
assert 'B46_DENY_OUTPUT_UNCHANGED_HOST_ONLY' in f
assert 'B46_ALIAS_FAIL_CLOSED_NO_OUTPUT_ON_DENY=PASS' in f
assert 'hmac.compare_digest' in t and "'-std=c99'" in t
print('B46_CONTRACT=PASS_HOST_ONLY_INACTIVE_SLOT_ADMISSION_NO_DB')
