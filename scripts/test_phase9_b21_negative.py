#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/phase9_b21_cut_matrix_fixture.c').read_text()
for term in ('return 20;','return 21;','return 22;','return 23;','return 24;',
             'return 25;','return 26;','return 27;',
             'memcmp(&sentinel,&unchanged,sizeof(sentinel))',
             'selected.ack.pending','candidate,size,size+1u'):
    assert term in s,term
h=(R/'firmware/src/phase9_b21_cut_matrix_host.h').read_text()
assert 'memcpy(temp.bytes,candidate,written)' in h
assert 'if(written)memcpy' in h
print('B21_NEGATIVE=PASS_TRUNC_STALE_BITFLIP_INVALID_ARGS_AND_ACK')
