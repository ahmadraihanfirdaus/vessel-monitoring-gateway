#!/usr/bin/env python3
"""Strict CI + provenance test. No MySQL job change."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B28 CAS revision fence')==1
p0=ci.index('B27 host two-round dual quorum sequence')
p1=ci.index('B28 CAS revision fence')
p2=ci.index('backend-mysql-isolated:')
assert p0<p1<p2
for name in ('test_phase9_b28_revision_fence.py','test_phase9_b28_contract.py',
             'test_phase9_b28_negative.py','test_phase9_b28_tst002.py'):
    assert ci.count('python3 -B scripts/'+name)==1,name
assert 'mysql' in ci[p2:].lower()
print('B28_TST002=PASS_CI_HOST_ONLY_MYSQL_ISOLATION_PRESERVED')
