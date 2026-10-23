#!/usr/bin/env python3
"""B13 scoped policy source inspection, no DB, no generated files."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]
controller=(r/'backend/laravel/app/Http/Controllers/Api/DeviceHistoryController.php').read_text()
helper=(r/'backend/laravel/app/Support/StrictDeviceHistoryCursor.php').read_text()
feature=(r/'backend/laravel/tests/Feature/Phase9B13CursorContractTest.php').read_text()
assert 'StrictDeviceHistoryCursor::isValid($cursor)' in controller
assert "get('authenticated_device')" in controller
assert "array_keys($parameters) !== ['received_at', 'id', '_pointsToNextItems']" in helper
assert '18446744073709551615' in helper
assert 'DateTimeImmutable::createFromFormat' in helper
assert 'cursorPaginate' in (r/'backend/laravel/app/Services/DeviceReadService.php').read_text()
assert feature.count('public function test_') == 8
print('B13_CURSOR_POLICY=PASS_8_CASES_STATIC')
