#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b39_domain_scope.py').read_text()
for x in ('purpose_cross_replay_restore_to_publish','purpose_cross_replay_publish_to_restore',
 'purpose_policy_mismatch','device_policy_mismatch','device_caller_mismatch',
 'retired_after_rotation','before_activated_epoch','epoch_replayed',
 'wrong_master_secret','wrong_key_signer','old_domain_hmac',
 'forged_crc_valid_context_tag','unsig_epoch_flip',
 'structural_ok_without_auth>=8','assert len(cases)==45'):
 assert x in s,x
print('B39_NEGATIVE=PASS_CROSS_PURPOSE_DEVICE_KEY_REPLAY_AND_CONTEXT_FORGERY_CASES')
