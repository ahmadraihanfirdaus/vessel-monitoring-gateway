#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b38_key_rotation_host.h').read_text()
s=(r/'scripts/test_phase9_b38_key_rotation.py').read_text()
for x in ('vg_b38_precheck_rotation(', 'vg_b37_peek_untrusted(', 'vg_b31_overlaps(',
          'exclusive_epoch_floor', 'activation_epoch', '*observed_epoch=epoch;'):
 assert x in h,x
for x in ('secrets.token_bytes(32)', 'hmac.new(key,DOMAIN+blob[:96],hashlib.sha256)',
          'hmac.compare_digest(', 'old_receipt_post_cutover', 'forged_crc_valid_not_authenticated',
          'B38_EXTERNAL_TRUSTED_KEYRING_COUNTER_ESP32=NOT_VERIFIED', 'assert len(cases)==47'):
 assert x in s,x
assert 'HMAC_SECRET=' not in h and 'malloc(' not in h
print('B38_CONTRACT=PASS_STRUCTURAL_C99_NO_AUTH_PYTHON_EPHEMERAL_ROTATION_POLICY')
