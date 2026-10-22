import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Trace(unittest.TestCase):
 def test_exact_trace_and_limits(self):
  with (ROOT/'docs/testing/phase9-b7-scoped-trace.csv').open(newline='') as stream:
   rows=list(csv.DictReader(stream))
  self.assertEqual(len(rows),5)
  self.assertEqual({x['context'] for x in rows},{'SYS-002','SYS-003','SYS-004','NET-002','TST-001'})
  self.assertTrue(all(x['formal_status']=='OPEN' and x['boundary']=='HOST_NO_DEVICE_NO_DB' for x in rows))
  doc=(ROOT/'docs/testing/phase9-b7-host-safety-boundary.md').read_text()
  for k in ('No ESP32','No HTTP','No MySQL','No actuator','No physical'):
   self.assertIn(k,doc)
 def test_ci_wires_all_cases(self):
  yml=(ROOT/'.github/workflows/phase9-multi-context-ci.yml').read_text()
  for name in ('sys002','sys003','sys004','net002','tst001','integrated'):
   self.assertIn('scripts/test_phase9_b7_'+name+'.py',yml)
if __name__=='__main__':unittest.main(verbosity=2)
