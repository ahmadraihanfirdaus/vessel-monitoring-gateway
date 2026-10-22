#!/usr/bin/env python3
import unittest
from phase9_b3_host_fixture import compile_and_run
class TestSys002Provenance(unittest.TestCase):
 def test_source_mode_validation(self):
  compile_and_run(r"""
#include "phase9_sys002_telemetry_provenance_host.h"
int main(void){vg_telemetry_payload_t p={0};
strcpy(p.device_id,"demo");strcpy(p.boot_id,"boot");
strcpy(p.firmware_version,"host");p.source_mode=VG_SOURCE_SIMULATION;
p.channel_count=1;strcpy(p.channels[0].name,"rpm");
p.channels[0].quality=VG_QUALITY_VALID;p.channels[0].has_value=true;p.channels[0].value=12.0;
assert(sys002_host_safe_payload_label(&p,"simulation"));
assert(!sys002_host_safe_payload_label(&p,"bench_test"));
assert(!sys002_host_safe_payload_label(&p,"physical"));
p.source_mode=VG_SOURCE_PHYSICAL;
assert(!sys002_host_safe_payload_label(&p,"physical"));
p.source_mode=VG_SOURCE_BENCH_TEST;
assert(sys002_host_safe_payload_label(&p,"bench_test"));
p.channels[0].has_value=false;assert(!sys002_host_safe_payload_label(&p,"bench_test"));
return 0;}
""")
if __name__=='__main__':unittest.main(verbosity=2)
