from pathlib import Path
R=Path(__file__).resolve().parents[1]
ci=(R/'.github/workflows/phase9-multi-context-ci.yml').read_text()
assert 'Phase9B17HttpReceiptExportTest' in ci
assert 'VG_B17_RECEIPTS_JSONL' in ci
assert 'phase9_b17_receipt_crosscheck.py' in ci
assert 'test_phase9_b17_negative.py' in ci
assert 'backend-http-no-db-b9:' in ci and 'backend-mysql-isolated:' in ci
assert ci.count('backend-http-no-db-b9:')==1
print('B17_CI=PASS_ISOLATED_HTTP_RECONCILIATION')
