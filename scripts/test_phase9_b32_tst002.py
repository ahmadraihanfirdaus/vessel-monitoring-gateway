#!/usr/bin/env python3
"""B32 CI remains an isolated host-only job; keep B9-B17 Laravel/MySQL."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B32 host-only separated checkpoint receipt input region contract')==1
assert ci.index('B31 host-only publish memory alias isolation')<ci.index('B32 host-only separated checkpoint receipt input region contract')<ci.index('backend-mysql-isolated:')
for stem in ('input_provenance','contract','negative','tst002'):
    name='test_phase9_b32_'+stem+'.py'
    assert ci.count('python3 -B scripts/'+name)==1,name
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B32_TST002=PASS_HOST_REGISTRY_MYSQL_ISOLATION_PRESERVED')
