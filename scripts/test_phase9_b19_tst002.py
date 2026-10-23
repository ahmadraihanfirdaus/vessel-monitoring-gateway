#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ci=(ROOT/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for item in ('test_phase9_b18_checkpoint.py','test_phase9_b19_dual_slot.py',
             'test_phase9_b19_contract.py','test_phase9_b19_negative.py',
             'test_phase9_b19_tst002.py'):
    assert ci.count('scripts/'+item)==1,item
assert 'backend-mysql-isolated:' in ci and 'firmware-host:' in ci
print('B19_CI=PASS_HOST_AND_BACKEND_ISOLATION_PRESERVED')
