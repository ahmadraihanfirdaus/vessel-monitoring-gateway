#!/usr/bin/env python3
"""Structural test for real routes, no-DB fixture and CI B9 scope; not HTTP runtime proof."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class B9Scope(unittest.TestCase):
 def test_real_routes_and_full_boundaries(self):
  api=(ROOT/'backend/laravel/routes/api.php').read_text()
  middleware=(ROOT/'backend/laravel/app/Http/Middleware/EnsureTelemetryPayloadSize.php').read_text()
  test=(ROOT/'backend/laravel/tests/Feature/Phase9B9HttpBoundaryTest.php').read_text()
  for route in ("'/v1/telemetry'", "'/v1/events'", "'/v1/device/state'", "'/v1/device/history'", "'/v1/device/health'"):
   self.assertIn(route,api)
  self.assertGreaterEqual(api.count("'device.auth'"),5)
  self.assertGreaterEqual(api.count("'telemetry.payload.size'"),2)
  self.assertIn("if (! $request->isJson())",middleware)
  self.assertIn('->assertStatus(415)',test)
  self.assertIn('TelemetryIngestService::IDENTICAL',test)
  self.assertIn('Mockery::mock(DeviceReadService::class)',test)
  for bad in ('RefreshDatabase','artisan migrate','DB::table(', 'Device::query('):self.assertNotIn(bad,test)
 def test_ci_no_database_job(self):
  ci=(ROOT/'.github/workflows/phase9-multi-context-ci.yml').read_text()
  self.assertIn('backend-http-no-db-b9:',ci)
  b9=ci.split('backend-http-no-db-b9:',1)[1]
  self.assertIn('DB_PORT:',b9)
  self.assertIn("DB_CONNECTION: mysql",b9)
  self.assertIn('Phase9B9HttpBoundaryTest',b9)
  for forbidden in ('php artisan migrate','RefreshDatabase','services:\n      mysql:'):
   self.assertNotIn(forbidden,b9)
 def test_open_formal_trace(self):
  s=(ROOT/'docs/testing/phase9-b9-scoped-trace.csv').read_text()
  for id in ('API-001','SEC-002','TEL-001','TEL-003','NET-002','UI-002','TST-001'):
   self.assertIn(id,s)
  self.assertIn('FORMAL_OPEN',s)
if __name__=='__main__':unittest.main(verbosity=2)
