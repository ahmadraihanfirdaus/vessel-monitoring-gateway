#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for t in ('test_phase9_b23_witness.py','test_phase9_b23_contract.py',
          'test_phase9_b23_negative.py','test_phase9_b23_tst002.py'):
    assert s.count('python3 -B scripts/'+t)==1,t
assert s.count('B23 host exact witnessed commit boundary')==1
assert 'backend-mysql-isolated:' in s and 'firmware-host:' in s
for path in ('docs/testing/phase9-b23-witness-commit.md',
             'docs/testing/phase9-b23-scoped-trace.csv'):
    assert (R/path).is_file(),path
print('B23_TST002=PASS_HOST_CI_SUITES_REGISTERED')
