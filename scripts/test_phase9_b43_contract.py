#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b43_nonce_ledger_host.h').read_text()
p=(r/'scripts/test_phase9_b43_nonce_ledger.py').read_text()
fixture=(r/'scripts/phase9_b43_nonce_ledger_fixture.c').read_text()
for term in ('VG_B43_NONCE_CAPACITY 8u','vg_b43_ledger_valid(',
             'vg_b31_overlaps(ledger_region,other_region)',
             'vg_b42_verify_challenge(', 'if(reused)return false;',
             'ledger->count>=VG_B43_NONCE_CAPACITY',
             'memcpy(ledger->used[ledger->count],issued_nonce,VG_B42_NONCE_LEN)',
             '*verified_epoch=candidate_epoch;', 'NOT persistent, atomic, thread safe'):
    assert term in h,term
assert h.index('if(reused)return false;')<h.index('vg_b42_verify_challenge(')<h.index('memcpy(ledger->used[ledger->count]')
for term in ('secrets.token_bytes(32)','secrets.token_bytes(16)',
             'hmac.new(master,CHALLENGE+data,hashlib.sha256).digest()',
             'B43_DURABLE_NONCE_REPLAY_CAS_THREAD_SAFETY_ESP32=NOT_VERIFIED'):
    assert term in p,term
for term in ('ledger-corrupt','exhaust','alias-input', 'vg_b43_ledger_init(',
             'memcmp(&snapshot,&ledger,sizeof(ledger))'):
    assert term in fixture,term
for blocked in ('malloc(', 'system(', 'pthread_', 'DB_CONNECTION=', 'malloc '):
    assert blocked not in h,blocked
print('B43_CONTRACT=PASS_BOUNDED_LEDGER_INPUT_ISOLATION_AND_NO_EVICTION')
