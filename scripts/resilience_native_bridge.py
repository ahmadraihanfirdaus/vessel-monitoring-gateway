"""Strict native host actor bridge; no database, credentials or network calls."""
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading

from data_ui_contracts import strict_json, native_contract

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'scripts/resilience_host_fixture.c'


def build(folder):
    folder = Path(folder)
    if (folder.resolve() != folder or not folder.is_dir() or folder.is_symlink()
            or folder.parent != Path(tempfile.gettempdir()).resolve()
            or not folder.name.startswith(('vg-resilience-', 'vg-live-http-'))):
        raise ValueError('OWNED_TEMPORARY_BUILD_DIRECTORY_REQUIRED')
    exe = folder/('resilience-actor.exe' if os.name == 'nt' else 'resilience-actor')
    if exe.exists() or exe.is_symlink():
        raise ValueError('FRESH_NATIVE_OUTPUT_REQUIRED')
    result = subprocess.run([os.environ.get('VG_HOST_CC', 'gcc'), '-std=c99', '-Wall', '-Wextra',
        '-Werror', '-pedantic', '-Os', '-I', str(ROOT/'firmware/src'), str(FIXTURE), '-o', str(exe),
        *([] if os.name == 'nt' else ['-lm'])], capture_output=True, timeout=60)
    if result.returncode:
        raise RuntimeError('RESILIENCE_NATIVE_COMPILE_FAILED')
    return exe


def check_record(record, now, phase, previous=None):
    if type(now) is not int or type(phase) is not int or not 0 <= phase <= 3:
        raise ValueError('EXACT_OBSERVATION_INPUT_REQUIRED')
    wanted = {'sequence', 'now_ms', 'skipped', 'begin', 'cancel', 'network_state',
              'exhausted', 'local_alarm', 'events', 'packet'}
    if not isinstance(record, dict) or set(record) != wanted:
        raise ValueError('EXACT_NATIVE_SCHEMA_REQUIRED')
    for field in ('sequence', 'now_ms', 'skipped', 'begin', 'cancel', 'network_state'):
        if type(record[field]) is not int or record[field] < 0:
            raise ValueError('INTEGER_NATIVE_COUNTER_REQUIRED')
    if record['now_ms'] != now or record['network_state'] > 3:
        raise ValueError('NATIVE_TIME_OR_NETWORK_STATE')
    for field in ('exhausted', 'local_alarm'):
        if type(record[field]) is not bool:
            raise ValueError('EXACT_NATIVE_BOOLEAN_REQUIRED')
    if record['sequence'] != (previous['sequence'] + 1 if previous else 1):
        raise ValueError('NATIVE_SEQUENCE_ADVANCE_REQUIRED')
    packet = record['packet']
    native_contract((json.dumps(packet, separators=(',', ':'))+'\n').encode())
    if (packet['sequence'] != record['sequence'] or packet['uptime_ms'] != now
            or packet['device_id'] != 'resilience:demo' or packet['boot_id'] != 'synthetic-resilience'
            or packet['schema_version'] != '1.1' or len(packet['channels']) != 44):
        raise ValueError('NATIVE_PACKET_IDENTITY')
    channels = packet['channels']
    temperature = channels['compartment_temperature_c']
    expected = ({'value':25,'quality':'valid'}, {'value':None,'quality':'invalid'},
                {'value':65,'quality':'stale'}, {'value':30,'quality':'valid'})[phase]
    if temperature != expected:
        raise ValueError('TEMPERATURE_QUALITY_VALUE_OR_RECOVERY')
    for name, channel in channels.items():
        if name != 'compartment_temperature_c' and channel['quality'] != 'valid':
            raise ValueError('FAULT_NOT_ISOLATED')
    expected_rpm = 1500 if phase in (1, 2) else 2010
    if channels['engine_3_rpm']['value'] != expected_rpm:
        raise ValueError('ENGINE_STIMULUS')
    if record['local_alarm'] is not (phase in (1, 2)):
        raise ValueError('LOCAL_ALARM_OR_EARLY_CLEAR')
    events = record['events']
    if not isinstance(events, list) or len(events) > 8:
        raise ValueError('BOUNDED_EVENT_ARRAY_REQUIRED')
    if len(events) != (0 if phase == 0 else (4 if phase == 3 else 2)):
        raise ValueError('NONVACUOUS_ALARM_LIFECYCLE_REQUIRED')
    if previous and events[:len(previous['events'])] != previous['events']:
        raise ValueError('IMMUTABLE_EVENT_PREFIX_REQUIRED')
    last = -1
    for index, event in enumerate(events):
        if (event.get('event_id') != index+1 or type(event['event_id']) is not int
                or type(event.get('occurred_at_ms')) is not int or not last <= event['occurred_at_ms'] <= now
                or event.get('source_mode') != 'simulation' or event.get('device_id') != 'resilience:demo'
                or event.get('boot_id') != 'synthetic-resilience'
                or event.get('event_type') not in ('alarm_raised', 'alarm_cleared')):
            raise ValueError('ORDERED_NATIVE_EVENT_REQUIRED')
        last = event['occurred_at_ms']
        if phase in (1, 2) and event['event_type'] == 'alarm_cleared':
            raise ValueError('EARLY_RECOVERY_EVENT')
        if event.get('alarm', {}).get('acknowledged_at_ms') is not None:
            raise ValueError('NO_IMPLICIT_ACK')
        alarm = event.get('alarm', {})
        raised = index < 2
        if (event.get('source_id') != (4 if index % 2 == 0 else 7)
                or event.get('linked_alarm_id') != index % 2+1
                or event['event_type'] != ('alarm_raised' if raised else 'alarm_cleared')
                or alarm.get('priority_code') != 1
                or alarm.get('reason_code') != (4003 if index % 2 == 0 else 5001)
                or alarm.get('state') != ('active_unack' if raised else 'cleared')
                or (raised and alarm.get('cleared_at_ms') is not None)
                or (not raised and alarm.get('cleared_at_ms') != event['occurred_at_ms'])):
            raise ValueError('EXACT_IMMUTABLE_EVENT_METADATA')
    return record


