#!/usr/bin/env python3
"""Verify B33 CI registration without changing MySQL isolation job."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B33 host-only revision stabilization at publication')==1
assert ci.index('B32 host-only separated checkpoint receipt input region contract')<ci.index('B33 host-only revision stabilization at publication')<ci.index('backend-mysql-isolated:')
for stem in ('stable_revision','contract','negative','tst002'):
    name='test_phase9_b33_'+stem+'.py'
    assert ci.count('python3 -B scripts/'+name)==1,name
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B33_TST002=PASS_HOST_REGISTRY_MYSQL_ISOLATION_PRESERVED')
