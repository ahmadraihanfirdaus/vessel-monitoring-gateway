#!/usr/bin/env python3
"""B32 reject any weakening of six pairwise input checks."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
c=(R/'scripts/test_phase9_b32_input_provenance.py').read_text()
f=(R/'scripts/phase9_b32_input_provenance_fixture.c').read_text()
h=(R/'firmware/src/phase9_b32_input_provenance_host.h').read_text()
for marker in ('alias_cas_pending','alias_rr_pending','alias_rr_cas',
    'alias_cas_rr','alias_pending_cas','alias_pending_rr',
    'alias_readback_pending_image','alias_readback_cas',
    'alias_guard_pending_guard','alias_state_pending_state',
    'no_external_cas','no_external_readback','wrong_revision','wrong_ack'):
    assert marker in c and marker in f,marker
assert 'len(cases)==24' in c
assert 'for(unsigned j=i+1u;j<4u;j++)' in h
assert 'vg_b31_finalize_isolated(' in h
print('B32_NEGATIVE=PASS_INPUT_ALIAS_DENIAL_AND_B31_CHAIN_PRESERVED')
