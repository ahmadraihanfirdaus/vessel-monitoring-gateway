"""Verify B14 CI uses C99 emitted bytes and actual Laravel route with no DB."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class CI(unittest.TestCase):
 def test_bridge_gated_in_no_db_job(self):
  ci=(ROOT/'.github/workflows/phase9-multi-context-ci.yml').read_text()
  job=ci.split('backend-http-no-db-b9:',1)[1]
  for fragment in ('phase9_b14_wire_bridge.py', 'Phase9B14FirmwareWireHttpTest','VG_B14_WIRE_JSONL'):
   self.assertIn(fragment,job)
  self.assertNotIn('php artisan migrate',job)
 def test_compiler_fails_closed(self):
  script=(ROOT/'scripts/phase9_b14_wire_bridge.py').read_text()
  for term in ('-Werror','TemporaryDirectory','compiled.returncode', 'json.loads', 'sequence', "path.open('xb')"):
   self.assertIn(term,script)
if __name__=='__main__':unittest.main(verbosity=2)
