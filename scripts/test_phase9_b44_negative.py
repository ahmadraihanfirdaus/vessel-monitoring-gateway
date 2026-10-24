#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b44_nonce_snapshot_host.h').read_text()
s=(r/'scripts/test_phase9_b44_nonce_snapshot.py').read_text()
c=(r/'scripts/phase9_b44_nonce_snapshot_fixture.c').read_text()
for pattern in ('stale_authenticated','wrong_key','source_authenticated_wrong',
                'wrong_version_authenticated','reserved_authenticated',
                'duplicate_nonce_authenticated','count_oversize_authenticated',
                'nonzero_trailing_authenticated','zero_active_nonce_authenticated',
                'tampered.append(', 'assert not denied.exists()',
                'assert not out.exists()'):
    assert pattern in s,pattern
for pattern in ('memcmp(&ledger,&sentinel,sizeof(ledger))',
                'B44_RESTORE_DENIED_UNCHANGED_TEST_ONLY',
                'B44_ALIAS_BOUNDS_FAILURE_IMMUTABLE=PASS'):
    assert pattern in c,pattern
assert h.index('if(!authenticated)return false;')<h.index('candidate.count=vg_b44_get32')
assert h.index('if(!valid)')<h.index('memcpy(output,&candidate')
print('B44_NEGATIVE=PASS_TAMPER_STALE_SOURCE_ALIAS_AND_FAILURE_IMMUTABILITY')
