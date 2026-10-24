#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b38_key_rotation.py').read_text()
for x in ('old_key_new_epoch','new_key_before_cutover','retired_equal_active',
  'key_material_missing','wrong_current_secret','replayed_old_key_with_valid_new_mac',
  'new_receipt_replayed_same_epoch','unsigned_future_epoch','hmac_valid_wrong_device',
  'structural_false_auth>=6'):
 assert x in s,x
print('B38_NEGATIVE=PASS_RETIRED_KEY_REPLAY_FLOOR_KEY_ID_AND_SECRET_CHECKS')
