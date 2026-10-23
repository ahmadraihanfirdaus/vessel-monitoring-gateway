#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b26_dual_witness_host.h').read_text()
c=(R/'scripts/phase9_b26_dual_witness_fixture.c').read_text()
for m in ('vg_b26_seed','vg_b26_confirm','primary_domain==secondary_domain',
          'vg_b25_observe','primary_witness->generation!=secondary_witness->generation',
          'primary_witness->confirmed_ack!=secondary_witness->confirmed_ack',
          'guard->accepted_round==UINT64_MAX','*next=candidate',
          '*restored=pr','*committed=pc','EXTERNALLY','NOT an authentication'):
    assert m.lower() in h.lower(),m
for m in ('B26_STAGE=PASS_HOST_ABI_UNTRUSTED_TWO_SOURCES','B26_QUORUM=PASS_',
          'memcmp(&next,&next_pre,sizeof(next))!=0','vg_b26_confirm('):
    assert m in c,m
for forbidden in ('php artisan','SQLSTATE[','esp_partition_write(','fsync('):
    assert forbidden not in h,forbidden
print('B26_CONTRACT=PASS_TWO_SOURCE_EPOCH_CONSENSUS_AND_OUTPUT_ATOMICITY')
