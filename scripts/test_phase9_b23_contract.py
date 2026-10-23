#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b23_witness_commit_host.h').read_text()
c=(R/'scripts/phase9_b23_witness_fixture.c').read_text()
for token in ('vg_b23_restore_witnessed','vg_b23_prepare_witnessed',
    'vg_b23_propose_after_readback','vg_b19_decode','vg_b19_select',
    'vg_b20_verify_readback','old->generation==UINT32_MAX',
    'caller','CRC is','*out=selected','*proposal=local'):
    assert token.lower() in h.lower(),token
for token in ('-Werror','SQLSTATE','php artisan','ESP32 certified'):
    assert token not in h,token
for token in ('vg_b23_witness w={11u,8u}','vg_b23_witness proposed=',
    'B23_ESP_NVS_POWERLOSS_NETWORK_DB=NOT_VERIFIED'):
    assert token in c,token
print('B23_CONTRACT=PASS_EXACT_WITNESS_NO_FALSE_DURABILITY_CLAIM')
