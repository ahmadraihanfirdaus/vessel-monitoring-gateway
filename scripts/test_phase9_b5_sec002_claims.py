import json,unittest
from phase9_b5_testlib import php_eval,valid_raw
BODY="""$v=json_decode(stream_get_contents(STDIN),true);echo App\\Support\\Phase9B5AuthClaims::allowSynthetic($v['claims'],$v['raw'])?'YES':'NO';"""
C={'tls_verified':True,'external_secret':True,'device_authenticated':True,'device_id':'demo'}
def check(claims,raw=None):return php_eval(json.dumps({'claims':claims,'raw':raw or valid_raw()}),BODY)
class Sec(unittest.TestCase):
 def test_claims(self):
  self.assertEqual(check(C),'YES')
  for k in ('tls_verified','external_secret','device_authenticated'):
   c=C.copy();c[k]=False;self.assertEqual(check(c),'NO',k)
  c=C.copy();c['device_id']='wrong';self.assertEqual(check(c),'NO')
 def test_payload_duplicate_still_rejected(self):
  self.assertEqual(check(C,valid_raw().replace('"boot_id":"synthetic"','"boot_id":"synthetic","boot_id":"synthetic"')),'NO')
if __name__=='__main__':unittest.main(verbosity=2)
