import unittest
from phase9_b7_testlib import compile_and_run,COMMON
class Source(unittest.TestCase):
 def test_refuse_physical_and_mismatched_labels(self):
  compile_and_run(COMMON+r'''
int main(void){(void)sample;(void)eval;(void)alarm;(void)begin;(void)observe;(void)cancel;(void)demo_payload;vg_telemetry_payload_t p;demo_payload(&p);
assert(phase9_b7_source_admit(&p,"simulation"));
assert(!phase9_b7_source_admit(&p,"bench_test"));
assert(!phase9_b7_source_admit(&p,"physical"));
p.source_mode=VG_SOURCE_BENCH_TEST;
assert(phase9_b7_source_admit(&p,"bench_test"));
p.source_mode=VG_SOURCE_PHYSICAL;
assert(!phase9_b7_source_admit(&p,"physical"));
p.source_mode=VG_SOURCE_SIMULATION;p.device_id[0]='\0';
assert(!phase9_b7_source_admit(&p,"simulation"));
assert(!phase9_b7_source_admit(NULL,"simulation"));return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
