import unittest
from phase9_b7_testlib import compile_and_run,COMMON
class Receipt(unittest.TestCase):
 def test_ack_requires_all_gates_and_correlation(self):
  compile_and_run(COMMON+r'''
int main(void){(void)sample;(void)eval;(void)alarm;(void)begin;(void)observe;(void)cancel;(void)demo_payload;net002_host_offline_store j;net002_host_init(&j);
assert(net002_host_add_critical(&j,21u,1u,"alarm"));
net002_host_replay_cursor c={0};assert(net002_replay_begin(&j,&c));
phase9_b6_host_receipt r={true,true,true,21u,123u};
assert(!phase9_b7_replay_ack_guard(&j,&c,r,123u,false,true,true));
assert(!phase9_b7_replay_ack_guard(&j,&c,r,123u,true,false,true));
assert(!phase9_b7_replay_ack_guard(&j,&c,r,123u,true,true,false));
assert(!phase9_b7_replay_ack_guard(&j,&c,r,124u,true,true,true));
assert(c.offset==0u);
r.response_verified=false;
assert(!phase9_b7_replay_ack_guard(&j,&c,r,123u,true,true,true));
assert(c.offset==0u);r.response_verified=true;
assert(phase9_b7_replay_ack_guard(&j,&c,r,123u,true,true,true));
assert(c.offset==1u);
assert(!phase9_b7_replay_ack_guard(&j,&c,r,123u,true,true,true));
return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
