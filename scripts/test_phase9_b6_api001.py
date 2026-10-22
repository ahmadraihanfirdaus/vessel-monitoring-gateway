import unittest
from phase9_b6_testlib import ingest,item,CLAIMS,valid_raw
class Decision(unittest.TestCase):
 def test_ingress_duplicate_conflict(self):
  r=ingest([item(),item(),item(valid_raw(uptime_ms=99)),item(valid_raw(sequence=2))])
  self.assertEqual([x['decision'] for x in r],['ACCEPT_FIRST','DUPLICATE_SAME','CONFLICT','ACCEPT_FIRST'])
  self.assertEqual([x['ack_eligible'] for x in r],[True,True,False,True])
 def test_forged_claim_or_duplicate_key_blocked(self):
  invalid=valid_raw().replace('"device_id":"demo"','"device_id":"demo","device_id":"demo"')
  c={**CLAIMS,'tls_verified':False}
  r=ingest([item(invalid),item(claims=c),item()])
  self.assertEqual([x['decision'] for x in r],['BLOCK','BLOCK','ACCEPT_FIRST'])
  self.assertEqual([x['ack_eligible'] for x in r],[False,False,True])
if __name__=='__main__':unittest.main(verbosity=2)
