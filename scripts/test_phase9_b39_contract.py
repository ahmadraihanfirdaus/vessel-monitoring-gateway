#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b39_domain_scope_host.h').read_text()
s=(r/'scripts/test_phase9_b39_domain_scope.py').read_text()
for x in ('vg_b39_precheck_untrusted_scope(', 'vg_b38_precheck_rotation(', 'vg_b31_overlaps(',
          'VG_B39_PURPOSE_RESTORE 1u','VG_B39_PURPOSE_PUBLISH 2u',
          'vg_b36_get32(expected_wire+12u)','*observed_epoch=local_epoch;'):
 assert x in h,x
for x in ('secrets.token_bytes(32)','KDF_DOMAIN+ctx','AUTH_DOMAIN+ctx+msg',
          'hmac.compare_digest(', 'purpose_cross_replay_restore_to_publish',
          'purpose_cross_replay_publish_to_restore','old_domain_hmac',
          'B39_C99_STRUCTURAL_PASS_NEVER_AUTHORIZES_ACK=VERIFIED',
          'B39_ESP32_KEY_PROVISIONING_DOMAIN_POLICY_ATOMIC_CAS=NOT_VERIFIED'):
 assert x in s,x
assert 'SECRET_KEY=' not in h and 'malloc(' not in h
print('B39_CONTRACT=PASS_HOST_SCOPE_DERIVATION_C99_STRUCTURAL_ONLY_NO_AUTH')
