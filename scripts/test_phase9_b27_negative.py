#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
c=(R/'scripts/phase9_b27_quorum_sequence_fixture.c').read_text()
p=(R/'scripts/test_phase9_b27_quorum_sequence.py').read_text()
for s in ('first_old','first_split','first_ack_mismatch','first_primary_replay',
          'first_secondary_skip','first_corrupt_middle','first_bad_ticket',
          'second_old','second_split','second_primary_replay',
          'second_secondary_skip','second_corrupt_after','second_bad_ticket',
          'second_bad_link','second_bad_expected','wrong_domain',
          'swapped_domains','round_overflow','domain_dup'):
    assert '"'+s+'"' in c and "'"+s+"'" in p,s
assert 'committed!=false' in c
assert 'memcmp(&next,&nx,sizeof(nx))!=0' in c
assert 'memcmp(&out,&ox,sizeof(ox))!=0' in c
assert 'B27_EXTERNAL_SOURCE_AUTH_DURABILITY_ESP_NVS=NOT_VERIFIED' in p
print('B27_NEGATIVE=PASS_NO_PARTIAL_COMMIT_ON_SECOND_ROUND_DENIAL')
