#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for p in ('test_phase9_b22_guarded_restore.py','test_phase9_b22_contract.py',
          'test_phase9_b22_negative.py','test_phase9_b22_tst002.py'):
    assert s.count('python3 -B scripts/'+p)==1,p
for p in ('docs/testing/phase9-b22-rollback-witness.md',
          'docs/testing/phase9-b22-scoped-trace.csv'):
    assert (R/p).is_file(),p
assert 'B22 host-only monotonic restore witness' in s
assert 'backend-mysql-isolated:' in s and 'firmware-host:' in s
print('B22_TST002=PASS_HOST_CI_REGISTERED')
