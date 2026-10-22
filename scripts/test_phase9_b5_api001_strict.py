import json,unittest
from phase9_b5_testlib import valid_raw,php_eval
STRICT="echo App\\Support\\Phase9B5StrictPayload::acceptsSynthetic(stream_get_contents(STDIN))?'YES':'NO';"
class StrictApi(unittest.TestCase):
 def test_normal(self):self.assertEqual(php_eval(valid_raw(),STRICT),'YES')
 def test_duplicate_nested(self):
  s=valid_raw().replace('"quality":"valid"','"quality":"valid","quality":"valid"',1)
  self.assertEqual(php_eval(s,STRICT),'NO')
 def test_escaped_duplicate(self):
  s=valid_raw().replace('"device_id":"demo"','"device_id":"demo","\\u0064evice_id":"demo"')
  self.assertEqual(php_eval(s,STRICT),'NO')
 def test_bad_structure(self):
  for s in [valid_raw()[:-1],valid_raw()+' 0',valid_raw().replace('"schema_version"','"schema_version" : '),'{"x":1,"x":2}',valid_raw().replace('"sequence":1','"sequence":-1')]:
   self.assertEqual(php_eval(s,STRICT),'NO',s[:50])
if __name__=='__main__':unittest.main(verbosity=2)
