import unittest,json
from phase9_b6_testlib import run_c
class Wire(unittest.TestCase):
 def test_wire_schema_and_source(self):
  raw=run_c(r'''
#include <stdio.h>
#include <string.h>
#include "phase9_b6_wire_gate.h"
int main(void){vg_telemetry_payload_t p={0};
strcpy(p.device_id,"demo");strcpy(p.boot_id,"synthetic");strcpy(p.firmware_version,"host");
p.sequence=4u;p.uptime_ms=0u;p.source_mode=VG_SOURCE_SIMULATION;p.channel_count=2u;
strcpy(p.channels[0].name,"rpm");p.channels[0].quality=VG_QUALITY_VALID;p.channels[0].has_value=true;p.channels[0].value=0.0;
strcpy(p.channels[1].name,"temp");p.channels[1].quality=VG_QUALITY_MISSING;p.channels[1].has_value=false;
char output[4096];assert(phase9_b6_wire_export(&p,output,sizeof(output)));puts(output);
p.source_mode=VG_SOURCE_PHYSICAL;assert(!phase9_b6_wire_export(&p,output,sizeof(output)));assert(output[0]=='\0');
assert(!phase9_b6_wire_export(&p,output,0u));return 0;}
''')
  d=json.loads(raw);self.assertEqual(d['channels']['rpm']['value'],0);self.assertIsNone(d['channels']['temp']['value'])
  self.assertEqual(d['source_mode'],'simulation')
if __name__=='__main__':unittest.main(verbosity=2)
