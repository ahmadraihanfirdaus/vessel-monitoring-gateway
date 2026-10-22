import unittest
from phase9_b8_testlib import decisions,item,CLAIMS
class Claims(unittest.TestCase):
 def test_reject_invalid_claims_and_time_boundary(self):
  bad=[]
  for field,val in [('tls_verified',False),('device_id','forged'),('scope','actuator:write'),('iat_ms',1500),('exp_ms',1100),('exp_ms',301001)]:
   c=CLAIMS.copy();c[field]=val;bad.append(item(claims=c))
  bad.extend([item(now=999),item(now=2000)])
  r=decisions(bad+[item()]);self.assertEqual([x['ack_eligible'] for x in r],[False]*8+[True])
 def test_reject_payload_duplicate_keys(self):
  from phase9_b8_testlib import valid_raw
  raw=valid_raw().replace('"device_id":"demo"','"device_id":"demo","device_id":"demo"')
  r=decisions([item(raw=raw),item()]);self.assertEqual([x['ack_eligible'] for x in r],[False,True])
if __name__=='__main__':unittest.main(verbosity=2)
