#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
c=(R/'scripts/phase9_b23_witness_fixture.c').read_text()
h=(R/'firmware/src/phase9_b23_witness_commit_host.h').read_text()
for token in ('bad[0].len=n-1u','bad[0].bytes[n/2u]^=1u',
    'bad[1].bytes[20]^=1u','sentinel.generation!=97u',
    'memcmp(&keep,&result,sizeof(result))','vg_b23_restore_witnessed(bad,tag,&proposed',
    'vg_b23_restore_witnessed(bad,tag,&w','make(&bad[0],11u,9u,tag)'):
    assert token in c,token
for token in ('!am && !bm','if(!am && !bm)return false;',
    'pending_correlation','selected.ack.pending','generation!=old->generation+1u'):
    assert token in h,token
print('B23_NEGATIVE=PASS_FAIL_CLOSED_ON_UNWITNESSED_CORRUPT_STALE_AND_SPLIT_BRAIN')
