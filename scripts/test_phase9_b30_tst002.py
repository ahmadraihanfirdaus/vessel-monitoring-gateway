#!/usr/bin/env python3
"""CI host-only registration; preserve isolated MySQL job."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B30 exact checkpoint readback binding')==1
assert ci.index('B29 two phase external CAS publish barrier') < ci.index('B30 exact checkpoint readback binding') < ci.index('backend-mysql-isolated:')
for stem in ('exact_readback','contract','negative','tst002'):
    name='test_phase9_b30_'+stem+'.py'
    assert ci.count('python3 -B scripts/'+name)==1,name
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B30_TST002=PASS_CI_HOST_ONLY_MYSQL_JOB_PRESERVED')
