#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ci=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
pre=ci.split('backend-mysql-isolated:',1)[0]
for item in ('stage_readback','contract','negative','tst002'):
    n='scripts/test_phase9_b46_'+item+'.py'
    assert pre.count(n)==1,n
assert 'backend-mysql-isolated:' in ci
assert 'backend-http-contract:' in ci or 'backend-http' in ci
print('B46_TST002=PASS_CI_HOST_ONLY_BACKEND_JOBS_PRESERVED')
