#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ci=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B35 canonical host wire receipt and no-write failure matrix')==1
assert ci.index('B34 single-envelope host checkpoint publication integrity')<ci.index('B35 canonical host wire receipt and no-write failure matrix')<ci.index('backend-mysql-isolated:')
for stem in ('wire_receipt','contract','negative','tst002'):
 name='test_phase9_b35_'+stem+'.py'
 assert ci.count('python3 -B scripts/'+name)==1,name
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B35_TST002=PASS_HOST_REGISTRY_MYSQL_ISOLATION_PRESERVED')
