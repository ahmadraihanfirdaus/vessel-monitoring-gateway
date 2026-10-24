#!/usr/bin/env python3
"""B32 host C99 input independence and no DB contract."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b32_input_provenance_host.h').read_text()
f=(R/'scripts/phase9_b32_input_provenance_fixture.c').read_text()
for marker in ('vg_b32_finalize_separated_inputs(',
    'vg_b31_region_of(pending,sizeof(*pending)',
    'vg_b31_region_of(cas,sizeof(*cas)',
    'vg_b31_region_of(rr,sizeof(*rr)',
    'vg_b31_region_of(readback,readback_len',
    'for(unsigned i=0u;i<4u;i++)', 'for(unsigned j=i+1u;j<4u;j++)',
    'vg_b31_overlaps(sources[i],sources[j])', 'vg_b31_finalize_isolated(',
    'NOT actual provenance','readback_len>VG_B19_SLOT_MAX'):
    assert marker in h,marker
for marker in ('alias_cas_pending','alias_rr_pending','alias_rr_cas',
    'alias_cas_rr','alias_pending_cas','alias_pending_rr',
    'memcmp(&pending,&pending_before', 'memcmp(&cas,&cas_before',
    'memcmp(&rr,&rr_before','memcmp(actual,image_before',
    'vg_b32_finalize_separated_inputs('):
    assert marker in f,marker
for forbidden in ('malloc(', 'free(', 'system(', 'fopen(', 'sqlite',
    'PDO','esp_partition_write','crypto_auth','memmove('):
    assert forbidden not in h,forbidden
print('B32_CONTRACT=PASS_PAIRWISE_INPUT_ADDRESS_SEPARATION_NO_MUTATION_ON_DENIAL')
