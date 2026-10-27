"""Actual >=60s native/TLS host protocol. No database mutations or fixture setup."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time

from resilience_native_bridge import Actor

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT/'docs/testing/formal-resilience-cases-20261027.md'


def execute(exe, client, proxy):
    if 'PROTOCOL_CASE_BY_CASE_REVIEW=PASS_FOR_SIM010_SIM012_SIM013_WITH_BOUNDARIES_ABOVE' not in PROTOCOL.read_text(encoding='utf-8'):
        raise RuntimeError('RESILIENCE_CASE_REVIEW_REQUIRED')
    actor = Actor(exe)
    worker = ThreadPoolExecutor(max_workers=1)
    future = None
    statuses = []
    observations = []
    last_begin = 0
    observed = 0
    restored = False
    reset_sent = False
    last_tick = -100
    previous_wall = None
    max_gap = 0
    rows = 0
    fault_cycles = 0
    exhausted_cycles = 0
    snapshots = {}
    try:
        baseline = actor.tick(0, 0)
        # Baseline starts the native connection cycle. Hold its actual request
        # until the private exact-body fault is armed. No authorization or DB IO.
        wire = json.dumps(baseline['packet'], separators=(',', ':')).encode()
        started = proxy.arm_readonly_api_outage(client.agent, wire)

        def request(recovery):
            if recovery:
                status, _, _ = client.request('/up', timeout=1)
            else:
                status, _, _ = client.request('/api/v1/telemetry', wire,
                    {'Content-Type':'application/json'}, timeout=1)
            return status

        last_begin = baseline['begin']
        future = worker.submit(request, False)
        snapshots['baseline'] = baseline
        while True:
            elapsed = time.monotonic()-started
            if elapsed > 90:
                raise RuntimeError('RESILIENCE_WALL_WATCHDOG')
            now = int(elapsed*1000)
            if now < last_tick+100 or now < 100:
                time.sleep(0.01)
                continue
            if future is not None and future.done():
                # The owned endpoint must actually reply, never treat a socket
                # exception/timeout as successful fault execution or recovery.
                status = future.result()
                expected = 200 if restored else 503
                if type(status) is not int or status != expected:
                    raise ValueError('ACTUAL_OUTAGE_OR_RECOVERY_STATUS')
                statuses.append({'status':status, 'elapsed_ms':now})
                observed = 1 if status == 200 else 3
                future = None
            if now >= 60000 and not restored:
                if future is not None:
                    raise ValueError('NETWORK_WORKER_NOT_QUIESCENT')
                outage_seconds = proxy.restore_readonly_api()
                restored = True
            # Network restored first; keep INVALID, then STALE, then VALID.
            phase = 1 if now < 60500 else (2 if now < 61000 else 3)
            reset = int(restored and not reset_sent)
            if reset:
                reset_sent = True
                observed = 0
            row = actor.tick(now, phase, observed, reset)
            rows += 1
            if previous_wall is not None:
                max_gap = max(max_gap, now-previous_wall)
            previous_wall = now
            last_tick = now
            if phase in (1, 2):
                fault_cycles += 1
            if row['exhausted']:
                exhausted_cycles += 1
            if row['begin'] != last_begin:
                if row['begin'] != last_begin+1 or future is not None:
                    raise ValueError('SINGLE_BOUNDED_NETWORK_WORKER_REQUIRED')
                last_begin = row['begin']
                observed = 0
                future = worker.submit(request, restored)
            if row['exhausted'] and not restored and (last_begin != 3 or future is not None):
                raise ValueError('EXACT_BOUNDED_EXHAUSTION_REQUIRED')
            label = ('recovered' if phase == 3 else ('stale' if phase == 2 else
                    ('network_restored_sensor_invalid' if row['network_state'] == 2 else
                     ('offline' if row['exhausted'] else 'fault'))))
            if label not in snapshots:
                snapshots[label] = row
            if now >= 61300 and future is None:
                snapshots['final'] = row
                break
        required = {'baseline','fault','offline','network_restored_sensor_invalid','stale','recovered','final'}
        if (set(snapshots) != required or rows < 500 or fault_cycles < 500 or exhausted_cycles < 400
                or max_gap > 1000 or last_begin != 4 or len(statuses) != 4
                or [x['status'] for x in statuses] != [503,503,503,200]
                or len(proxy.readonly_outage_responses) != 3 or outage_seconds < 60
                or snapshots['final']['network_state'] != 2 or snapshots['final']['exhausted']):
            raise ValueError('NONVACUOUS_FULL_OUTAGE_AND_RECOVERY_REQUIRED')
        # Exactly two raise and two clear transitions; original prefix persisted
        # unchanged through offline/stale/recovery, no ACK or HTTP-driven release.
        raised = snapshots['offline']['events']
        events = snapshots['final']['events']
        if (len(raised) != 2 or len(events) != 4 or events[:2] != raised
                or [e['event_type'] for e in events] != ['alarm_raised']*2+['alarm_cleared']*2
                or any(e['occurred_at_ms'] < 61000 for e in events[2:])):
            raise ValueError('VALID_DATA_GATED_ORIGINAL_RECOVERY_EVENTS')
        record = dict(version=1, cases=['SIM-010','SIM-012','SIM-013'],
            execution='actual_host_c99_and_loopback_tls_readonly_laravel', database_writes=False,
            physical_runtime=False, outage_elapsed_ms=int(outage_seconds*1000),
            sampling_cycles=rows, fault_cycles=fault_cycles, exhausted_cycles=exhausted_cycles,
            maximum_observed_sampling_gap_ms=max_gap, external_policy=dict(sample_ms=100,
                connect_timeout_ms=2000, reconnect_backoff_ms=250,max_attempts=3),
            responses=statuses, outage_response_elapsed_ms=proxy.readonly_outage_responses,
            explicit_reset_count=1, ordered_events=events,
            observations={name:dict(sequence=row['sequence'], now_ms=row['now_ms'],
                network_state=row['network_state'], exhausted=row['exhausted'], local_alarm=row['local_alarm'],
                temperature=row['packet']['channels']['compartment_temperature_c'],
                engine3_rpm=row['packet']['channels']['engine_3_rpm'],
                packet_sha256=hashlib.sha256(json.dumps(row['packet'],sort_keys=True,separators=(',',':')).encode()).hexdigest())
                for name,row in snapshots.items()})
        print('FORMAL_RESILIENCE_RECORD='+json.dumps(record,sort_keys=True),flush=True)
        print('FORMAL_RESILIENCE=PASS_ACTUAL_HOST_ONLY_NO_DB_WRITE',flush=True)
        return record
    finally:
        worker.shutdown(wait=True, cancel_futures=True)
        actor.close()
