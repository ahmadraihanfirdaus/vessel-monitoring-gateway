from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert 'python3 -B scripts/test_phase9_b16_receipt_gate.py' in ci
assert 'python3 -B scripts/test_phase9_b16_contract.py' in ci
assert 'php artisan test --filter=Phase9B16ReceiptReplayTest' in ci
assert 'VG_B14_WIRE_JSONL' in ci and 'VG_B15_EVENT_JSONL' in ci
assert ci.count('backend-http-no-db-b9:')==1
assert 'backend-mysql-isolated:' in ci and 'firmware-host:' in ci
print('B16_CI=PASS_SCOPED_NO_DB_HTTP_RUNNER')
