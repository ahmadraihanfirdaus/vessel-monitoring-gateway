import unittest
from phase9_b7_testlib import compile_and_run,COMMON
class ReadOnly(unittest.TestCase):
 def test_only_whitelisted_empty_queries(self):
  compile_and_run(COMMON+r'''
int main(void){(void)sample;(void)eval;(void)alarm;(void)begin;(void)observe;(void)cancel;(void)demo_payload;char cmd[]="stop";
assert(phase9_b7_readonly_allow("telemetry.read",NULL,0u));
assert(phase9_b7_readonly_allow("diagnostic.read",NULL,0u));
assert(phase9_b7_readonly_allow("health.read",NULL,0u));
assert(!phase9_b7_readonly_allow("engine.start",NULL,0u));
assert(!phase9_b7_readonly_allow("telemetry.read",cmd,4u));
assert(!phase9_b7_readonly_allow("telemetry.read",cmd,0u));
assert(!phase9_b7_readonly_allow("telemetry.read",NULL,4u));
assert(!phase9_b7_readonly_allow(NULL,NULL,0u));return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
