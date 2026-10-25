#!/usr/bin/env python3
"""Source-policy check only; Laravel actual dispatch is mandatory and separate."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]
class Boundary(unittest.TestCase):
    def test_middleware_uses_no_store_private(self):
        src=(R/'backend/laravel/app/Http/Middleware/NoStoreDeviceResponse.php').read_text()
        for text in ["'no-store, private'", "'no-cache'", "setVary('Authorization', false)"]:
            self.assertIn(text,src)
    def test_registration_and_six_route_bindings(self):
        bootstrap=(R/'backend/laravel/bootstrap/app.php').read_text()
        routes=(R/'backend/laravel/routes/api.php').read_text()
        self.assertIn("'device.response.no-store' =>",bootstrap)
        self.assertIn("'/v1/device/events'",routes)
        self.assertEqual(routes.count("'device.response.no-store'"),6)
        self.assertEqual(routes.count("'device.auth'"),6)
        self.assertEqual(routes.count("'telemetry.payload.size'"),2)
        self.assertLess(routes.index("'device.response.no-store'"),routes.index("'telemetry.payload.size'"))
    def test_no_db_in_feature_tests(self):
        s=(R/'backend/laravel/tests/Feature/Phase9B12CacheBoundaryTest.php').read_text()
        for bad in ['RefreshDatabase', 'DB::', 'artisan migrate', 'Sqlite', 'PDO::']:
            self.assertNotIn(bad,s)
        self.assertEqual(s.count('public function test_'),8)
if __name__=='__main__':unittest.main(verbosity=2)
