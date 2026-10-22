import unittest
from phase9_b4_testlib import compile_c
class Sec002(unittest.TestCase):
 def test_fail_closed_transport_claims(self):
  compile_c(r"""
#include "phase9_b4_sec002_gate.h"
int main(void){phase9_b4_transport_claims c={true,true,true,true};
assert(phase9_b4_sec002_host_admit(c,VG_SOURCE_SIMULATION));
assert(phase9_b4_sec002_host_admit(c,VG_SOURCE_BENCH_TEST));
assert(!phase9_b4_sec002_host_admit(c,VG_SOURCE_PHYSICAL));
c.tls_peer_verified=false;assert(!phase9_b4_sec002_host_admit(c,VG_SOURCE_SIMULATION));
c.tls_peer_verified=true;c.device_auth_context_present=false;
assert(!phase9_b4_sec002_host_admit(c,VG_SOURCE_SIMULATION));
c.device_auth_context_present=true;c.credentials_outside_source=false;
assert(!phase9_b4_sec002_host_admit(c,VG_SOURCE_SIMULATION));return 0;}
""")
if __name__=='__main__':unittest.main(verbosity=2)
