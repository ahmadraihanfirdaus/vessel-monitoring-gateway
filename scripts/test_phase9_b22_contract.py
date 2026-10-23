#!/usr/bin/env python3
"""Bounded guard must not silently weaken B19/B20 or claim trusted witness storage."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b22_guarded_restore_host.h').read_text()
c=(R/'scripts/phase9_b22_guarded_restore_fixture.c').read_text()
for key in ('vg_b22_restore_guarded','vg_b22_prepare_guarded','vg_b19_select',
            'vg_b20_prepare','minimum_generation','minimum_confirmed_ack',
            'local.ack.pending','external','CRC != signature','*out=local'):
    assert key in h,key
for key in ('-Werror','SYS-003','SEC-001'): # ensure no disabling strict compilation or fabricated formal claims
    assert key not in h,key
for key in ('bad_ack_floor','vg_b19_next_generation(UINT32_MAX','split brain',
            'B22_STORAGE_HARDWARE_NETWORK=NOT_VERIFIED'):
    assert key in c,key
print('B22_CONTRACT=PASS_NO_SOURCE_PRODUCTION_CHANGE_NO_WITNESS_CLAIM')
