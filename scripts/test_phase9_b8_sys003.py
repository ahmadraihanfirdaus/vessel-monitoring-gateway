import unittest
from phase9_b8_testlib import compile_and_run
class Alarm(unittest.TestCase):
 def test_latch_recovery_requires_three_clean_samples_and_ack(self):
  compile_and_run(r'''
#include "phase9_b8_alarm_latch.h"
int main(void){phase9_b8_alarm_latch a;phase9_b8_alarm_init(&a);
assert(!phase9_b8_alarm_observe(&a,false,true,false));assert(a.latched);
for(int k=0;k<2;k++) assert(!phase9_b8_alarm_observe(&a,true,true,false));
assert(!phase9_b8_alarm_clear(&a,true));
assert(!phase9_b8_alarm_observe(&a,true,true,false));
assert(!phase9_b8_alarm_clear(&a,false));
assert(phase9_b8_alarm_clear(&a,true));assert(!a.latched);
assert(phase9_b8_alarm_observe(&a,true,true,false));
assert(!phase9_b8_alarm_observe(&a,true,false,false));assert(a.latched);
return 0;}
''')
 def test_fail_closed_on_missing_state(self):
  compile_and_run(r'''
#include "phase9_b8_alarm_latch.h"
int main(void){assert(!phase9_b8_alarm_observe(0,true,true,false));
assert(!phase9_b8_alarm_clear(0,true));return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
