#!/usr/bin/env python3
"""Fail closed if B33 host source drops source snapshot or revalidation."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b33_stable_revision_host.h').read_text()
c=(R/'scripts/test_phase9_b33_stable_revision.py').read_text()
assert c.count('probe_first_mutate_')>=4 and c.count('probe_second_mutate_')>=4
for term in ('before!=externally_expected_after_revision', 'after!=before',
             'memcmp(pending,&held_pending','memcmp(readback,held_readback,readback_len)',
             '*published_guard=candidate_guard','*published_state=candidate_state'):
    assert h.count(term)>=1,term
assert h.count('vg_b31_overlaps(')==3
print('B33_NEGATIVE=PASS_REVISION_AND_MUTATION_GUARDS_PRESENT')
