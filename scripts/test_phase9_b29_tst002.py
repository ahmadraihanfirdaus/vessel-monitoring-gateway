#!/usr/bin/env python3
"""CI registration must not modify the existing isolated MySQL job."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert ci.count('backend-mysql-isolated:')==1
assert ci.count('B29 two phase external CAS publish barrier')==1
assert ci.index('B28 CAS revision fence')<ci.index('B29 two phase external CAS publish barrier')<ci.index('backend-mysql-isolated:')
for stem in ('publish_barrier','contract','negative','tst002'):
    name='test_phase9_b29_'+stem+'.py'
    assert ci.count('python3 -B scripts/'+name)==1,name
assert 'mysql' in ci[ci.index('backend-mysql-isolated:'):].lower()
print('B29_TST002=PASS_CI_HOST_ONLY_MYSQL_JOB_PRESERVED')
