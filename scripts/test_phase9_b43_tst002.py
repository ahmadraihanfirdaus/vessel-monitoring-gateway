#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
y=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert y.count('backend-mysql-isolated:')==1
assert y.count('B43 host-only bounded nonce replay denial')==1
assert y.index('B42 host session challenge bound authenticated receipt')<y.index('B43 host-only bounded nonce replay denial')<y.index('backend-mysql-isolated:')
for n in ('nonce_ledger','contract','negative','tst002'):
    assert y.count('python3 -B scripts/test_phase9_b43_'+n+'.py')==1,n
assert y.count('mysql:8.0')==1
print('B43_TST002=PASS_HOST_NONCE_LEDGER_AND_MYSQL_CI_ISOLATION')
