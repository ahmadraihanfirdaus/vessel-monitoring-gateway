#!/usr/bin/env python3
"""Confirm CI runs Laravel B11 tests in no-DB job, not in core-only checks."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ci=(root/'.github/workflows/phase9-multi-context-ci.yml').read_text()
zone=ci.split('backend-http-no-db-b9:',1)[1]
assert '--filter=Phase9B11DependencyUnavailableTest' in zone
assert 'test_phase9_b11_contract.py' in zone
assert 'test_phase9_b11_tst002.py' in zone
assert 'DB_PORT:' in zone and "'1'" in zone
assert 'php artisan migrate' not in zone and 'mysql:' not in zone
print('B11_CI_POLICY=PASS_NO_DB_HTTP_TEST_JOB')
