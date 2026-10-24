#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ci=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B38 host-only receipt signing key rotation')==1
assert ci.index('B37 host HMAC receipt authorization')<ci.index('B38 host-only receipt signing key rotation')<ci.index('backend-mysql-isolated:')
for n in ('key_rotation','contract','negative','tst002'):
 assert ci.count('python3 -B scripts/test_phase9_b38_'+n+'.py')==1,n
print('B38_TST002=PASS_CI_ISOLATED_FROM_MYSQL_OLD_GATES_RETAINED')
