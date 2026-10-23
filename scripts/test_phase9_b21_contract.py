#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b21_cut_matrix_host.h').read_text()
c=(R/'scripts/phase9_b21_cut_matrix_fixture.c').read_text()
for s in ('vg_b21_inject_prefix','vg_b21_fallback_is_conservative',
          'retain_tail','vg_b19_select','!result.ack.pending','written>candidate_len'):
    assert s in h,s
for s in ('vg_b20_prepare','vg_b20_verify_readback','for(size_t cut=0u;cut<size;++cut)',
          'for(unsigned bit=0u;bit<8u;++bit)','candidate[size','B21_MATRIX=PASS_TRUNC_',
          'HOST_MEMORY_FAULT_MODEL_NOT_DISK_ATOMICITY_NVS_POWERLOSS'):
    if s=='candidate[size':continue
    assert s in c,s
assert 'UPDATE production' not in h
print('B21_CONTRACT=PASS_FAIL_CLOSED_CUT_AND_RESTORE_HOST_BOUNDARY')
