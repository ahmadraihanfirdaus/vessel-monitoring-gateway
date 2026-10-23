#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
c=(r/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert 'test_phase9_b13_cursor_contract.py' in c
assert 'test_phase9_b13_tst002.py' in c
assert 'Phase9B13CursorContractTest' in c
assert 'backend-http-no-db-b9:' in c
assert 'backend-mysql-isolated:' in c
assert "DB_PORT: '1'" in c
assert 'php artisan migrate --force' in c  # Existing isolated CI job, not runner
print('B13_CI_POLICY=PASS')
