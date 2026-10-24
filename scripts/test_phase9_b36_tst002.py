#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
ci=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B36 cross-language canonical checkpoint receipt interop')==1
assert ci.index('B35 canonical host wire receipt')<ci.index('B36 cross-language canonical checkpoint receipt interop')<ci.index('backend-mysql-isolated:')
for stem in ('wire_interop','contract','negative','tst002'):
 assert ci.count('python3 -B scripts/test_phase9_b36_'+stem+'.py')==1,stem
print('B36_TST002=PASS_HOST_REGISTRY_MYSQL_BOUNDARY_UNCHANGED')
