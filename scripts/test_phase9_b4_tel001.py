import unittest,json
from phase9_b4_testlib import compile_c
class Tel001(unittest.TestCase):
 def test_required_fields_source_and_buffer(self):
  out=compile_c(r"""
#include "phase9_b4_tel001_wire.h"
int main(void){vg_telemetry_payload_t p={0};
strcpy(p.device_id,"demo");strcpy(p.boot_id,"b4");strcpy(p.firmware_version,"1.0");
p.source_mode=VG_SOURCE_SIMULATION;p.channel_count=1;p.sequence=11u;p.uptime_ms=42u;
strcpy(p.channels[0].name,"rpm");p.channels[0].quality=VG_QUALITY_VALID;
p.channels[0].has_value=true;p.channels[0].value=120.0;
char output[1024];assert(phase9_b4_tel001_export(&p,output,sizeof(output)));
puts(output);char tiny[8];assert(!phase9_b4_tel001_export(&p,tiny,sizeof(tiny)));
p.source_mode=VG_SOURCE_PHYSICAL;assert(!phase9_b4_tel001_export(&p,output,sizeof(output)));
return 0;}
""")
  obj=json.loads(out)
  self.assertEqual(set(obj),{'schema_version','device_id','firmware_version','boot_id','sequence','uptime_ms','source_mode','channels'})
  self.assertEqual(obj['source_mode'],'simulation');self.assertEqual(obj['sequence'],11)
if __name__=='__main__':unittest.main(verbosity=2)
