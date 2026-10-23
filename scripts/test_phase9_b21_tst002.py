#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for script in ('test_phase9_b21_cut_matrix.py','test_phase9_b21_contract.py',
               'test_phase9_b21_negative.py','test_phase9_b21_tst002.py'):
    assert s.count('python3 -B scripts/'+script)==1,script
assert 'B21 exhaustive host checkpoint fault matrix' in s
assert 'backend-mysql-isolated:' in s and 'firmware-host:' in s
for p in ('docs/testing/phase9-b21-exhaustive-cut-matrix.md',
          'docs/testing/phase9-b21-scoped-trace.csv'):
    assert (R/p).is_file(),p
print('B21_TST002=PASS_CI_HOST_ONLY_REGISTRATION')
