import unittest
from phase9_b8_testlib import compile_and_run,decisions,item
class Integrated(unittest.TestCase):
 def test_alarm_blocks_receipt_until_explicit_recovery(self):
  compile_and_run(r'''
#include "phase9_b8_safety_replay.h"
int main(void){phase9_b8_alarm_latch a;phase9_b8_ack_window w;
phase9_b8_alarm_init(&a);phase9_b8_ack_init(&w);
assert(phase9_b8_ack_begin(&w,1u,40u));
phase9_b8_safety_replay_result r=phase9_b8_safety_replay_step(&a,&w,
 true,true,true,false,1u,40u,true,true);
assert(!r.ack_applied&&r.alarm_latched&&w.pending);
for(int k=0;k<2;k++){r=phase9_b8_safety_replay_step(&a,&w,
 true,true,false,false,1u,40u,true,true);assert(!r.ack_applied);}
r=phase9_b8_safety_replay_step(&a,&w,true,true,false,true,1u,40u,false,true);
assert(!r.alarm_latched&&!r.ack_applied&&w.pending);
r=phase9_b8_safety_replay_step(&a,&w,true,true,false,false,1u,40u,true,true);
assert(r.local_safe&&r.ack_applied&&!w.pending&&w.last_accepted_sequence==1u);
assert(!phase9_b8_ack_commit(&w,1u,40u,true,true,true));return 0;}
''')
 def test_synthetic_sec_and_replay_integrate(self):
  r=decisions([item(seq=1),item(seq=1),item(seq=3),item(seq=2),item(seq=2)])
  self.assertEqual([x['ack_eligible'] for x in r],[True,True,False,True,True])
if __name__=='__main__':unittest.main(verbosity=2)
