#!/usr/bin/env python3
"""B34 CI host registration leaves existing MySQL CI job untouched."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B34 single-envelope host checkpoint publication integrity')==1
assert ci.index('B33 host-only revision stabilization at publication') < ci.index('B34 single-envelope host checkpoint publication integrity') < ci.index('backend-mysql-isolated:')
for stem in ('publish_envelope','contract','negative','tst002'):
    name='test_phase9_b34_'+stem+'.py'
    assert ci.count('python3 -B scripts/'+name)==1,name
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B34_TST002=PASS_HOST_REGISTRY_MYSQL_ISOLATION_PRESERVED')
