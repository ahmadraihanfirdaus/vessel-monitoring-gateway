#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b44_nonce_snapshot_host.h').read_text()
s=(r/'scripts/test_phase9_b44_nonce_snapshot.py').read_text()
f=(r/'scripts/phase9_b44_nonce_snapshot_fixture.c').read_text()
for token in ('VG_B44_SNAPSHOT_LENGTH 192u','VG_B44_BODY_LENGTH 160u',
              'VG_B44_VERSION 1u','vg_b44_seal_nonce_ledger(',
              'vg_b44_restore_nonce_ledger(', 'vg_b44_disjoint4(',
              'vg_b40_ct_eq32(', 'vg_b43_ledger_valid(',
              'vg_b40_zero(', 'trusted_min_generation==0u',
              'NOT crash-atomic storage','VG_PHASE9_B44_LEDGER_SNAPSHOT_HMAC_V1'):
    assert token in h,token
assert h.index('vg_b40_ct_eq32(')<h.index('vg_b43_nonce_ledger candidate;')<h.index('memcpy(output,&candidate')
for token in ('oracle(',"HEADER=struct.Struct('<4sIQQII')",'hmac.new(key,DOMAIN+body',
              'source_authenticated_wrong','duplicate_nonce_authenticated',
              'stale_authenticated','B44_TRUSTED_GENERATION_FLOOR'):
    assert token in s,token
for token in ('B44_ALIAS_BOUNDS_FAILURE_IMMUTABLE=PASS',
              'memcmp(&ledger,&sentinel,sizeof(ledger))',
              'B44_RESTORE_DENIED_UNCHANGED_TEST_ONLY'):
    assert token in f,token
for blocked in ('fopen(', 'pthread_', 'DB_CONNECTION=', 'malloc('):
    assert blocked not in h,blocked
print('B44_CONTRACT=PASS_CANONICAL_192_HMAC_FLOOR_AND_NO_DB')
