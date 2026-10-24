#!/usr/bin/env python3
"""Fail closed if output alias cases or readback separation weaken."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
case=(R/'scripts/test_phase9_b31_publish_isolation.py').read_text()
fixture=(R/'scripts/phase9_b31_publish_isolation_fixture.c').read_text()
header=(R/'firmware/src/phase9_b31_publish_isolation_host.h').read_text()
for marker in ('alias_readback_pending_image','alias_readback_pending_prefix',
  'alias_readback_cas','alias_readback_rr',
  'alias_guard_pending_guard','alias_fence_pending_fence',
  'alias_state_pending_state','alias_committed_cas','alias_committed_receipt',
  'alias_guard_fence','alias_state_guard','alias_state_fence',
  'alias_committed_state','alias_state_actual','alias_fence_actual',
  'null_out_guard','null_out_fence','null_out_state','null_out_committed',
  'wrong_ack','no_external_cas','wrong_readback'):
    assert marker in case and marker in fixture,marker
assert 'len(cases)==31' in case
assert 'for(unsigned j=i+1u;j<4u;j++)' in header
assert 'for(unsigned j=0u;j<4u;j++)' in header
assert 'for(unsigned i=0u;i<3u;i++)' in header
print('B31_NEGATIVE=PASS_OVERLAP_DENIAL_MATRIX_READBACK_INDEPENDENCE')
