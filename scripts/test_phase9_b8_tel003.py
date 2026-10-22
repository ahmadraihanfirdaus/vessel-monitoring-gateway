import unittest
from phase9_b8_testlib import decisions,item
class Ordered(unittest.TestCase):
 def test_monotonic_duplicate_gap_and_conflict(self):
  x=decisions([item(seq=11),item(seq=11),item(seq=13),item(seq=12),item(seq=11),item(seq=12)])
  self.assertEqual([r['window'] for r in x],['FIRST','REPEAT','GAP','NEXT','STALE','REPEAT'])
  self.assertEqual([r['ack_eligible'] for r in x],[True,True,False,True,False,True])
 def test_repeated_identity_modified_body_is_rejected(self):
  from phase9_b8_testlib import valid_raw
  x=decisions([item(seq=1),item(seq=1,raw=valid_raw(sequence=1,uptime_ms=7))])
  self.assertEqual([r['decision'] for r in x],['ACCEPT_FIRST','CONFLICT'])
  self.assertEqual([r['ack_eligible'] for r in x],[True,False])
if __name__=='__main__':unittest.main(verbosity=2)
