#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
y=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert y.count('backend-mysql-isolated:')==1
assert y.count('B41 host key cutover revision fence')==1
assert y.index('B40 standalone C99 HMAC verifier matched to Python oracle') < y.index('B41 host key cutover revision fence') < y.index('backend-mysql-isolated:')
for n in ('rotation_fence','contract','negative','tst002'):
    assert y.count('python3 -B scripts/test_phase9_b41_'+n+'.py')==1,n
assert y.count('mysql:8.0')==1
print('B41_TST002=PASS_CI_HOST_JOB_REGISTERED_WITH_MYSQL_ISOLATION')
