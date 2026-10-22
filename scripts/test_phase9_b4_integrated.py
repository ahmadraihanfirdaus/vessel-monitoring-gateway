import json,unittest
from phase9_b4_testlib import compile_c,php_accepts
class Integrated(unittest.TestCase):
 def test_c_producer_to_php_validator_null_and_security_boundary(self):
  out=compile_c(r"""
#include "phase9_b4_tel001_wire.h"
#include "phase9_b4_tel002_quality.h"
#include "phase9_b4_sec002_gate.h"
int main(void){vg_telemetry_payload_t p={0};strcpy(p.device_id,"demo");
strcpy(p.boot_id,"boot-4");strcpy(p.firmware_version,"demo-4");
p.channel_count=2;p.sequence=3u;p.uptime_ms=123u;p.source_mode=VG_SOURCE_SIMULATION;
strcpy(p.channels[0].name,"rpm");p.channels[0].quality=VG_QUALITY_VALID;
p.channels[0].has_value=true;p.channels[0].value=0.0;
strcpy(p.channels[1].name,"temperature");p.channels[1].quality=VG_QUALITY_MISSING;
phase9_b4_transport_claims t={true,true,true,true};
assert(phase9_b4_sec002_host_admit(t,p.source_mode));
assert(phase9_b4_tel002_safe_payload(&p));char json[1024];
assert(phase9_b4_tel001_export(&p,json,sizeof(json)));puts(json);
return 0;}
""")
  self.assertTrue(php_accepts(out))
  v=json.loads(out);v['channels']['temperature']['value']=0
  self.assertFalse(php_accepts(json.dumps(v,separators=(',',':'))))
if __name__=='__main__':unittest.main(verbosity=2)
