#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
for name in ('test_phase9_b24_witness_receipt.py','test_phase9_b24_contract.py',
             'test_phase9_b24_negative.py','test_phase9_b24_tst002.py'):
 assert ci.count('python3 -B scripts/'+name)==1,name
assert ci.count('B24 host witness receipt observation and interruption matrix')==1
for name in ('docs/testing/phase9-b24-witness-receipt.md',
             'docs/testing/phase9-b24-scoped-trace.csv'):
 assert (R/name).is_file(),name
assert 'backend-mysql-isolated:' in ci
print('B24_TST002=PASS_CI_REGISTERED_AND_MOCK_DB_BOUNDARY_PRESERVED')
