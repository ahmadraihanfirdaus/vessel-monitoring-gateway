#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b37_hmac_receipt_host.h').read_text()
s=(r/'scripts/test_phase9_b37_hmac_receipt.py').read_text()
for t in ('VG_B37_SEALED_LENGTH 128u','vg_b37_peek_untrusted(',
          'vg_b36_reference_decode(', 'vg_b31_overlaps(', '*key_id=k;*epoch=e;'):
    assert t in h,t
for t in ('hmac.compare_digest(', 'secrets.token_bytes(32)',
          'hmac.new(key,LABEL+msg,hashlib.sha256)',
          'epoch<=min_exclusive_epoch',"assert len(cases)==36"):
    assert t in s,t
assert not any(t in h for t in ('HMAC_KEY=', 'private_key', 'malloc(', 'system('))
print('B37_CONTRACT=PASS_STRUCTURAL_C99_ONLY_PYTHON_HMAC_AUTHORIZATION')
