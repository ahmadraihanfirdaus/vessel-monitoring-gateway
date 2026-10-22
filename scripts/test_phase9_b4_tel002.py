import unittest,json
from phase9_b4_testlib import compile_c
class Tel002(unittest.TestCase):
 def test_null_quality_and_explicit_zero(self):
  out=compile_c(r"""
#include "phase9_b4_tel002_quality.h"
#include "phase9_b4_tel001_wire.h"
int main(void){vg_telemetry_payload_t p={0};strcpy(p.device_id,"demo");
strcpy(p.boot_id,"b4");strcpy(p.firmware_version,"1.0");p.source_mode=VG_SOURCE_SIMULATION;
p.channel_count=3;strcpy(p.channels[0].name,"rpm");p.channels[0].quality=VG_QUALITY_VALID;
p.channels[0].has_value=true;p.channels[0].value=0.0;
strcpy(p.channels[1].name,"temperature");p.channels[1].quality=VG_QUALITY_MISSING;
strcpy(p.channels[2].name,"voltage");p.channels[2].quality=VG_QUALITY_INVALID;
assert(phase9_b4_tel002_safe_payload(&p));char out[1024];
assert(phase9_b4_tel001_export(&p,out,sizeof(out)));puts(out);
p.channels[1].has_value=true;p.channels[1].value=0.0;
assert(!phase9_b4_tel002_safe_payload(&p));return 0;}
""")
  ch=json.loads(out)['channels']
  self.assertEqual(ch['rpm'],{'value':0,'quality':'valid'})
  self.assertEqual(ch['temperature'],{'value':None,'quality':'missing'})
  self.assertEqual(ch['voltage'],{'value':None,'quality':'invalid'})
if __name__=='__main__':unittest.main(verbosity=2)
