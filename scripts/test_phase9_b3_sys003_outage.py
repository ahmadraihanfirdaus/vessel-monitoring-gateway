#!/usr/bin/env python3
import unittest
from phase9_b3_host_fixture import compile_and_run
class TestSys003Outage(unittest.TestCase):
 def test_local_always_first_even_if_network_null(self):
  compile_and_run(r"""
#include "phase9_sys003_outage_cycle_host.h"
typedef struct{int sample,eval,alarm,begin;}ctx_t;
static void sample(void *c){((ctx_t *)c)->sample++;}
static void evaluate(void *c){((ctx_t *)c)->eval++;}
static void alarm(void *c){((ctx_t *)c)->alarm++;}
static bool begin(void *c){ctx_t *x=(ctx_t *)c;assert(x->sample==2&&x->alarm==2);x->begin++;return false;}
static net001_host_link observe(void *c){(void)c;return NET001_LINK_DOWN;}
static void cancel(void *c){(void)c;}
int main(void){ctx_t x={0};sys003_local_driver local={&x,sample,evaluate,alarm};
sys003_host_cycle_result a=sys003_host_cycle(local,0,0);
assert(a.local_ok&&!a.network_attempted&&x.sample==1);
net001_host_adapter net={0};net001_host_policy policy={10u,5u,2u};
net001_host_driver driver={&x,begin,observe,cancel};
assert(net001_host_init(&net,policy,driver));
sys003_host_cycle_result b=sys003_host_cycle(local,&net,1);
assert(b.local_ok&&b.network_attempted&&x.sample==2&&x.alarm==2);
return 0;}
""")
if __name__=='__main__':unittest.main(verbosity=2)