class Actor:
    def __init__(self, exe):
        self.process = subprocess.Popen([str(exe)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        self.rows = queue.Queue(maxsize=2)
        self.previous = None
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        while True:
            raw = self.process.stdout.readline(16385)
            try:
                self.rows.put(raw, timeout=2)
            except queue.Full:
                return
            if not raw or len(raw) > 16384:
                return

    def tick(self, now, phase, observed=0, reset=0):
        if any(type(n) is not int for n in (now, phase, observed, reset)) or not (
                0 <= now <= 2**32-1 and 0 <= phase <= 3 and 0 <= observed <= 3 and reset in (0, 1)):
            raise ValueError('FINITE_NATIVE_COMMAND_REQUIRED')
        self.process.stdin.write(f'T {now} {phase} {observed} {reset}\n'.encode('ascii'))
        self.process.stdin.flush()
        try:
            raw = self.rows.get(timeout=3)
        except queue.Empty:
            raise RuntimeError('NATIVE_ACTOR_PROGRESS_TIMEOUT') from None
        if not raw or len(raw) > 16384 or not raw.endswith(b'\n'):
            raise ValueError('BOUNDED_COMPLETE_NATIVE_RESPONSE_REQUIRED')
        row = check_record(strict_json(raw), now, phase, self.previous)
        self.previous = row
        return row

    def close(self):
        self.process.stdin.close()
        try:
            code = self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=3)
            code = -1
        self.reader.join(timeout=3)
        self.process.stdout.close()
        if code:
            raise RuntimeError('NATIVE_ACTOR_EXIT_NONZERO')


def fast_packets(exe):
    """Deterministic integration fixture only, never actual60second evidence."""
    actor = Actor(exe)
    try:
        rows = [actor.tick(now, phase) for now, phase in ((0, 0), (100, 1), (200, 2), (300, 3))]
        return rows
    finally:
        actor.close()
