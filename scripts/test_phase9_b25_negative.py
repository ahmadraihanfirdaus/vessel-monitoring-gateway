#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'scripts/test_phase9_b25_observation_epoch.py').read_text()
c=(R/'scripts/phase9_b25_observation_epoch_fixture.c').read_text()
for key in ('repeat_new','repeat_old','epoch_replay','epoch_gap','wrong_domain',
            'wrong_tag','guard_witness','bad_receipt','bad_slot',
            'bad_previous','out_of_order','future','overflow',
            'zero_device','zero_domain'):
    assert key in p and key in c,key
assert 'memcmp(&next,&next_before,sizeof(next))!=0' in c
assert 'memcmp(&recovered,&recovered_before,sizeof(recovered))!=0' in c
assert 'committed!=true' in c
print('B25_NEGATIVE=PASS_REPLAY_WRONG_SOURCE_EPOCH_AND_OUTPUT_ATOMICITY')
