#!/usr/bin/env python3
"""Supplementary source-policy checks; the Laravel HTTP suite is the actual behavior gate."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Contract(unittest.TestCase):
    def test_runtime_production_file_is_concrete(self):
        s=(ROOT/'backend/laravel/app/Http/Middleware/EnsureTelemetryPayloadSize.php').read_text()
        self.assertIn('unsupported_telemetry_media_type',s)
        self.assertIn('preg_match(',s)
        self.assertNotIn('if (! $request->isJson())',s)
    def test_backend_fault_not_caught_as_cursor_error(self):
        s=(ROOT/'backend/laravel/app/Http/Controllers/Api/DeviceHistoryController.php').read_text()
        self.assertIn('Cursor::fromEncoded($cursor)',s)
        self.assertIn('$this->service->history(',s)
        self.assertLess(s.index('catch (\\Throwable)'),s.index('$this->service->history('))
        self.assertNotIn('try {\n            $body = $this->service->history',s)
    def test_laravel_test_contains_all_contexts(self):
        s=(ROOT/'backend/laravel/tests/Feature/Phase9B10HttpResilienceTest.php').read_text()
        for context in ('api001','sec002','ui002','sys003'):
            self.assertIn('test_'+context,s)
        self.assertNotIn('RefreshDatabase',s)
if __name__=='__main__':unittest.main(verbosity=2)
