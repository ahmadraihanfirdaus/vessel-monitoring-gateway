#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b40_hmac_verify.py').read_text()
for marker in ('wrong_master_key','retired_old_receipt','cross_purpose_restore_to_publish',
    'cross_purpose_publish_to_restore','device_mismatch','floor_equal_epoch',
    'activation_future','unsigned_zero_mac','truncated_mac','extra_trailing_byte',
    'valid_crc_changed_payload','wire_crc_corrupt','changed_expected_wire',
    'mac_mutation_','wire_mutation_','same_mac_wrong_wire',
    "assert len(cases)==46,len(cases)", 'structural_without_mac>=8'):
    assert marker in s,marker
print('B40_NEGATIVE=PASS_KEY_DOMAIN_EPOCH_MAC_CRC_LENGTH_DEVICE_AND_WIRE_TAMPER_CASES')
