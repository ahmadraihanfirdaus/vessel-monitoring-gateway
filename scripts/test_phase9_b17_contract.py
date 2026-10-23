from pathlib import Path
R=Path(__file__).resolve().parents[1]
php=(R/'backend/laravel/tests/Feature/Phase9B17HttpReceiptExportTest.php').read_text()
py=(R/'scripts/phase9_b17_receipt_crosscheck.py').read_text()
c=(R/'scripts/phase9_b17_receipt_policy_fixture.c').read_text()
assert php.count('public function test_')==8
assert "'origin_verified' => false" in php and "shouldNotReceive('resolve')" in php
assert 'Cache-Control' in php and 'VG_B17_RECEIPTS_JSONL' in php
assert 'new QueryException(' in php and 'Mockery' in php
assert 'phase9_b16_receipt_gate.h' in c and 'vg_b16_commit_receipt' in c
assert 'strict_json' in py and 'duplicate_json_key' in py
assert 'authenticated_response_verified' in c and 'local_safety_pass' in c
print('B17_CONTRACT=PASS_HTTP_RECEIPT_SOURCE_HOST_BOUNDARY')
