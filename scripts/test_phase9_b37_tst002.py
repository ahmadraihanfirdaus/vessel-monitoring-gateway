#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ci=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B37 host HMAC receipt authorization')==1
assert ci.index('B36 cross-language canonical checkpoint receipt interop')<ci.index('B37 host HMAC receipt authorization')<ci.index('backend-mysql-isolated:')
for suffix in ('hmac_receipt','contract','negative','tst002'):
 assert ci.count('python3 -B scripts/test_phase9_b37_'+suffix+'.py')==1,suffix
print('B37_TST002=PASS_HOST_ONLY_CI_ISOLATED_FROM_MYSQL')
