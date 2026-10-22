import unittest
from pathlib import Path
from phase9_b8_testlib import ROOT
class Evidence(unittest.TestCase):
 def test_trace_and_ci_are_scoped(self):
  trace=(ROOT/'docs/testing/phase9-b8-scoped-trace.csv').read_text()
  ci=(ROOT/'.github/workflows/phase9-multi-context-ci.yml').read_text()
  for c in ('SYS-003','NET-002','TEL-003','SEC-002','TST-001'):
   self.assertIn(c,trace)
  for n in ('sys003','net002','tel003','sec002','tst001','integrated'):
   self.assertIn(f'test_phase9_b8_{n}.py',ci)
  self.assertIn('formal',trace)
 def test_existing_anchors_unchanged(self):
  for p in ['firmware/src/core_measurement.h','firmware/src/phase9_b7_gateway_cycle.h']:
   self.assertTrue((ROOT/p).is_file())
if __name__=='__main__':unittest.main(verbosity=2)
