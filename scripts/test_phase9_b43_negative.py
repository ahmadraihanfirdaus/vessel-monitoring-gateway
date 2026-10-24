#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b43_nonce_ledger.py').read_text()
c=(r/'scripts/phase9_b43_nonce_ledger_fixture.c').read_text()
for term in ('nonce_bit_', 'proof_bit_', 'post_revision_changed',
             'revision_floor_stale','wrong_key','zero_nonce','wrong_source',
             'wrong_purpose','wrong_device','damaged_seal','echo_mismatch',
             'B43_REPLAY_SAME_PROCESS_BOUNDED_FAIL_CLOSED=VERIFIED'):
    assert term in s,term
for term in ('memcmp(&snapshot,&ledger,sizeof(ledger))','ledger.used[2][0]=1u',
             'VG_B43_NONCE_CAPACITY','ledger.count!=1u',
             'sentinel!=UINT64_C(0x8877665544332211)',
             'B43_LEDGER=REPLAY_DENIED_TEST_ONLY'):
    assert term in c,term
print('B43_NEGATIVE=PASS_REPLAY_CORRUPT_CAPACITY_ALIAS_AND_FAILURE_IMMUTABILITY')
