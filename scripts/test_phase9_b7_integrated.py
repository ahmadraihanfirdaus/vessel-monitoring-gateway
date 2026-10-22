import unittest
from phase9_b7_testlib import compile_and_run,COMMON
class Gateway(unittest.TestCase):
 def test_outage_safety_readonly_provenance_then_ack(self):
  compile_and_run(COMMON+r'''
int main(void){(void)sample;(void)eval;(void)alarm;(void)begin;(void)observe;(void)cancel;(void)demo_payload;b7_ctx ctx={0};ctx.link=NET001_LINK_PENDING;
net001_host_driver drv={&ctx,begin,observe,cancel};
net001_host_policy policy={10u,5u,3u};net001_host_adapter n={0};
assert(net001_host_init(&n,policy,drv));
sys003_local_driver local={&ctx,sample,eval,alarm};
vg_telemetry_payload_t p;demo_payload(&p);
net002_host_offline_store j;net002_host_init(&j);
assert(net002_host_add_critical(&j,21u,1u,"critical"));
net002_host_replay_cursor cur={0};assert(net002_replay_begin(&j,&cur));
phase9_b7_gateway_request q={0};q.local=local;q.network=&n;q.telemetry=&p;
q.declared_source="simulation";q.topic="telemetry.read";q.journal=&j;
q.cursor=&cur;q.correlation_id=300u;q.receipt=(phase9_b6_host_receipt){true,true,true,21u,300u};
q.tick_ms=0u;
phase9_b7_gateway_result r=phase9_b7_gateway_step(&q);
assert(r.safety_ran&&r.network_attempted&&r.source_admitted&&r.readonly_allowed);
assert(!r.replay_advanced&&cur.offset==0u&&ctx.samples==1&&ctx.alarms==1);
q.tick_ms=10u;r=phase9_b7_gateway_step(&q);assert(r.safety_ran);
assert(!r.replay_advanced&&cur.offset==0u&&ctx.alarms==2);
q.tick_ms=15u;r=phase9_b7_gateway_step(&q);assert(!r.replay_advanced);
q.tick_ms=16u;r=phase9_b7_gateway_step(&q);assert(!r.replay_advanced);
ctx.link=NET001_LINK_UP;q.tick_ms=17u;r=phase9_b7_gateway_step(&q);
assert(r.safety_ran&&r.link_state==NET001_HOST_READY);
assert(r.replay_advanced&&cur.offset==1u&&ctx.samples==5&&ctx.alarms==5);
assert(!phase9_b7_gateway_step(&q).replay_advanced);
net002_host_replay_cursor cur2={0};assert(net002_replay_begin(&j,&cur2));
q.cursor=&cur2;q.topic="engine.start";q.tick_ms=18u;
r=phase9_b7_gateway_step(&q);assert(r.safety_ran&&!r.readonly_allowed&&!r.replay_advanced);
q.topic="telemetry.read";q.declared_source="physical";q.tick_ms=19u;
r=phase9_b7_gateway_step(&q);assert(r.safety_ran&&!r.source_admitted&&!r.replay_advanced);
q.declared_source="simulation";q.receipt.response_verified=false;q.tick_ms=20u;
r=phase9_b7_gateway_step(&q);assert(r.safety_ran&&!r.replay_advanced);
q.receipt.response_verified=true;q.local.local_alarm=NULL;q.tick_ms=21u;
int begins=ctx.begins;r=phase9_b7_gateway_step(&q);
assert(!r.safety_ran&&!r.network_attempted&&!r.replay_advanced&&ctx.begins==begins);
assert(cur2.offset==0u);return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
