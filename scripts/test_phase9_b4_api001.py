import copy,json,unittest
from phase9_b4_testlib import php_accepts
base={'schema_version':'1.0','device_id':'demo','firmware_version':'1.0','boot_id':'b4','sequence':1,'uptime_ms':42,'source_mode':'simulation','channels':{'rpm':{'value':0,'quality':'valid'},'temp':{'value':None,'quality':'missing'}}}
def check(d):return php_accepts(json.dumps(d,separators=(',',':')))
class Api001(unittest.TestCase):
 def test_accept_synthetic_only(self):
  self.assertTrue(check(base))
  for key,wrong in [('schema_version','3.0'),('device_id','bad space'),('sequence',-1),('source_mode','physical')]:
   p=copy.deepcopy(base);p[key]=wrong;self.assertFalse(check(p),key)
 def test_null_and_payload_bounds(self):
  p=copy.deepcopy(base);p['channels']['temp']['value']=0
  self.assertFalse(check(p))
  p=copy.deepcopy(base);p['channels']['rpm']['value']=None;self.assertFalse(check(p))
  p=copy.deepcopy(base);p['extra']='x';self.assertFalse(check(p))
  self.assertFalse(php_accepts('x'*4097))
 def test_unsigned_64_boundary(self):
  p=copy.deepcopy(base);p['sequence']=18446744073709551615
  self.assertTrue(check(p));p['sequence']=18446744073709551616;self.assertFalse(check(p))
if __name__=='__main__':unittest.main(verbosity=2)
