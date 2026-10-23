#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for path in ('test_phase9_b25_observation_epoch.py','test_phase9_b25_contract.py',
             'test_phase9_b25_negative.py','test_phase9_b25_tst002.py'):
    assert 'python3 -B scripts/'+path in ci,path
assert ci.count('backend-mysql-isolated:')==1
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B25_TST002=PASS_CI_HOST_GATES_AND_PRESERVED_MYSQL_JOB')
