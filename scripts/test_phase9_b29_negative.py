#!/usr/bin/env python3
"""Require denial matrix and unchanged pre-publication output evidence."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'scripts/test_phase9_b29_publish_barrier.py').read_text()
c=(R/'scripts/phase9_b29_publish_barrier_fixture.c').read_text()
for k in ('prepare_stale','prepare_corrupt','prepare_split','prepare_replay',
          'missing_cas','stale_after','advanced_after','receipt_old_rev',
          'receipt_wrong_tag','receipt_wrong_primary','receipt_wrong_secondary',
          'receipt_wrong_round','receipt_generation','receipt_ack',
          'pending_not_ready','pending_next_witness','pending_pending_ack',
          'duplicate_receipt','null_receipt'):
    assert k in p and k in c,k
assert 'memcmp(&pending,&original,sizeof(pending))' in c
assert 'committed!=true' in c
assert 'memcmp(&published_guard,&guard_original' in c
assert 'memcmp(&published_fence,&fence_original' in c
assert 'memcmp(&published_state,&state_original' in c
print('B29_NEGATIVE=PASS_STALE_CAS_REPLAY_SPLIT_IDENTITY_NO_PARTIAL_PUBLICATION')
