import json,unittest
from phase9_b6_testlib import ingest,item,run_c,valid_raw,CLAIMS
class EndToEnd(unittest.TestCase):
 def test_c99_wire_to_php_decision(self):
  raw=run_c(r'''
#include <stdio.h>
#include <string.h>
#include "phase9_b6_wire_gate.h"
int main(void){vg_telemetry_payload_t p={0};strcpy(p.device_id,"demo");
strcpy(p.boot_id,"synthetic");strcpy(p.firmware_version,"host");p.source_mode=VG_SOURCE_SIMULATION;
p.sequence=9u;p.uptime_ms=0u;p.channel_count=2u;
strcpy(p.channels[0].name,"rpm");p.channels[0].has_value=true;p.channels[0].quality=VG_QUALITY_VALID;p.channels[0].value=0.;
strcpy(p.channels[1].name,"temp");p.channels[1].quality=VG_QUALITY_MISSING;
char b[4096];assert(phase9_b6_wire_export(&p,b,sizeof(b)));puts(b);return 0;}
''').strip()
  results=ingest([item(raw),item(raw),item(raw.replace('"sequence":9','"sequence":9,"sequence":9'))])
  self.assertEqual([x['decision'] for x in results],['ACCEPT_FIRST','DUPLICATE_SAME','BLOCK'])
  self.assertTrue(results[0]['ack_eligible']);self.assertEqual(results[0]['quality']['valid_zero'],1)
  self.assertEqual(results[0]['quality']['missing_null'],1)
 def test_denied_claim_not_receipt(self):
  c={**CLAIMS,'device_authenticated':False}
  status=ingest([item(claims=c),item()]);self.assertEqual(status[0]['decision'],'BLOCK')
  self.assertFalse(status[0]['ack_eligible']);self.assertTrue(status[1]['ack_eligible'])
  # Synthetic receipt only: C guard consumes caller-supplied verified data.
  run_c(r'''
#include "phase9_b6_receipt_gate.h"
int main(void){net002_host_offline_store s;net002_host_init(&s);
assert(net002_host_add_critical(&s,9u,10u,"outage"));net002_host_replay_cursor c={0};
assert(net002_replay_begin(&s,&c));phase9_b6_host_receipt r={true,true,false,9u,77u};
assert(!phase9_b6_replay_accept(&s,&c,r,77u));assert(c.offset==0u);
r.application_ack_eligible=true;assert(phase9_b6_replay_accept(&s,&c,r,77u));return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
