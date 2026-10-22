import json,unittest
from phase9_b5_testlib import valid_raw,php_eval
RUN="""$ledger=new App\\Support\\Phase9B5DedupLedger(2); $data=json_decode(stream_get_contents(STDIN),true); foreach($data as $raw) echo $ledger->ingest($raw).'|';"""
class Dedup(unittest.TestCase):
 def test_duplicate_conflict_and_capacity(self):
  one=valid_raw();spaced=json.dumps(json.loads(one),indent=1)
  conflict=valid_raw(uptime_ms=1);other=valid_raw(sequence=2);third=valid_raw(sequence=3)
  self.assertEqual(php_eval(json.dumps([one,spaced,conflict,other,third]),RUN),'ACCEPT_FIRST|DUPLICATE_SAME|CONFLICT|ACCEPT_FIRST|CAPACITY|')
 def test_identity_boot_boundary(self):
  self.assertEqual(php_eval(json.dumps([valid_raw(),valid_raw(boot_id='next')]),RUN),'ACCEPT_FIRST|ACCEPT_FIRST|')
if __name__=='__main__':unittest.main(verbosity=2)
