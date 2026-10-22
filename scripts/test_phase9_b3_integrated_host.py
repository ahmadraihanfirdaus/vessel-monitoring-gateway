#!/usr/bin/env python3
"""Single host fixture crossing all five Batch 3 integration scopes."""
import unittest
from phase9_b3_host_fixture import compile_and_run
class TestBatch3HostIntegration(unittest.TestCase):
 def test_outage_recovery_replay_provenance_and_dedup(self):
  compile_and_run(r"""
#include "phase9_net001_uplink_host_bridge.h"
#include "phase9_net002_replay_cursor_host.h"
#include "phase9_sys002_telemetry_provenance_host.h"
#include "phase9_sys003_outage_cycle_host.h"
#include "phase9_tel003_dedup_host_window.h"
typedef struct{int local,network_begin,sends;net001_host_link link;}ctx_t;
static void local_tick(void *p){((ctx_t *)p)->local++;}
static bool begin(void *p){((ctx_t *)p)->network_begin++;return true;}
static net001_host_link observe(void *p){return ((ctx_t *)p)->link;}
static void cancel(void *p){(void)p;}
static bool send(void *p,const uint8_t *b,size_t n){ctx_t *c=(ctx_t *)p;c->sends++;return n==2u&&b[0]==3u;}
int main(void){ctx_t c={0};c.link=NET001_LINK_PENDING;
net001_host_adapter network={0};net001_host_policy policy={10u,5u,3u};
net001_host_driver driver={&c,begin,observe,cancel};
assert(net001_host_init(&network,policy,driver));
sys003_local_driver local={&c,local_tick,local_tick,local_tick};
net002_host_offline_store offline;net002_host_init(&offline);
const uint8_t bytes[]={3u,9u};assert(net002_host_set_latest(&offline,bytes,2));
assert(net002_host_add_critical(&offline,7u,1u,"test_alarm"));
net001_host_uplink uplink={&c,send};
assert(sys003_host_cycle(local,&network,0).local_ok);
assert(net001_try_send_latest(&network,&offline,uplink)==NET001_SEND_NOT_READY);
assert(sys003_host_cycle(local,&network,10).local_ok); /* timeout */
assert(network.state==NET001_HOST_BACKOFF&&c.local==6);
assert(net001_try_send_latest(&network,&offline,uplink)==NET001_SEND_NOT_READY);
assert(sys003_host_cycle(local,&network,15).local_ok); /* backoff -> idle */
assert(sys003_host_cycle(local,&network,16).local_ok); /* begin */
c.link=NET001_LINK_UP;assert(sys003_host_cycle(local,&network,17).local_ok);
assert(network.state==NET001_HOST_READY&&c.local==15);
assert(net001_try_send_latest(&network,&offline,uplink)==NET001_SEND_SUBMITTED);
assert(c.sends==1&&offline.has_latest);
net002_host_replay_cursor cursor={0};net002_host_critical_event event={0};
assert(net002_replay_begin(&offline,&cursor));
assert(net002_replay_peek(&offline,&cursor,&event)&&event.event_id==7);
assert(net002_replay_ack(&offline,&cursor,7));
vg_telemetry_payload_t p={0};strcpy(p.device_id,"demo");strcpy(p.boot_id,"boot");
strcpy(p.firmware_version,"b3");p.source_mode=VG_SOURCE_SIMULATION;p.channel_count=1;
strcpy(p.channels[0].name,"rpm");p.channels[0].quality=VG_QUALITY_VALID;
p.channels[0].has_value=true;p.channels[0].value=1.0;
assert(sys002_host_safe_payload_label(&p,"simulation"));
tel003_host_window w;tel003_host_init(&w);
assert(tel003_host_admit(&w,&p)==TEL003_HOST_NEW);
assert(tel003_host_admit(&w,&p)==TEL003_HOST_REPLAY);
p.channels[0].value=2.0;
assert(tel003_host_admit(&w,&p)==TEL003_HOST_CONFLICT);
return 0;}
""")
if __name__=='__main__':unittest.main(verbosity=2)
