#!/usr/bin/env python3
"""Regression evidence of security/availability fail-closed modes."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'scripts/test_phase9_b28_revision_fence.py').read_text()
c=(R/'scripts/phase9_b28_revision_fence_fixture.c').read_text()
for token in ('stale_observed','future_observed','fence_revision_zero',
              'fence_revision_overflow','fence_wrong_tag','fence_ack',
              'guard_primary_epoch','guard_secondary_epoch','guard_round_overflow',
              'first_primary_replay','second_secondary_replay','first_split',
              'second_split','corrupt_after','corrupt_expected','domain_collision',
              'alias_fence','alias_guard'):
    assert token in p and token in c,token
assert 'cx!=true' in c
assert 'result || memcmp(&next_guard,&old_guard' in c
assert 'committed!=true' in c
print('B28_NEGATIVE=PASS_30_DENIALS_STALE_CAS_SPLIT_REPLAY_CORRUPT_ATOMICITY')
