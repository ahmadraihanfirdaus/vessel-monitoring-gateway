"""Separate development integration producer. Owned isolated DB fixtures write.

Native deterministic frames are explicitly rebound only to the approved fixture
device/lease boot; channel values, alarm metadata and original sequence/time stay
unchanged. These fast packets never replace actual60s formal NO_DB_WRITE evidence.
"""
import hashlib
import json
import re
from pathlib import Path

from resilience_native_bridge import build, fast_packets
from live_database_identity import audit_identity_matches


def mapped(rows, device, boot):
    if device != 'runtime:demo' or not boot.startswith('resilience-') or len(boot) != 43:
        raise ValueError('OWNED_INTEGRATION_IDENTITIES_REQUIRED')
    if not re.fullmatch('resilience-[a-f0-9]{32}', boot):
        raise ValueError('EXACT_LEASE_BOOT_REQUIRED')
    packets = [dict(row['packet'],device_id=device,boot_id=boot) for row in rows]
    events = [dict(event,device_id=device,boot_id=boot) for event in rows[-1]['events']]
    return packets, events


def execute(client, binary, env, profile, device_path, api, php_run, expect):
    folder = Path(env['VG_LIVE_HTTP_LEASE']).parent
    rows = fast_packets(build(folder))
    packets, events = mapped(rows,profile['device'] if 'device' in profile else 'runtime:demo',
                             'resilience-'+profile['id'])
    token = env['VG_LIVE_DEVICE_TOKEN']

    def audit():
        result = php_run(binary, Path('scripts/live_http_fixture.php'), ['--resilience-audit'], env)
        if result.returncode:
            raise RuntimeError('RESILIENCE_DIRECT_DB_AUDIT_BLOCKED')
        value=json.loads(result.stdout)
        expect('RESILIENCE_AUDIT_APPROVED_TARGET', audit_identity_matches(value, profile))
        return value

    before = audit()
    expect('RESILIENCE_FRESH_DIRECT_DB_IDENTITIES',before['sample_count'] == 0 and before['event_count'] == 0)
    statuses=[]
    for index, packet in enumerate(packets):
        raw=json.dumps(packet,separators=(',',':')).encode()
        status,_,_=api(client,'/api/v1/telemetry',raw,token)
        statuses.append(status)
        expect('RESILIENCE_NATIVE_FRAME_'+str(index+1)+'_CREATED',status == 201)
        status,_,body=api(client,'/api/v1/device/state',token=token)
        state=json.loads(body).get('state',{})
        expect('RESILIENCE_NATIVE_FRAME_'+str(index+1)+'_EXACT_READBACK',status == 200 and all(
            state.get(k) == v for k,v in packet.items()))
        status,_,body=client.request(device_path)
        expected=(b'VALID',b'INVALID',b'STALE',b'VALID')[index]
        cell=re.search(rb'<td>compartment_temperature_c</td><td>(.*?)</td><td><span class="badge">([A-Z]+)</span>',body,re.S)
        expected_value=(b'25',b'&mdash;',b'65',b'30')[index]
        expect('RESILIENCE_NATIVE_FRAME_'+str(index+1)+'_UI_QUALITY',status == 200
            and cell is not None and cell[2]==expected and cell[1].split(b'<small>',1)[0].strip()==expected_value
            and b'ACK bukan CLEAR' in body and b'SIMULATION' in body)
    for index,event in enumerate(events):
        status,_,_=api(client,'/api/v1/events',json.dumps(event,separators=(',',':')).encode(),token)
        expect('RESILIENCE_NATIVE_EVENT_'+str(index+1)+'_CREATED',status == 201)
    status,_,body=api(client,'/api/v1/device/events?limit=100',token=token)
    persisted=sorted([e for e in json.loads(body).get('items',[]) if e['boot_id']=='resilience-'+profile['id']],
                     key=lambda e:int(e['event_id']))
    def canonical(event):
        value=dict(event)
        for name in ('event_id','linked_alarm_id','source_id','occurred_at_ms'):value[name]=str(value[name])
        value['alarm']={k:(str(v) if k.endswith('_at_ms') and v is not None else v)
                        for k,v in event['alarm'].items()}
        return value
    expect('RESILIENCE_ORDERED_EVENTS_FULL_METADATA_READBACK',status == 200 and len(persisted)==4 and all(
        all(item.get(k)==v for k,v in canonical(event).items()) for item,event in zip(persisted,events)))
    after=audit()
    expected_temperature=[{'quality':p['channels']['compartment_temperature_c']['quality'],
                           'value':p['channels']['compartment_temperature_c']['value']} for p in packets]
    expect('RESILIENCE_DIRECT_DB_EXACT_FOUR_SAMPLE_CHANNELS_QUALITY',after['sample_count']==4
        and after['event_count']==4 and len(after['samples'])==4
        and [s['temperature'] for s in after['samples']]==expected_temperature
        and all(s['channel_count']==44 and s['sequence']==str(i+1) for i,s in enumerate(after['samples'])))
    expect('RESILIENCE_DIRECT_DB_ORIGINAL_EVENT_METADATA',after['events']==[canonical(e) for e in events])
    status,_,body=client.request(device_path)
    html_rows=re.findall(rb'<tr>(.*?)</tr>',body,re.S)
    own_rows=[row for row in html_rows if ('resilience-'+profile['id']).encode() in row]
    expect('RESILIENCE_CONNECTED_UI_ORIGINAL_ALARM_SNAPSHOTS',status==200 and len(own_rows)==4 and all(
        any((event['event_type']+' / '+str(event['linked_alarm_id'])).encode() in row
            and (' / '+str(event['event_id'])+'</td>').encode() in row
            and ('reason code: '+str(event['alarm']['reason_code'])).encode() in row
            and event['alarm']['state'].encode() in row and b'NOT_ACKNOWLEDGED' in row
            for row in own_rows) for event in events))
    print('RESILIENCE_DEVELOPMENT_INTEGRATION_RECORD='+json.dumps(dict(
        producer='actual_native_fast_frames_private_tls_php_mariadb_owned_fixture_writes',
        formal_sixty_second_execution=False,identity_mapping='only_device_and_lease_bound_boot',
        sample_statuses=statuses,sample_count=after['sample_count'],event_count=after['event_count'],
        native_packet_sha256=hashlib.sha256(json.dumps([r['packet'] for r in rows],sort_keys=True).encode()).hexdigest(),
        mapped_packet_sha256=hashlib.sha256(json.dumps(packets,sort_keys=True).encode()).hexdigest(),
        direct_quality=expected_temperature),sort_keys=True),flush=True)
