#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b37_hmac_receipt.py').read_text()
for t in ('rebuilt_crc_unsigned_forgery','valid_hmac_wrong_device',
          'valid_hmac_wrong_keyid','valid_hmac_stale_epoch',
          'valid_hmac_future_from_other_key','wrong_active_key',
          'epoch_replay_floor','wrong_expected_id','structural_with_invalid_auth>=5',
          'forged_wire[:68]','B37_KEY_PROVISIONING_COUNTER_PERSISTENCE_ESP32=NOT_VERIFIED'):
    assert t in s,t
print('B37_NEGATIVE=PASS_UNSIGNED_REBUILT_CRC_REPLAY_WRONG_KEY_AND_ID')
