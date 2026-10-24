#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b41_rotation_fence.py').read_text()
for marker in ('old_after_cutover','retired_policy_after','new_revision',
               'wrong_after_source','floor_equal','bad_key_id','mac_zero',
               'flipped_mac_','flipped_wire_','alias_output_before',
               'assert len(cases)==52,len(cases)',
               'assert (result==\'B41_ROTATION_FENCE=ACCEPT_TEST_ONLY\')==expect'):
    assert marker in s,marker
print('B41_NEGATIVE=PASS_STALE_REVISION_REVOKED_KEY_SOURCE_POLICY_AND_MAC_TAMPER')
