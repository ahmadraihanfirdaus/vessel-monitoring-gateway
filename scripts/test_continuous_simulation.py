"""Real strict C99 deterministic oracles; not hardware/timing/formal evidence."""
import hashlib
import json
from pathlib import Path
import unittest
from phase9_b4_testlib import compile_c
from continuous_simulation_wire_bridge import build_bytes
from runtime_uplink_wire_bridge import build_bytes as legacy_bytes

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (ROOT/'scripts/continuous_simulation_fixture.c').read_text(encoding='utf-8')
SETUP = FIXTURE[:FIXTURE.index('int main(void)')]
SETUP += '\nint main(void) { static vg_continuous_simulation_t r; vg_continuous_config_t c=test_config();\n'


class ContinuousSimulationTest(unittest.TestCase):
    def c(self, code):
        return compile_c(SETUP+code+'\nreturn 0;}\n', extra_flags=('-Os',))

    def test_actual_24_frames_all_domains_and_checkpoint_recovery(self):
        packets = [json.loads(line) for line in build_bytes().splitlines()]
        first = packets[0]['channels']
        self.assertEqual(len(first), 48)
        self.assertEqual(first['engine_4_runtime_s']['value'], 3780)
        self.assertEqual(first['nav_latitude_deg'], {'value': 0, 'quality': 'valid'})
        self.assertEqual(first['hatch_state']['value'], 1)
        self.assertEqual(first['compartment_temperature_c']['value'], 25)
        self.assertEqual(first['power_voltage_v']['value'], 5)
        self.assertEqual(packets[1]['channels']['hatch_state']['value'], 2)
        self.assertEqual(packets[2]['channels']['hatch_state'], {'value': None, 'quality': 'missing'})
        self.assertEqual(packets[3]['channels']['engine_3_rpm']['value'], 1500)
        self.assertEqual(packets[2]['channels']['nav_latitude_deg']['quality'], 'stale')
        self.assertEqual(packets[4]['channels']['nav_latitude_deg'], {'value': None, 'quality': 'missing'})
        self.assertEqual(packets[8]['channels']['nav_latitude_deg'], {'value': 0, 'quality': 'valid'})
        self.assertEqual(packets[-1]['channels']['runtime_journal_retained']['value'], 8)
        self.assertGreater(packets[-1]['channels']['runtime_journal_rejected']['value'], 0)

    def test_legacy_wire_is_byte_identical(self):
        self.assertEqual(hashlib.sha256(legacy_bytes()).hexdigest(), '21930ab910d66844d7903d2e726c3c5a8db9809018deacb0e26d93d61f88ee4a')

    def test_config_rejects_missing_thresholds_physical_monitor_block_and_unterminated_identity(self):
        self.c(r'''
assert(vg_continuous_config_valid(&c));
vg_continuous_config_t bad=c;bad.interval_ms=0;assert(!vg_continuous_config_valid(&bad));
bad=c;bad.navigation_age.offline_after_ms=400;assert(!vg_continuous_config_valid(&bad));
bad=c;bad.monitoring.bilge_rule_mode=VG_POLICY_RULE_BLOCK;assert(!vg_continuous_config_valid(&bad));
bad=c;bad.monitoring.temperature_rule_mode=VG_POLICY_RULE_BLOCK;assert(!vg_continuous_config_valid(&bad));
bad=c;bad.monitoring.temperature_thresholds.warning_high_c=NAN;assert(!vg_continuous_config_valid(&bad));
bad=c;bad.monitoring.temperature_thresholds.warning_high_c=60;assert(!vg_continuous_config_valid(&bad));
bad=c;bad.engine_deviation.warning_threshold_rpm=0;assert(!vg_continuous_config_valid(&bad));
bad=c;bad.demo_priority=0;assert(!vg_continuous_config_valid(&bad));
bad=c;memset(bad.device,'x',sizeof(bad.device));assert(!vg_continuous_config_valid(&bad));
bad=c;strcpy(bad.boot,"bad/boot");assert(!vg_continuous_config_valid(&bad));
memset(&r,0xA5,sizeof(r));static vg_continuous_simulation_t before;before=r;
assert(!vg_continuous_init(&r,&bad,0));assert(!memcmp(&r,&before,sizeof(r)));
''')

    def test_wait_regression_skipped_periods_and_sequence_exhaustion(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));assert(vg_continuous_poll(&r,199)==VG_CONTINUOUS_WAIT);
