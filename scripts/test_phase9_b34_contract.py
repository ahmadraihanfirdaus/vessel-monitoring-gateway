#!/usr/bin/env python3
"""B34 envelope is sourced from guarded B33 and coherent checkpoint fields."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b34_publish_envelope_host.h').read_text()
f=(R/'scripts/phase9_b34_publish_envelope_fixture.c').read_text()
for name in ('vg_b34_finalize_envelope(', 'vg_b33_finalize_stable_revision(',
    'vg_b31_region_of(', 'vg_b31_overlaps(', '*published=candidate;',
    'candidate.state.generation!=pending->base.next_state.generation',
    'candidate.state.ack.last_accepted_sequence!=',
    'candidate.guard.primary.last_witness.confirmed_ack',
    'candidate.valid_marker=VG_B34_ENVELOPE_VALID;',
    'vg_b18_crc32(readback,readback_len)', 'atomic publication for concurrent readers'):
    assert name in h,name
assert h.index('vg_b33_finalize_stable_revision(')<h.index('*published=candidate;')
assert h.index('candidate.valid_marker=VG_B34_ENVELOPE_VALID')<h.index('*published=candidate;')
for name in ('alias_output_pending','alias_output_cas','alias_output_rr',
  'alias_output_readback','probe_second_mutate_readback','wrong_ack'):
    assert name in f,name
for forbidden in ('malloc(', 'free(', 'system(', 'fopen(', 'PDO','esp_partition_write'):
    assert forbidden not in h,forbidden
print('B34_CONTRACT=PASS_PRIVATE_OUTPUT_ENVELOPE_AND_COHERENCE')
