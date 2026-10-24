#!/usr/bin/env python3
"""Host-only publication output isolation contract assertions."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b31_publish_isolation_host.h').read_text()
f=(R/'scripts/phase9_b31_publish_isolation_fixture.c').read_text()
for marker in ('vg_b31_finalize_isolated(', 'vg_b31_region_of(',
    'vg_b31_overlaps(', 'UINTPTR_MAX', 'vg_b30_finalize_exact(',
    'vg_b31_overlaps(inputs[i],inputs[3])',
    'vg_b31_overlaps(outputs[i],inputs[j])',
    'vg_b31_overlaps(outputs[i],outputs[j])',
    'NOT memory protection','NOT', 'readback_len>VG_B19_SLOT_MAX'):
    assert marker in h,marker
for marker in ('alias_state_pending_state','alias_guard_fence',
    'alias_readback_pending_image','alias_committed_state',
    'memcmp(&pending,&pending_before','memcmp(&cas,&cas_before',
    'memcmp(&rr,&rr_before','memcmp(actual,image_before',
    'vg_b31_finalize_isolated('):
    assert marker in f,marker
for forbidden in ('malloc(', 'free(', 'system(', 'fopen(', 'sqlite',
    'PDO', 'esp_partition_write', 'crypto_auth', 'memmove('):
    assert forbidden not in h,forbidden
print('B31_CONTRACT=PASS_HOST_PUBLICATION_NONALIAS_AND_ZERO_MUTATION_ON_DENIAL')
