import json,unittest
from phase9_b5_testlib import php_eval,valid_raw,run_c
CODE="""$data=json_decode(stream_get_contents(STDIN),true);$ledger=new App\\Support\\Phase9B5DedupLedger(2);foreach($data as $entry){if(!App\\Support\\Phase9B5AuthClaims::allowSynthetic($entry['claims'],$entry['raw'])){echo 'BLOCK|';continue;}echo $ledger->ingest($entry['raw']).'|';}"""
CLAIM={'tls_verified':True,'external_secret':True,'device_authenticated':True,'device_id':'demo'}
class Integrated(unittest.TestCase):
 def test_security_strict_dedup_flow(self):
  a=valid_raw();bad=a.replace('"device_id":"demo"','"device_id":"demo","device_id":"demo"')
  c=CLAIM.copy();c['tls_verified']=False
  data=[{'claims':CLAIM,'raw':a},{'claims':CLAIM,'raw':a},{'claims':CLAIM,'raw':bad},{'claims':CLAIM,'raw':valid_raw(sequence=1,uptime_ms=10)},{'claims':c,'raw':valid_raw(sequence=2)},{'claims':CLAIM,'raw':valid_raw(sequence=2)}]
  self.assertEqual(php_eval(json.dumps(data),CODE),'ACCEPT_FIRST|DUPLICATE_SAME|BLOCK|CONFLICT|BLOCK|ACCEPT_FIRST|')
 def test_replay_ack_then_host_ingest(self):
  raw=run_c(r"""
#include <stdio.h>
#include "phase9_b5_replay_ack_guard.h"
int main(void){net002_host_offline_store s;net002_host_init(&s);assert(net002_host_add_critical(&s,17u,1u,"x"));
net002_host_replay_cursor c={0};assert(net002_replay_begin(&s,&c));
phase9_b5_ack_claims p={true,true,17u};assert(phase9_b5_replay_commit_ack(&s,&c,p));
printf("%u\n",(unsigned)c.offset);return 0;}
""")
  self.assertEqual(raw.strip(),'1')
  self.assertEqual(php_eval(json.dumps([{'claims':CLAIM,'raw':valid_raw()}]),CODE),'ACCEPT_FIRST|')
if __name__=='__main__':unittest.main(verbosity=2)
