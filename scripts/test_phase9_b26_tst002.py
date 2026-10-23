#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for f in ('test_phase9_b26_dual_witness.py','test_phase9_b26_contract.py',
          'test_phase9_b26_negative.py','test_phase9_b26_tst002.py'):
    assert 'python3 -B scripts/'+f in ci,f
assert ci.count('backend-mysql-isolated:')==1
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B26_TST002=PASS_REGISTERED_HOST_GATES_MYSQL_JOB_UNCHANGED')
