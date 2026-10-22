import unittest
from phase9_b6_testlib import run_c
class Receipt(unittest.TestCase):
 def test_receipt_correlation_and_ack(self):
  run_c(r'''
#include "phase9_b6_receipt_gate.h"
int main(void){net002_host_offline_store s;net002_host_init(&s);
assert(net002_host_add_critical(&s,7u,10u,"alarm"));assert(net002_host_add_critical(&s,8u,11u,"warning"));
net002_host_replay_cursor c={0};assert(net002_replay_begin(&s,&c));
phase9_b6_host_receipt r={true,true,true,7u,101u};
assert(!phase9_b6_replay_accept(&s,&c,r,102u));assert(c.offset==0u);
r.application_ack_eligible=false;assert(!phase9_b6_replay_accept(&s,&c,r,101u));
r.application_ack_eligible=true;r.response_verified=false;assert(!phase9_b6_replay_accept(&s,&c,r,101u));
r.response_verified=true;assert(phase9_b6_replay_accept(&s,&c,r,101u));assert(c.offset==1u);
assert(!phase9_b6_replay_accept(&s,&c,r,101u));r.event_id=8u;r.correlation_id=102u;
assert(phase9_b6_replay_accept(&s,&c,r,102u));assert(c.offset==2u);return 0;}
''')
 def test_mutated_queue_refused(self):
  run_c(r'''
#include "phase9_b6_receipt_gate.h"
int main(void){net002_host_offline_store s;net002_host_init(&s);
assert(net002_host_add_critical(&s,7u,10u,"alarm"));net002_host_replay_cursor c={0};
assert(net002_replay_begin(&s,&c));assert(net002_host_add_critical(&s,8u,11u,"new"));
phase9_b6_host_receipt r={true,true,true,7u,101u};
assert(!phase9_b6_replay_accept(&s,&c,r,101u));assert(c.offset==0u);return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