assert(r.sequence==0);assert(vg_continuous_poll(&r,200)==VG_CONTINUOUS_ENCODED);
static vg_continuous_simulation_t before;before=r;
assert(vg_continuous_poll(&r,199)==VG_CONTINUOUS_REJECTED);assert(!memcmp(&r,&before,sizeof(r)));
assert(vg_continuous_poll(&r,1000)==VG_CONTINUOUS_ENCODED);assert(r.skipped==3&&r.sequence==2);
r.sequence=UINT64_MAX;before=r;assert(vg_continuous_poll(&r,1200)==VG_CONTINUOUS_EXHAUSTED);
assert(!memcmp(&r,&before,sizeof(r)));
assert(vg_continuous_init(&r,&c,UINT64_MAX));assert(vg_continuous_poll(&r,UINT64_MAX)==VG_CONTINUOUS_ENCODED);
assert(vg_continuous_poll(&r,UINT64_MAX)==VG_CONTINUOUS_EXHAUSTED);
''')

    def test_full_journal_does_not_freeze_local_sampling_or_replace_old_events(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));
for(unsigned i=1;i<=8;i++)assert(vg_continuous_poll(&r,i*200)==VG_CONTINUOUS_ENCODED);
assert(r.journal.count==8);vg_journal_event_t retained[8];memcpy(retained,r.journal.events,sizeof(retained));
for(unsigned i=9;i<=2000;i++)assert(vg_continuous_poll(&r,i*200)==VG_CONTINUOUS_ENCODED);
assert(r.sequence==2000&&r.latest_sequence==2000&&r.journal.rejected_full>0);
assert(!memcmp(retained,r.journal.events,sizeof(retained))&&r.alarm_errors==0);
assert(r.logical_alarm_active);assert(!vg_continuous_acknowledge(&r,0,400000));
r.journal.rejected_full=UINT64_MAX;assert(vg_continuous_poll(&r,400200)==VG_CONTINUOUS_ENCODED);
assert(r.journal.rejected_full==UINT64_MAX);
''')

    def test_ack_remains_active_monotonic_and_new_reason_realerts(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));assert(vg_continuous_poll(&r,200)==VG_CONTINUOUS_ENCODED);
assert(vg_continuous_poll(&r,400)==VG_CONTINUOUS_ENCODED);assert(r.alarms[0].condition_active);
uint64_t alarm=r.alarms[0].id;assert(vg_continuous_acknowledge(&r,0,450));
assert(r.alarms[0].state==VG_ALARM_STATE_ACTIVE_ACK&&r.logical_alarm_active);
assert(!vg_continuous_acknowledge(&r,0,450));assert(vg_continuous_poll(&r,449)==VG_CONTINUOUS_REJECTED);
assert(vg_continuous_poll(&r,600)==VG_CONTINUOUS_ENCODED);
assert(r.alarms[0].id!=alarm&&r.alarms[0].state==VG_ALARM_STATE_ACTIVE_UNACK);
assert(!r.virtual_start_permitted);
''')

    def test_engine_lost_null_stopped_zero_and_uint64_not_rounded(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));assert(vg_continuous_poll(&r,200)==VG_CONTINUOUS_ENCODED);
vg_engine_snapshot_t *e=&r.sample.engines.engines[0];e->state=VG_ENGINE_STATE_STOPPED;e->rpm=0;
assert(vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
assert(r.working_payload.channels[1].quality==VG_QUALITY_VALID&&r.working_payload.channels[1].value==0);
e->runtime_s=VG_EXACT_DOUBLE_UINT64_MAX;
assert(vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));assert(r.working_payload.channels[3].has_value);
e->runtime_s=VG_EXACT_DOUBLE_UINT64_MAX+1;
assert(vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
assert(r.working_payload.channels[3].quality==VG_QUALITY_INVALID&&!r.working_payload.channels[3].has_value);
e->state=VG_ENGINE_STATE_UNKNOWN;e->communication_quality=VG_ENGINE_COMM_LOST;
assert(vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
for(size_t i=0;i<5;i++)assert(!r.working_payload.channels[i].has_value&&r.working_payload.channels[i].quality==VG_QUALITY_MISSING);
assert(r.working_payload.channels[5].has_value&&r.working_payload.channels[5].value==VG_ENGINE_COMM_LOST);
''')

    def test_domain_rejects_foreign_source_invalid_values_and_future_metadata(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));assert(vg_continuous_poll(&r,200)==VG_CONTINUOUS_ENCODED);
