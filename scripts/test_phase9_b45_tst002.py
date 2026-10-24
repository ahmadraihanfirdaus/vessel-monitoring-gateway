#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ci=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
pre=ci.split('backend-mysql-isolated:',1)[0]
for n in ('test_phase9_b45_slot_recovery.py','test_phase9_b45_contract.py',
          'test_phase9_b45_negative.py','test_phase9_b45_tst002.py'):
    assert pre.count('scripts/'+n)==1,n
assert 'backend-mysql-isolated:' in ci
print('B45_TST002=PASS_CI_HOST_ONLY_NO_MYSQL_JOB_CHANGE')
