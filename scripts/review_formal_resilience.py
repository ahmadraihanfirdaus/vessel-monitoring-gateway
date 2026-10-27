"""Independent read-only case review. No PHP bootstrap, network or DB access."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from data_ui_contracts import strict_json
from run_live_http_integration import ROOT, source_snapshot


def review(text, digest):
    lines=text.splitlines()
    if (len(text)>128*1024 or re.search(r'=(?:FAIL|BLOCKED)',text)
            or lines[-2:]!=['LIVE_HTTP_SOURCE_STABILITY=PASS_SHA256_'+digest,
                           'LIVE_HTTP_GATE=PASS_READONLY_RESILIENCE_HOST_ONLY_FULL_SUITE_NOT_RUN']):
        raise ValueError('CURRENT_COMPLETE_READONLY_RUNTIME_REQUIRED')
    for marker in ('LIVE_HTTP_CASE=REAL_LOOPBACK_TLS_AND_PHP_READY=PASS',
                   'LIVE_HTTP_PREFLIGHT=PASS_EXACT_EMPTY_APPROVED_CATALOG_PHP_8_2_35_VALID_PROCESS_KEY',
                   'LIVE_HTTP_CASE=READONLY_RESILIENCE_EXACT_EMPTY_CATALOG_POSTFLIGHT=PASS',
                   'LIVE_HTTP_CLEANUP=PASS_NO_DATABASE_FIXTURES_CREATED',
                   'FORMAL_RESILIENCE=PASS_ACTUAL_HOST_ONLY_NO_DB_WRITE'):
        if lines.count(marker)!=1:raise ValueError('REQUIRED_ACTUAL_GUARD_OR_TERMINAL')
    if any('VERIFIED_ISOLATED_FIXTURE_PREPARATION' in line or 'RESILIENCE_DEVELOPMENT_INTEGRATION_RECORD=' in line for line in lines):
        raise ValueError('FORMAL_NO_DB_WRITE_MODE_REQUIRED')
    found=[line.split('=',1)[1] for line in lines if line.startswith('FORMAL_RESILIENCE_RECORD=')]
    if len(found)!=1:raise ValueError('EXACT_ONE_STRUCTURED_RECORD_REQUIRED')
    configs=[line.split('=',1)[1] for line in lines if line.startswith('LIVE_HTTP_CONFIG_AUDIT=')]
    if len(configs)!=1:raise ValueError('EXACT_ONE_EFFECTIVE_CONFIGURATION_REQUIRED')
    config=strict_json(configs[0]);target=config.get('target',{})
    approved={('127.0.0.1','3307','vessel_gateway_codex_test','vgw_codex'),
              ('127.0.0.1','3306','vessel_gateway_ci','root')}
    if (tuple(str(target.get(name)) for name in ('host','port','database','username')) not in approved
            or config.get('environment')!='testing' or config.get('php')!='8.2.35'
            or config.get('app_key_configured') is not True or config.get('app_key_cipher_compatible') is not True
            or config.get('app_key_source')!='ephemeral_runner_process' or config.get('app_debug') is not False):
        raise ValueError('EFFECTIVE_CONFIG_TARGET_AND_KEY_ADMISSION')
    record_index=next(i for i,line in enumerate(lines) if line.startswith('FORMAL_RESILIENCE_RECORD='))
    if not (lines.index('LIVE_HTTP_CASE=REAL_LOOPBACK_TLS_AND_PHP_READY=PASS')<record_index
            <lines.index('FORMAL_RESILIENCE=PASS_ACTUAL_HOST_ONLY_NO_DB_WRITE')
            <lines.index('LIVE_HTTP_CASE=READONLY_RESILIENCE_EXACT_EMPTY_CATALOG_POSTFLIGHT=PASS')
            <lines.index('LIVE_HTTP_CLEANUP=PASS_NO_DATABASE_FIXTURES_CREATED')<len(lines)-2):
        raise ValueError('ACTUAL_EXECUTION_POSTFLIGHT_ORDER')
    r=strict_json(found[0])
    expected={'version','cases','execution','database_writes','physical_runtime','outage_elapsed_ms',
        'sampling_cycles','fault_cycles','exhausted_cycles','maximum_observed_sampling_gap_ms','external_policy',
        'responses','outage_response_elapsed_ms','explicit_reset_count','ordered_events','observations'}
    if (not isinstance(r,dict) or set(r)!=expected or type(r['version']) is not int or r['version']!=1
            or r['cases']!=['SIM-010','SIM-012','SIM-013'] or r['database_writes'] is not False
            or r['physical_runtime'] is not False
            or r['execution']!='actual_host_c99_and_loopback_tls_readonly_laravel'):
        raise ValueError('ACTUAL_CASE_PROVENANCE')
    bounds={'outage_elapsed_ms':(60000,90000),'sampling_cycles':(500,900),
        'fault_cycles':(500,900),'exhausted_cycles':(400,900),
        'maximum_observed_sampling_gap_ms':(100,1000),'explicit_reset_count':(1,1)}
    for name,(lo,hi) in bounds.items():
        if type(r[name]) is not int or not lo<=r[name]<=hi:raise ValueError('NONVACUOUS_TIMING_'+name.upper())
    if r['fault_cycles']>r['sampling_cycles'] or r['exhausted_cycles']>r['fault_cycles']:
        raise ValueError('IMPOSSIBLE_CYCLE_COUNTS')
    policy=dict(sample_ms=100,connect_timeout_ms=2000,reconnect_backoff_ms=250,max_attempts=3)
    if r['external_policy']!=policy or any(type(v) is not int for v in r['external_policy'].values()):
        raise ValueError('EXPLICIT_POLICY')
    responses=r['responses'];attempts=r['outage_response_elapsed_ms']
    if (not isinstance(responses,list) or len(responses)!=4 or not isinstance(attempts,list) or len(attempts)!=3
            or any(type(t) is not int or not 0<=t<60000 for t in attempts)
            or attempts!=sorted(set(attempts))):raise ValueError('BOUNDED_ACTUAL_REQUESTS')
    for index,response in enumerate(responses):
        if (not isinstance(response,dict) or set(response)!={'status','elapsed_ms'}
                or type(response['status']) is not int or response['status']!=(503 if index<3 else 200)
                or type(response['elapsed_ms']) is not int
                or not (0<=response['elapsed_ms']<60000 if index<3 else 60000<=response['elapsed_ms']<=90000)
                or (index and response['elapsed_ms']<=responses[index-1]['elapsed_ms'])):
            raise ValueError('EXACT_ACTUAL_RESPONSE_TIMELINE')
    o=r['observations'];names={'baseline','fault','offline','network_restored_sensor_invalid','stale','recovered','final'}
    if not isinstance(o,dict) or set(o)!=names:raise ValueError('FULL_STATE_TIMELINE')
    prior_time=-1;prior_sequence=0
    for name in ('baseline','fault','offline','network_restored_sensor_invalid','stale','recovered','final'):
        row=o[name]
        if (not isinstance(row,dict) or set(row)!={'sequence','now_ms','network_state','exhausted','local_alarm',
                'temperature','engine3_rpm','packet_sha256'}
                or type(row['now_ms']) is not int or type(row['sequence']) is not int
                or row['now_ms']<=prior_time or row['sequence']<=prior_sequence
                or type(row['network_state']) is not int or not 0<=row['network_state']<=3
                or type(row['exhausted']) is not bool or type(row['local_alarm']) is not bool
                or not re.fullmatch('[a-f0-9]{64}',row['packet_sha256'])):
            raise ValueError('STRICT_ORDERED_STATE_OBSERVATIONS')
        prior_time=row['now_ms'];prior_sequence=row['sequence']
        alarm=name in {'fault','offline','network_restored_sensor_invalid','stale'}
        expected_temp=({'value':25,'quality':'valid'} if name=='baseline' else
            ({'value':65,'quality':'stale'} if name=='stale' else
             ({'value':None,'quality':'invalid'} if alarm else {'value':30,'quality':'valid'})))
        if (row['temperature']!=expected_temp or row['local_alarm'] is not alarm
                or row['engine3_rpm']!={'quality':'valid','value':1500 if alarm else 2010}):
            raise ValueError('FAULT_AND_VALID_DATA_RECOVERY_STATES')
    if (o['baseline']['now_ms']!=0 or o['baseline']['sequence']!=1 or not o['offline']['exhausted']
            or o['offline']['network_state']==2 or o['network_restored_sensor_invalid']['network_state']!=2
            or o['network_restored_sensor_invalid']['now_ms']<60000 or o['stale']['now_ms']<60500
            or o['recovered']['now_ms']<61000 or o['final']['sequence']!=r['sampling_cycles']+1
            or o['final']['network_state']!=2 or o['final']['exhausted']):
        raise ValueError('EXHAUSTION_EXPLICIT_RESET_VALID_DATA_GATE')
    events=r['ordered_events']
    if not isinstance(events,list) or len(events)!=4:raise ValueError('FOUR_ORIGINAL_LIFECYCLE_FACTS')
    for index,event in enumerate(events):
        raised=index<2;time_ms=o['fault']['now_ms'] if raised else o['recovered']['now_ms']
        expected_event=dict(schema_version='1.1',device_id='resilience:demo',boot_id='synthetic-resilience',
            event_id=index+1,linked_alarm_id=index%2+1,source_id=4 if index%2==0 else 7,
            source_mode='simulation',event_type='alarm_raised' if raised else 'alarm_cleared',occurred_at_ms=time_ms,
            alarm=dict(priority_code=1,reason_code=4003 if index%2==0 else 5001,
                state='active_unack' if raised else 'cleared',raised_at_ms=o['fault']['now_ms'],
                acknowledged_at_ms=None,cleared_at_ms=None if raised else time_ms))
        if json.dumps(event,sort_keys=True)!=json.dumps(expected_event,sort_keys=True):
            raise ValueError('ORIGINAL_FULL_ALARM_METADATA_OR_IMPLICIT_ACK')
    return dict(cases=r['cases'],case_review='PASS_ACTUAL_HOST_ONLY_NO_DB_WRITE',source_sha256=digest,
        evidence_sha256=hashlib.sha256(text.encode()).hexdigest(),record=r,
        hardware_sdk_runtime_deployed_tls='NOT_RUN',final_approval='NOT_APPROVED')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log',type=Path,required=True);parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    if args.report.exists() or args.report.is_symlink():parser.error('refusing to overwrite evidence')
    try:
        from check_living_traceability import public_reference
        relative=args.log.resolve().relative_to(ROOT).as_posix()
        public_reference(relative)
        if not args.report.resolve().is_relative_to(ROOT/'evidence/test-results'):
            raise ValueError('PUBLIC_EVIDENCE_OUTPUT_REQUIRED')
        digest=hashlib.sha256(repr(sorted(source_snapshot().items())).encode()).hexdigest()
        result=review(args.log.read_text(encoding='utf-8'),digest)
        args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
        print('FORMAL_RESILIENCE_REVIEW=PASS_SIM010_SIM012_SIM013_HOST_ONLY')
        return 0
    except (ValueError,TypeError,KeyError,IndexError,UnicodeError,OSError):
        print('FORMAL_RESILIENCE_REVIEW=FAIL_MISSING_STALE_OR_INCONSISTENT_EVIDENCE')
        return 1


if __name__=='__main__':raise SystemExit(main())
