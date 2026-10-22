#!/usr/bin/env python3
import unittest
from phase9_b3_host_fixture import compile_and_run
class TestTel003Dedup(unittest.TestCase):
 def test_new_replay_conflict_full(self):
  compile_and_run(r"""
#include "phase9_tel003_dedup_host_window.h"
static vg_telemetry_payload_t make(uint64_t sequence){vg_telemetry_payload_t p={0};
strcpy(p.device_id,"d");strcpy(p.boot_id,"b");strcpy(p.firmware_version,"v");
p.source_mode=VG_SOURCE_SIMULATION;p.sequence=sequence;p.channel_count=1;
strcpy(p.channels[0].name,"rpm");p.channels[0].quality=VG_QUALITY_VALID;
p.channels[0].has_value=true;p.channels[0].value=1;return p;}
int main(void){tel003_host_window w;tel003_host_init(&w);
vg_telemetry_payload_t a=make(1),b=make(2),c=make(3),d=make(4);
assert(tel003_host_admit(&w,&a)==TEL003_HOST_NEW);
assert(tel003_host_admit(&w,&a)==TEL003_HOST_REPLAY);
a.channels[0].value=2;
assert(tel003_host_admit(&w,&a)==TEL003_HOST_CONFLICT);
assert(tel003_host_admit(&w,&b)==TEL003_HOST_NEW);
assert(tel003_host_admit(&w,&c)==TEL003_HOST_NEW);
assert(tel003_host_admit(&w,&d)==TEL003_HOST_FULL);
assert(w.count==3u);return 0;}
""")
if __name__=='__main__':unittest.main(verbosity=2)
