import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Trace(unittest.TestCase):
 def test_mapping_5_contexts(self):
  with (ROOT/'docs/testing/phase9-b5-scoped-trace.csv').open(newline='') as f:rows=list(csv.DictReader(f))
  self.assertEqual({r['requirement'] for r in rows},{'API-001','TEL-003','NET-002','SEC-002','TST-001'})
  self.assertEqual(len(rows),5)
  for r in rows:
   self.assertEqual(r['formal_status'],'FORMAL_OPEN')
   self.assertTrue((ROOT/r['source']).is_file())
   self.assertTrue((ROOT/r['test']).is_file())
if __name__=='__main__':unittest.main(verbosity=2)
