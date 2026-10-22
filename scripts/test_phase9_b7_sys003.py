import unittest
from phase9_b7_testlib import compile_and_run,COMMON
class Safety(unittest.TestCase):
 def test_always_local_first_even_outage_or_missing_callback(self):
  compile_and_run(COMMON+r'''
int main(void){(void)sample;(void)eval;(void)alarm;(void)begin;(void)observe;(void)cancel;(void)demo_payload;b7_ctx c={0};c.link=NET001_LINK_DOWN;
net001_host_adapter n={0};net001_host_driver d={&c,begin,observe,cancel};
net001_host_policy policy={10u,5u,3u};assert(net001_host_init(&n,policy,d));
sys003_local_driver l={&c,sample,eval,alarm};
sys003_host_cycle_result a=phase9_b7_safety_priority(l,&n,0u);
assert(a.local_ok&&a.network_attempted&&c.samples==1&&c.evals==1&&c.alarms==1);
a=phase9_b7_safety_priority(l,&n,1u);assert(a.local_ok&&c.samples==2);
l.local_alarm=NULL;int begins=c.begins;
a=phase9_b7_safety_priority(l,&n,2u);
assert(!a.local_ok&&!a.network_attempted&&c.begins==begins);
return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
