#!/usr/bin/env python3
import unittest
from phase9_b3_host_fixture import compile_and_run
class TestNet002Replay(unittest.TestCase):
 def test_ack_order_and_wrong_ack(self):
  compile_and_run(r"""
#include "phase9_net002_replay_cursor_host.h"
int main(void){net002_host_offline_store s;net002_host_init(&s);
assert(net002_host_add_critical(&s,4,1,"a"));
assert(net002_host_add_critical(&s,5,2,"b"));
net002_host_replay_cursor c={0};net002_host_critical_event e={0};
assert(net002_replay_begin(&s,&c));assert(net002_replay_peek(&s,&c,&e)&&e.event_id==4);
assert(!net002_replay_ack(&s,&c,5));assert(c.offset==0u);
assert(net002_replay_ack(&s,&c,4));assert(net002_replay_peek(&s,&c,&e)&&e.event_id==5);
assert(net002_replay_ack(&s,&c,5));assert(!net002_replay_peek(&s,&c,&e));
assert(s.count==2u);return 0;}
""")
 def test_mutation_fail_closed(self):
  compile_and_run(r"""
#include "phase9_net002_replay_cursor_host.h"
int main(void){net002_host_offline_store s;net002_host_init(&s);
assert(net002_host_add_critical(&s,1,1,"a"));net002_host_replay_cursor c={0};
assert(net002_replay_begin(&s,&c));assert(net002_host_add_critical(&s,2,2,"b"));
net002_host_critical_event e={0};assert(!net002_replay_peek(&s,&c,&e));
return 0;}
""")
if __name__=='__main__':unittest.main(verbosity=2)
