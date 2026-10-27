"""Deterministic/negative host tests. Never replace actual60second TLS execution."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from data_ui_contracts import strict_json
from resilience_native_bridge import Actor, build, check_record, fast_packets
from run_live_http_integration import GateFailure, LoopbackTLSProxy, ProxyHandler
from review_formal_resilience import review, ROOT
from resilience_live_extension import mapped


class ResilienceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory(prefix='vg-resilience-')
        cls.exe = build(Path(cls.folder.name).resolve())
        cls.rows = fast_packets(cls.exe)

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_native_actual_provider_policy_metadata_and_valid_gated_recovery(self):
        self.assertEqual([len(r['events']) for r in self.rows], [0,2,2,4])
        self.assertEqual([r['local_alarm'] for r in self.rows], [False,True,True,False])
        self.assertEqual(self.rows[-1]['events'][:2], self.rows[1]['events'])
        self.assertEqual([e['event_type'] for e in self.rows[-1]['events']],
                         ['alarm_raised','alarm_raised','alarm_cleared','alarm_cleared'])

    def test_actual_native_retry_budget_stops_until_explicit_reset(self):
        actor = Actor(self.exe)
        try:
            row = actor.tick(0,0)
            for now in range(100,10000,100):
                row = actor.tick(now,1,3)
            self.assertTrue(row['exhausted'])
            self.assertEqual(row['begin'],3)
            # A healthy external observation cannot revive an exhausted cycle.
            row = actor.tick(10000,1,1)
            self.assertTrue(row['exhausted']); self.assertEqual(row['begin'],3)
            row = actor.tick(10100,1,0,1)
            self.assertFalse(row['exhausted']); self.assertEqual(row['begin'],4)
            row = actor.tick(10200,1,1)
            self.assertEqual(row['network_state'],2)
            self.assertTrue(row['local_alarm'])
            self.assertEqual(len(row['events']),2)
            row = actor.tick(10300,2,1)
            self.assertTrue(row['local_alarm'])
            row = actor.tick(10400,3,1)
            self.assertFalse(row['local_alarm']); self.assertEqual(len(row['events']),4)
        finally:
            actor.close()

    def test_actual_native_pending_timeout_and_backoff_boundary(self):
        actor = Actor(self.exe)
        try:
            actor.tick(0,0)
            self.assertEqual(actor.tick(1900,1)['network_state'],1)
            self.assertEqual(actor.tick(2000,1)['network_state'],3)
            self.assertEqual(actor.tick(2200,1)['network_state'],3)
            self.assertEqual(actor.tick(2300,1)['network_state'],0)
            self.assertEqual(actor.tick(2400,1)['begin'],2)
        finally:
            actor.close()

    def test_actor_command_admission_rejects_malformed_regressing_out_of_bound_inputs(self):
        inputs = (b'X 0 0 0 0\n',b'T -1 0 0 0\n',b'T 4294967296 0 0 0\n',
                  b'T 0 4 0 0\n',b'T 0 0 4 0\n',b'T 0 0 0 2\n',b'T 0 0 0\n',
                  b'T 0 0 0 0 extra\n',b'T 0 0 0 0',b'T 0 0 0 0\nT 0 0 0 0\n')
        inputs += (b'T +0 0 0 0\n',b'T 1e2 0 0 0\n',b'T '+b'9'*64+b' 0 0 0\n',
                   b'T 0 '+b'9'*64+b' 0 0\n',b'T 0 0 0 0 \n')
        for raw in inputs:
            with self.subTest(raw=raw):
                result = subprocess.run([str(self.exe)], input=raw, capture_output=True,timeout=5)
                self.assertEqual(result.returncode,3)

    def test_independent_oracle_rejects_bad_types_quality_early_clear_and_empty_events(self):
        cases = []
        for field,value in [('sequence',True),('now_ms',True),('exhausted',0),('local_alarm',False),
                            ('events',[]),('network_state',4)]:
            row=copy.deepcopy(self.rows[1]); row[field]=value; cases.append(row)
        row=copy.deepcopy(self.rows[1]); row['packet']['channels']['compartment_temperature_c']['value']=0;cases.append(row)
        row=copy.deepcopy(self.rows[1]); row['packet']['channels']['hatch_state']['quality']='invalid';cases.append(row)
        row=copy.deepcopy(self.rows[1]); row['events'][0]['event_type']='alarm_cleared';cases.append(row)
        row=copy.deepcopy(self.rows[1]); row['events'][0]['alarm']['acknowledged_at_ms']=0;cases.append(row)
        row=copy.deepcopy(self.rows[1]); row['events'][0]['alarm']['priority_code']=2;cases.append(row)
        for row in cases:
            with self.assertRaises(ValueError): check_record(row,100,1,self.rows[0])
        with self.assertRaises(ValueError): strict_json('{"sequence":1,"sequence":2}')

    def test_immutable_prefix_identity_and_no_secret_build_admission(self):
        row=copy.deepcopy(self.rows[2]); row['events'][0]['occurred_at_ms']=101
        with self.assertRaises(ValueError): check_record(row,200,2,self.rows[1])
        with tempfile.TemporaryDirectory(prefix='foreign-native-') as folder:
            with self.assertRaises(ValueError): build(Path(folder).resolve())
        with self.assertRaises(ValueError): build(Path(self.folder.name).resolve())

    def test_integration_mapping_changes_only_approved_device_and_lease_boot(self):
        packets,events=mapped(self.rows,'runtime:demo','resilience-'+'a'*32)
        for row,packet in zip(self.rows,packets):
            expected=dict(row['packet'],device_id='runtime:demo',boot_id='resilience-'+'a'*32)
            self.assertEqual(packet,expected)
        for original,event in zip(self.rows[-1]['events'],events):
            self.assertEqual(event,dict(original,device_id='runtime:demo',boot_id='resilience-'+'a'*32))
        for device,boot in [('foreign','resilience-'+'a'*32),('runtime:demo','resilience-'+'A'*32),
                            ('runtime:demo','resilience-'+'a'*31)]:
            with self.assertRaises(ValueError):mapped(self.rows,device,boot)

    def test_private_outage_binding_minimum_sixty_seconds_and_no_external_control(self):
        proxy = LoopbackTLSProxy(('127.0.0.1',0),ProxyHandler)
        try:
            agent='vg-live/'+'a'*32
            with self.assertRaises(GateFailure): proxy.arm_readonly_api_outage('foreign',b'{}')
            with patch('run_live_http_integration.time.monotonic',return_value=100):
                proxy.arm_readonly_api_outage(agent,b'{}')
            for method,path,ua,body in [('GET','/api/v1/telemetry',agent,b'{}'),
                    ('POST','/up',agent,b'{}'),('POST','/api/v1/telemetry','foreign',b'{}'),
                    ('POST','/api/v1/telemetry',agent,b'{ }')]:
                self.assertFalse(proxy.readonly_api_unavailable(method,path,ua,body))
            with patch('run_live_http_integration.time.monotonic',return_value=159.999):
                self.assertTrue(proxy.readonly_api_unavailable('POST','/api/v1/telemetry',agent,b'{}'))
                with self.assertRaises(GateFailure): proxy.restore_readonly_api()
            with patch('run_live_http_integration.time.monotonic',return_value=160):
                self.assertEqual(proxy.restore_readonly_api(),60)
            self.assertFalse(proxy.readonly_api_unavailable('POST','/api/v1/telemetry',agent,b'{}'))
            self.assertEqual(len(proxy.readonly_outage_responses),1)
        finally:
            proxy.server_close()


class EvidenceReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Retained actual first run is an immutable historical regression fixture.
        # Its explicit historical source binding must never imply current-source PASS.
        cls.text=(ROOT/'evidence/test-results/formal-resilience-live-run1-20261027.txt').read_text(encoding='utf-8')
        cls.digest=next(line.rsplit('_',1)[1] for line in cls.text.splitlines()
                        if line.startswith('LIVE_HTTP_SOURCE_STABILITY=PASS_SHA256_'))

    def test_actual_historical_record_passes_only_its_explicit_source_binding(self):
        result=review(self.text,self.digest)
        self.assertEqual(result['record']['responses'][-1]['status'],200)
        self.assertFalse(result['record']['database_writes'])
        with self.assertRaises(ValueError):review(self.text,'0'*64)

    def test_reject_shortened_false_timing_missing_states_implicit_ack_and_vacuous_counters(self):
        prefix='FORMAL_RESILIENCE_RECORD='
        original=json.loads(next(line[len(prefix):] for line in self.text.splitlines() if line.startswith(prefix)))
        changes=[('outage_elapsed_ms',59999),('outage_elapsed_ms',True),('sampling_cycles',0),
                 ('exhausted_cycles',0),('maximum_observed_sampling_gap_ms',1001),
                 ('explicit_reset_count',0),('database_writes',True),('physical_runtime',True),
                 ('responses',[]),('ordered_events',[])]
        mutated=[]
        for field,value in changes:
            record=copy.deepcopy(original);record[field]=value;mutated.append(record)
        record=copy.deepcopy(original);record['observations']['stale']['local_alarm']=False;mutated.append(record)
        record=copy.deepcopy(original);record['observations']['network_restored_sensor_invalid']['temperature']={'quality':'valid','value':30};mutated.append(record)
        record=copy.deepcopy(original);record['ordered_events'][0]['alarm']['acknowledged_at_ms']=0;mutated.append(record)
        record=copy.deepcopy(original);record['ordered_events'][2]['occurred_at_ms']=60000;mutated.append(record)
        record=copy.deepcopy(original);record['responses'][2]['status']=200;mutated.append(record)
        record=copy.deepcopy(original);record['unexpected']=1;mutated.append(record)
        for record in mutated:
            text='\n'.join(prefix+json.dumps(record) if line.startswith(prefix) else line for line in self.text.splitlines())+'\n'
            with self.assertRaises(ValueError):review(text,self.digest)

    def test_reject_duplicate_records_wrong_mode_failure_and_incomplete_postflight(self):
        record=next(line for line in self.text.splitlines() if line.startswith('FORMAL_RESILIENCE_RECORD='))
        for text in (record+'\n'+self.text,
                self.text.replace('PASS_READONLY_RESILIENCE_HOST_ONLY_FULL_SUITE_NOT_RUN','PASS_LOCAL_ONLY_HARDWARE_DEPLOYED_TLS_NOT_RUN'),
                self.text.replace('LIVE_HTTP_CLEANUP=PASS_NO_DATABASE_FIXTURES_CREATED\n',''),
                'LIVE_HTTP_CASE=VERIFIED_ISOLATED_FIXTURE_PREPARATION=PASS\n'+self.text,
                'CASE=FAIL_NEGATIVE\n'+self.text):
            with self.assertRaises(ValueError):review(text,self.digest)

    def test_reject_changed_effective_target_invalid_key_and_out_of_order_postflight(self):
        for text in (self.text.replace('vessel_gateway_codex_test','vessel_gateway_main'),
                self.text.replace('"app_key_cipher_compatible":true','"app_key_cipher_compatible":false'),
                self.text.replace('"app_key_cipher_compatible":true','"app_key_cipher_compatible":1')):
            with self.assertRaises(ValueError):review(text,self.digest)
        marker='LIVE_HTTP_CASE=READONLY_RESILIENCE_EXACT_EMPTY_CATALOG_POSTFLIGHT=PASS'
        with self.assertRaises(ValueError):review(marker+'\n'+self.text.replace(marker+'\n',''),self.digest)


if __name__ == '__main__':
    unittest.main(verbosity=2)
