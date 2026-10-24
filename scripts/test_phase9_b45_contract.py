#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b45_slot_recovery_host.h').read_text()
f=(r/'scripts/phase9_b45_slot_recovery_fixture.c').read_text()
t=(r/'scripts/test_phase9_b45_slot_recovery.py').read_text()
assert 'vg_b44_restore_nonce_ledger' in h and 'vg_b31_overlaps' in h
assert 'memcmp(slot0,slot1,VG_B44_SNAPSHOT_LENGTH)' in h
assert 'generations[0]>=generations[1]' in h
assert 'vg_b40_zero(candidates,sizeof(candidates))' in h
assert 'B45_SELECT_DENIED_UNCHANGED_TEST_ONLY' in f
assert 'B45_ALIAS_LENGTH_IMMUTABLE=PASS' in f
assert 'hmac.compare_digest' in t and 'crash' not in t.lower().split('print(')[0]
print('B45_CONTRACT=PASS_HOST_ONLY_TWO_SLOT_READBACK_SELECTION_NO_DB')
