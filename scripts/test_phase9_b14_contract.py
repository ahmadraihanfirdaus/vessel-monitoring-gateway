"""Source-based contract test for C99 -> Laravel DB-free HTTP bridge."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Contract(unittest.TestCase):
 def test_c99_real_serializer_and_no_fake_payload(self):
  source=(ROOT/'scripts/phase9_b14_wire_fixture.c').read_text()
  for marker in ('phase9_b6_wire_export','UINT64_MAX','VG_SOURCE_PHYSICAL','VG_QUALITY_MISSING','VG_QUALITY_VALID'):
   self.assertIn(marker,source)
 def test_laravel_real_routes_with_in_memory_services(self):
  php=(ROOT/'backend/laravel/tests/Feature/Phase9B14FirmwareWireHttpTest.php').read_text()
  for term in ('/api/v1/telemetry', 'DeviceTokenAuthenticator', 'TelemetryIngestService', 'VG_B14_WIRE_JSONL', 'CONFLICTING'):
   self.assertIn(term,php)
  for forbidden in ('RefreshDatabase', 'DatabaseMigrations', 'DB::', 'migrate:fresh', 'file_put_contents'):
   self.assertNotIn(forbidden,php)
if __name__=='__main__':unittest.main(verbosity=2)
