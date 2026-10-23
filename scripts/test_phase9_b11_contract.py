#!/usr/bin/env python3
"""Static contract checks complement actual PHPUnit HTTP runtime tests."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
support=(root/'backend/laravel/app/Support/DependencyUnavailableResponse.php').read_text()
assert "'backend_temporarily_unavailable'" in support and "503" in support
assert "'Retry-After', '5'" in support
paths=[
    'app/Http/Middleware/AuthenticateDeviceToken.php',
    'app/Http/Controllers/Api/TelemetryIngestController.php',
    'app/Http/Controllers/Api/EventIngestController.php',
    'app/Http/Controllers/Api/DeviceStateController.php',
    'app/Http/Controllers/Api/DeviceHistoryController.php',
    'app/Http/Controllers/Api/DeviceHealthController.php',
]
for path in paths:
    text=(root/'backend/laravel'/path).read_text()
    assert 'catch (QueryException $exception)' in text, path
    assert 'DependencyUnavailableResponse::forConnectionFailure($exception)' in text, path
    assert 'throw $exception;' in text, path
test=(root/'backend/laravel/tests/Feature/Phase9B11DependencyUnavailableTest.php').read_text()
assert test.count('public function test_')==9
print('B11_HTTP_DEPENDENCY_CONTRACT=PASS_6_RUNTIME_BOUNDARIES_9_CASES')
