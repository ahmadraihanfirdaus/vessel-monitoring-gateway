#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ci=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B39 host HMAC purpose and device domain separation')==1
assert ci.index('B38 host-only receipt signing key rotation')<ci.index('B39 host HMAC purpose and device domain separation')<ci.index('backend-mysql-isolated:')
for name in ('domain_scope','contract','negative','tst002'):
 assert ci.count('python3 -B scripts/test_phase9_b39_'+name+'.py')==1,name
assert ci.count('mysql:8.0')==1
print('B39_TST002=PASS_CI_PRESERVES_MYSQL_JOB_AND_ISOLATES_HOST_SCOPE')
