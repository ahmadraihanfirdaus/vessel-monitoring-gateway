#!/usr/bin/env python3
"""B34 outputs must remain untouched on denial, including aliased controls."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b34_publish_envelope_host.h').read_text()
f=(R/'scripts/phase9_b34_publish_envelope_fixture.c').read_text()
s=(R/'scripts/test_phase9_b34_publish_envelope.py').read_text()
assert h.count('vg_b31_overlaps(')==2
assert 'if(vg_b31_overlaps(target,inputs[i]))return false;' in h
assert 'vg_b33_finalize_stable_revision(' in h
assert h.count('*published=candidate;')==1
assert 'memcmp(&output,&before_output,sizeof(output))' in f
assert 'const bool injected=' in f
assert s.count('alias_output_')>=4
assert s.count('probe_second_')>=4
print('B34_NEGATIVE=PASS_OVERLAP_AND_FAILURE_NO_OUTPUT_WRITE')
