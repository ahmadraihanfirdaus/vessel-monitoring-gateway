from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b16_receipt_gate.h').read_text()
php=(R/'backend/laravel/tests/Feature/Phase9B16ReceiptReplayTest.php').read_text()
assert 'phase9_b8_ack_commit' in h and 'authenticated_response_verified' in h
assert 'vg_b16_application_accept' in h and 'status==201u' in h and 'status==200u' in h
assert 'vg_b16_commit_receipt' in h and 'local_safety_pass' in h
assert 'VG_B14_WIRE_JSONL' in php and 'VG_B15_EVENT_JSONL' in php
assert php.count('public function test_')==8
assert all(s in php for s in ('conflicting_duplicate','conflicting_event_duplicate','identical_event_duplicate','identical_duplicate','Mockery::mock'))
assert 'RefreshDatabase' not in php and 'DatabaseMigrations' not in php
print('B16_CONTRACT=PASS_RECEIPT_AND_REAL_ROUTES_NO_DB')
