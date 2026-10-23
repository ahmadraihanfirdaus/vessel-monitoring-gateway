#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for name in ('test_phase9_b27_quorum_sequence.py','test_phase9_b27_contract.py',
             'test_phase9_b27_negative.py','test_phase9_b27_tst002.py'):
    assert 'python3 -B scripts/'+name in ci,name
assert ci.count('backend-mysql-isolated:')==1
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
assert 'B26 two-source host witness agreement' in ci
print('B27_TST002=PASS_HOST_CI_REGISTERED_PRESERVED_MYSQL_JOB')
