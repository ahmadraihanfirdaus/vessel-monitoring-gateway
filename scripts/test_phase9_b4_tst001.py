import subprocess,sys,unittest
from pathlib import Path
class Tst001(unittest.TestCase):
 def test_trace_inventory(self):
  p=subprocess.run([sys.executable,'-B','scripts/phase9_b4_scoped_trace_check.py'],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stderr)
  self.assertIn('PASS_5_FORMAL_OPEN',p.stdout)
if __name__=='__main__':unittest.main(verbosity=2)