r.sample.power.meta.source_mode=VG_SOURCE_PHYSICAL;
assert(!vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
r.sample.power.meta.source_mode=VG_SOURCE_SIMULATION;r.sample.power.meta.sampled_at_ms=201;
assert(!vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
r.sample.power.meta.sampled_at_ms=200;r.sample.power.voltage_v=NAN;
assert(!vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
''')

    def test_navigation_no_fix_unknown_checksum_age_boundaries(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));assert(vg_continuous_poll(&r,200)==VG_CONTINUOUS_ENCODED);
vg_navigation_state_t old=r.sample.navigation;
assert(!vg_nav_ingest_sentence(&r.sample.navigation,"$GPRMC,invalid*00",300,VG_SOURCE_SIMULATION));
assert(!memcmp(&old,&r.sample.navigation,sizeof(old)));
r.sample.navigation.fix_valid=false;
assert(vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
assert(r.working_payload.channels[24].quality==VG_QUALITY_INVALID&&!r.working_payload.channels[24].has_value);
r.sample.navigation.initialized=false;
assert(vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
assert(r.working_payload.channels[24].quality==VG_QUALITY_UNKNOWN&&!r.working_payload.channels[24].has_value);
r.sample.navigation=old;assert(vg_nav_update_age(&r.sample.navigation,599,&c.navigation_age));assert(r.sample.navigation.quality==VG_QUALITY_VALID);
assert(vg_nav_update_age(&r.sample.navigation,600,&c.navigation_age));assert(r.sample.navigation.quality==VG_QUALITY_STALE);
assert(vg_nav_update_age(&r.sample.navigation,1000,&c.navigation_age));assert(r.sample.navigation.quality==VG_QUALITY_MISSING);
''')

    def test_v11_72_channels_and_4096_bytes_limits_are_independent(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));assert(vg_continuous_poll(&r,200)==VG_CONTINUOUS_ENCODED);
vg_telemetry_snapshot_v11_t *p=&r.working_payload;p->channel_count=0;
for(unsigned i=0;i<72;i++){char name[33];snprintf(name,sizeof(name),"c%u",i);assert(vg_domain_add(p,name,VG_QUALITY_VALID,true,0));}
assert(vg_tel_v11_serialize_json(p,r.working_wire,sizeof(r.working_wire)));
assert(!vg_domain_add(p,"extra",VG_QUALITY_VALID,true,0));
assert(!vg_tel_serialize_vector_json("1.0",p->device_id,p->firmware_version,p->boot_id,0,0,p->source_mode,p->channels,72,r.working_wire,sizeof(r.working_wire)));
assert(!vg_tel_serialize_vector_json("1.2",p->device_id,p->firmware_version,p->boot_id,0,0,p->source_mode,p->channels,1,r.working_wire,sizeof(r.working_wire)));
for(unsigned i=0;i<72;i++){snprintf(p->channels[i].name,33,"long_channel_with_unique_idx_%02u",i);}
static char large[12000];assert(!vg_tel_v11_serialize_json(p,large,sizeof(large)));
memset(p->channels[71].name,'x',33);assert(!vg_tel_v11_is_consistent(p));
''')

    def test_eight_engines_map_68_fields_without_silent_truncation(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));assert(vg_continuous_poll(&r,200)==VG_CONTINUOUS_ENCODED);
r.sample.engines.engine_count=8;
for(unsigned i=4;i<8;i++){r.sample.engines.engines[i]=r.sample.engines.engines[0];r.sample.engines.engines[i].engine_id=(uint8_t)i+1;}
assert(vg_domain_build(&r.sample,c.device,"test",c.boot,1,200,&r.working_payload));
assert(r.working_payload.channel_count==68);
/* Long all-domain wire may exceed body cap: rejection, never a shortened body. */
bool fits=vg_tel_v11_serialize_json(&r.working_payload,r.working_wire,sizeof(r.working_wire));
assert(fits&&strlen(r.working_wire)<=4096);
''')

    def test_alarm_id_exhaustion_is_explicit_and_does_not_silence_condition(self):
        self.c(r'''
assert(vg_continuous_init(&r,&c,200));assert(vg_continuous_poll(&r,200)==VG_CONTINUOUS_ENCODED);
r.alarm_ids.next_id=UINT64_MAX;
assert(vg_continuous_poll(&r,400)==VG_CONTINUOUS_ENCODED);
assert(r.sequence==2&&r.alarm_errors>0&&r.logical_alarm_active&&!r.virtual_start_permitted);
assert(r.alarm_ids.next_id==UINT64_MAX);
''')

    def test_sdk_entry_has_no_physical_output_or_erase_and_separate_target(self):
        sdk = (ROOT/'firmware/src/esp32_continuous_main.h').read_text(encoding='utf-8')
        for guard in ('NVS_READONLY', 'vgw_demo', 'vg_continuous_poll', 'vg_storage_submit',
                      'vg_net_submit', 'strcmp(continuous_network_profile.device_id',
                      'mbedtls_platform_zeroize', 'bootloader_random_disable',
                      'VG_CONTINUOUS_ENCODING_REFUSED', 'UNAVAILABLE_LOCAL_RAM_ONLY',
                      'NOT_CONFIGURED_OR_UNAVAILABLE'):
            self.assertIn(guard, sdk)
        for forbidden in ('gpio_set_level(', 'nvs_flash_erase(', 'nvs_set_', 'esp_restart('):
            self.assertNotIn(forbidden, sdk)
        self.assertIn('[env:esp32dev_continuous]', (ROOT/'firmware/platformio.ini').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
