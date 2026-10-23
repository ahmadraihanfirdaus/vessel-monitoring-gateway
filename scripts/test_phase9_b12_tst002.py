#!/usr/bin/env python3
"""Verify the DB-free Laravel CI job invokes the B12 real feature tests."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
zone=s.split('backend-http-no-db-b9:',1)[1]
for token in ['test_phase9_b12_http_boundary.py','test_phase9_b12_tst002.py',
              '--filter=Phase9B12CacheBoundaryTest',"DB_PORT: '1'"]:
    assert token in zone,token
assert 'php artisan migrate' not in zone
assert 'mysql:' not in zone
print('B12_CI=PASS_DB_FREE_ROUTE_DISPATCH')
