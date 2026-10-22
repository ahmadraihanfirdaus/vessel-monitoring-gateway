#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from phase9_tst001_scoped_evidence import entries
class TraceMapping(unittest.TestCase):
 def test_five_mapped_scopes(self):self.assertEqual(len(entries()),5)
 def test_no_formal_pass_claim(self):self.assertTrue(all(x['formal_status']=='NOT_RUN' for x in entries()))
 def test_unique_and_sha256(self):
  rows=entries();self.assertEqual(len({x['case_id'] for x in rows}),5)
  self.assertTrue(all(len(x['test_path_sha256'])==64 and len(x['implementation_path_sha256'])==64 for x in rows))
if __name__=='__main__':unittest.main(verbosity=2)
