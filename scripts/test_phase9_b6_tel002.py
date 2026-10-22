import unittest,json
from phase9_b6_testlib import valid_raw,php
class Quality(unittest.TestCase):
 def test_null_zero_stale(self):
  raw=valid_raw(channels={'rpm':{'value':0,'quality':'valid'},'temp':{'value':None,'quality':'missing'},'stale':{'value':None,'quality':'stale'}})
  code="$v=json_decode(stream_get_contents(STDIN),true);echo json_encode(App\\Support\\Phase9B6ChannelAudit::profile($v['channels']));"
  d=json.loads(php(raw,code));self.assertEqual(d['valid_zero'],1);self.assertEqual(d['missing_null'],1);self.assertEqual(d['stale_null'],1)
 def test_reject_false_zero(self):
  code="$v=json_decode(stream_get_contents(STDIN),true);var_export(App\\Support\\Phase9B6ChannelAudit::profile($v['channels'])===null);"
  bad=valid_raw(channels={'rpm':{'value':0,'quality':'missing'}})
  self.assertEqual(php(bad,code),'true')
if __name__=='__main__':unittest.main(verbosity=2)
