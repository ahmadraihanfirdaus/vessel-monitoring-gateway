import unittest
from phase9_b5_testlib import run_c
class Ack(unittest.TestCase):
 def test_verified_order(self):
  run_c(r"""
#include "phase9_b5_replay_ack_guard.h"
int main(void){net002_host_offline_store s;net002_host_init(&s);
assert(net002_host_add_critical(&s,3u,1u,"first"));assert(net002_host_add_critical(&s,4u,2u,"second"));
net002_host_replay_cursor c={0};assert(net002_replay_begin(&s,&c));
phase9_b5_ack_claims p={true,false,3u};assert(!phase9_b5_replay_commit_ack(&s,&c,p));assert(c.offset==0u);
p.response_verified=true;p.acknowledged_event_id=4u;assert(!phase9_b5_replay_commit_ack(&s,&c,p));
p.acknowledged_event_id=3u;assert(phase9_b5_replay_commit_ack(&s,&c,p));assert(c.offset==1u);
assert(!phase9_b5_replay_commit_ack(&s,&c,p));p.acknowledged_event_id=4u;
assert(phase9_b5_replay_commit_ack(&s,&c,p));assert(c.offset==2u);assert(s.count==2u);return 0;}
""")
 def test_mutation_reject(self):
  run_c(r"""
#include "phase9_b5_replay_ack_guard.h"
int main(void){net002_host_offline_store s;net002_host_init(&s);assert(net002_host_add_critical(&s,1u,0u,"a"));
net002_host_replay_cursor c={0};assert(net002_replay_begin(&s,&c));assert(net002_host_add_critical(&s,2u,1u,"b"));
phase9_b5_ack_claims p={true,true,1u};assert(!phase9_b5_replay_commit_ack(&s,&c,p));return 0;}
""")
if __name__=='__main__':unittest.main(verbosity=2)
