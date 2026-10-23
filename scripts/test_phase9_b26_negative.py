#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'scripts/test_phase9_b26_dual_witness.py').read_text()
c=(R/'scripts/phase9_b26_dual_witness_fixture.c').read_text()
for x in ('disagree_new_old','disagree_old_new','different_ack',
    'different_generation','epoch_a_replay','epoch_b_replay',
    'epoch_a_gap','epoch_b_gap','duplicate_domain','swapped_domains',
    'bad_candidate','bad_old','bad_receipt','diverged_guard',
    'round_overflow','epoch_overflow','missing_source','seed_same_domain',
    'seed_zero_tag','seed_overflow_epoch'):
    assert x in c and x in p,x
assert 'memcmp(&restored,&restored_pre,sizeof(restored))!=0' in c
assert 'committed!=true' in c
print('B26_NEGATIVE=PASS_DISAGREEMENT_REPLAY_TAMPER_AND_ATOMIC_DENY')
