#!/usr/bin/env python3
import unittest
from phase9_b3_host_fixture import compile_and_run
class TestNet001Uplink(unittest.TestCase):
 def test_no_send_until_ready_and_preserve_snapshot(self):
  compile_and_run(r"""
#include "phase9_net001_uplink_host_bridge.h"
typedef struct {int sent;} fixture;
static bool send(void *p,const uint8_t *b,size_t n){fixture *f=(fixture *)p;f->sent++;return n==3u&&b[2]==3u;}
int main(void){net002_host_offline_store s;net002_host_init(&s);
uint8_t b[3]={1,2,3};assert(net002_host_set_latest(&s,b,3));
net001_host_adapter net={0};net.initialized=true;net.state=NET001_HOST_BACKOFF;
fixture f={0};net001_host_uplink tx={&f,send};
assert(net001_try_send_latest(&net,&s,tx)==NET001_SEND_NOT_READY);
assert(f.sent==0);net.state=NET001_HOST_READY;
assert(net001_try_send_latest(&net,&s,tx)==NET001_SEND_SUBMITTED);
assert(s.has_latest&&s.latest_len==3u&&f.sent==1);
assert(net001_try_send_latest(NULL,&s,tx)==NET001_SEND_INVALID);
return 0;}
""")
 def test_rejected_driver_retains_state(self):
  compile_and_run(r"""
#include "phase9_net001_uplink_host_bridge.h"
static bool decline(void *p,const uint8_t *b,size_t n){(void)p;(void)b;(void)n;return false;}
int main(void){net002_host_offline_store s;net002_host_init(&s);
assert(net002_host_set_latest(&s,"x",1));net001_host_adapter a={0};
a.initialized=true;a.state=NET001_HOST_READY;
assert(net001_try_send_latest(&a,&s,(net001_host_uplink){0,decline})==NET001_SEND_REJECTED);
assert(s.has_latest&&s.latest_len==1u);return 0;}
""")
if __name__=='__main__':unittest.main(verbosity=2)
