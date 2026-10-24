#!/usr/bin/env python3
"""B33 two external revision reads, no premature publication contract."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b33_stable_revision_host.h').read_text()
f=(R/'scripts/phase9_b33_stable_revision_fixture.c').read_text()
for marker in ('vg_b33_finalize_stable_revision(',
    'vg_b33_revision_probe', 'if(!probe(probe_context,&before)',
    'if(!probe(probe_context,&after)', 'after!=before',
    'vg_b32_finalize_separated_inputs(',
    'memcmp(pending,&held_pending', 'memcmp(cas,&held_cas',
    'memcmp(rr,&held_rr','memcmp(readback,held_readback,readback_len)',
    'vg_b31_overlaps(outputs[i],inputs[j])',
    '*committed=true;', 'NOT a lock-free atomic multi-field publish'):
    assert marker in h,marker
for case in ('probe_first_fail','probe_second_fail','probe_first_wrong_revision',
    'probe_second_wrong_revision','probe_first_mutate_pending',
    'probe_second_mutate_readback', 'null_probe','null_context'):
    assert case in f,case
assert h.index('if(!probe(probe_context,&after)') < h.index('*published_guard=candidate_guard;')
for forbidden in ('malloc(', 'free(', 'system(', 'fopen(', 'sqlite',
    'PDO','esp_partition_write','crypto_auth','memmove('):
    assert forbidden not in h,forbidden
print('B33_CONTRACT=PASS_TWO_PROBES_STAGED_OUTPUT_ZERO_PREMATURE_WRITES')
