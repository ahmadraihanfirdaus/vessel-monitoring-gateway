import csv,pathlib,unittest
P=pathlib.Path(__file__).resolve().parents[1]
class Trace(unittest.TestCase):
 def test_exact_scoped_map(self):
  with (P/'docs/testing/phase9-b6-scoped-trace.csv').open(newline='') as f:r=list(csv.DictReader(f))
  self.assertEqual({x['context'] for x in r},{'TEL-001','TEL-002','API-001','NET-002','TST-001'})
  self.assertEqual(len(r),5)
  self.assertTrue(all(x['formal_status']=='OPEN' and x['runtime_boundary']=='HOST_NO_NETWORK_NO_DB' for x in r))
 def test_existing_boundary_protected(self):
  self.assertIn('No HTTP', (P/'docs/testing/phase9-b6-host-boundary.md').read_text())
if __name__=='__main__':unittest.main(verbosity=2)
