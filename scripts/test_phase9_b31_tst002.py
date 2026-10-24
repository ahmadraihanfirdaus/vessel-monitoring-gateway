#!/usr/bin/env python3
"""Ensure CI includes B31 host gates while preserving isolated MySQL job."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B31 host-only publish memory alias isolation')==1
assert ci.index('B30 exact checkpoint readback binding') < ci.index('B31 host-only publish memory alias isolation') < ci.index('backend-mysql-isolated:')
for stem in ('publish_isolation','contract','negative','tst002'):
    name='test_phase9_b31_'+stem+'.py'
    assert ci.count('python3 -B scripts/'+name)==1,name
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B31_TST002=PASS_CI_HOST_ONLY_MYSQL_JOB_PRESERVED')
