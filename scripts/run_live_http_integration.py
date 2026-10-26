"""Actual loopback PHP/TLS/session gate. Default read-only; isolated fixtures only.

Never boot the normal dotenv app or print response bodies, cookies, keys or test
inputs. --execute admits a known empty isolated catalog, then cleans only rows
owned by its random fixture namespace. This is not deployed/ESP32 TLS evidence.
"""
import argparse
import base64
import hashlib
import hmac
import html
import http.client
import http.cookiejar
import http.server
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from runtime_uplink_wire_bridge import build_bytes
from continuous_simulation_wire_bridge import build_bytes as build_domain_bytes
from alarm_metadata_wire_bridge import build_bytes as build_alarm_bytes
from recovered_replay_wire_bridge import build_bytes as build_replay_bytes
from event_receipt_native_bridge import build_verifier, verify_receipt, build_retirement_fixture, run_retirement
from build_esp32_port import source_snapshot as firmware_source_snapshot
from data_ui_contracts import functional_observation

ROOT = Path(__file__).resolve().parents[1]
MAX_PROXY_BODY = 8192
MAX_REPLY = 1024 * 1024


class GateFailure(Exception):
    pass


class GateBlocked(Exception):
    pass


def owned_temporary_root(folder):
    return (folder.resolve() == folder and folder.is_dir() and not folder.is_symlink()
            and folder.parent == Path(tempfile.gettempdir()).resolve()
            and folder.name.startswith('vg-live-http-'))


def source_snapshot():
    records = firmware_source_snapshot()
    paths = [ROOT/'scripts'/name for name in ('run_live_http_integration.py', 'live_http_fixture.php',
        'live_http_router.php', 'live_http_tls.php', 'live_http_event_race.php', 'runtime_uplink_wire_bridge.py',
        'runtime_uplink_wire_fixture.c', 'continuous_simulation_wire_bridge.py',
        'continuous_simulation_fixture.c', 'alarm_metadata_wire_bridge.py',
        'alarm_metadata_wire_fixture.c', 'recovered_replay_wire_bridge.py',
        'recovered_replay_wire_fixture.c', 'test_offline_transaction.py',
        'event_receipt_native_bridge.py', 'event_receipt_native_crypto.h',
        'event_receipt_verify_fixture.c', 'event_retirement_file_fixture.c', 'phase9_b4_testlib.py',
        'data_ui_contracts.py', 'test_data_ui_contracts.py', 'run_formal_data_native.py',
        'review_formal_data_ui.py', 'test_review_formal_data_ui.py', 'test_formal_data_native.py')]
    paths.append(ROOT/'docs/testing/formal-data-ui-cases-20261026.md')
    base = ROOT/'backend/laravel'
    paths += [base/'bootstrap/app.php', base/'composer.lock']
    for directory in ('app', 'config', 'routes', 'resources/views', 'tests/Support', 'database/migrations'):
        paths += list((base/directory).rglob('*.php'))
    records.update({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(set(paths)) if p.is_file()})
    return records


def expect(name, condition):
    if not re.fullmatch('[A-Z0-9_]+', name):
        raise ValueError('invalid case label')
    print('LIVE_HTTP_CASE='+name+('=PASS' if condition else '=FAIL'), flush=True)
    if not condition:
        raise GateFailure(name)


def php_run(binary, script, arguments, env):
    return subprocess.run([binary, '-d', 'display_errors=0', '-d', 'log_errors=0',
                           str(ROOT/script), *arguments], cwd=ROOT, env=env,
                          capture_output=True, text=True, errors='replace', timeout=40)


class LoopbackTLSProxy(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, address):
        # Never log request headers, bodies, cookies or exception contents.
        pass


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def log_message(self, *args):
        pass

    def relay(self):
        self.connection.settimeout(10)
        allowed = {'127.0.0.1:'+str(self.server.server_port), 'localhost:'+str(self.server.server_port)}
        lengths = self.headers.get_all('Content-Length', [])
        if self.headers.get('Host') not in allowed or self.headers.get('Transfer-Encoding') is not None or len(lengths) > 1:
            self.send_error(400)
            return
        raw_length = lengths[0] if lengths else '0'
        if not re.fullmatch('[0-9]+', raw_length) or len(raw_length) > 5:
            self.send_error(400)
            return
        length = int(raw_length)
        if length > MAX_PROXY_BODY:
            self.send_error(413)
            return
        body = self.rfile.read(length)
        if len(body) != length:
            self.send_error(400)
            return
        headers = {key: value for key, value in self.headers.items()
                   if key.lower() not in {'connection', 'transfer-encoding', 'content-length'}
                   and not key.lower().startswith('x-forwarded-')}
        headers['X-Forwarded-Proto'] = 'https'
        headers['Content-Length'] = str(length)
        headers['Connection'] = 'close'
        upstream = http.client.HTTPConnection('127.0.0.1', self.server.backend_port, timeout=15)
        try:
            upstream.request(self.command, self.path, body=body, headers=headers)
            response = upstream.getresponse()
            output = response.read(MAX_REPLY+1)
            if len(output) > MAX_REPLY:
                self.send_error(502)
                return
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in {'connection', 'transfer-encoding', 'content-length'}:
                    self.send_header(key, value)
            self.send_header('Content-Length', str(len(output)))
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(output)
        except (OSError, http.client.HTTPException):
            self.send_error(502)
        finally:
            upstream.close()

    do_GET = relay
    do_POST = relay
    do_HEAD = relay


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


class Client:
    def __init__(self, base, context, agent, hidden):
        self.base, self.agent, self.hidden = base, agent, hidden
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}),
            urllib.request.HTTPSHandler(context=context), NoRedirect(),
            urllib.request.HTTPCookieProcessor(self.cookies))

    def request(self, path, data=None, headers=None, method=None):
        if not path.startswith('/') or path.startswith('//'):
            raise GateFailure('NONLOCAL_REQUEST_DENIED')
        all_headers = {'User-Agent': self.agent}
        all_headers.update(headers or {})
        request = urllib.request.Request(self.base+path, data=data, headers=all_headers, method=method)
        try:
            response = self.opener.open(request, timeout=20)
        except urllib.error.HTTPError as exception:
            response = exception
        with response:
            body = response.read(MAX_REPLY+1)
            hidden = list(self.hidden)
            for key, value in all_headers.items():
                if key.lower() == 'authorization' and value.lower().startswith('bearer '):
                    hidden.append(value[7:])
            if len(body) > MAX_REPLY or any(value and value.encode() in body for value in hidden):
                raise GateFailure('RESPONSE_SIZE_OR_SECRET_LEAK')
            return response.status, response.headers, body


def csrf(body):
    match = re.search(rb'name="_token"\s+value="([^"]+)"', body)
    if match is None:
        raise GateFailure('MISSING_CSRF_FORM')
    return html.unescape(match[1].decode('ascii'))


def form(values):
    return urllib.parse.urlencode(values).encode()


def api(client, path, data=None, token=None, media='application/json', receipt=False):
    headers = {'Accept': 'application/json'}
    if token is not None:
        headers['Authorization'] = 'Bearer '+token
    if data is not None:
        headers['Content-Type'] = media
    if receipt:
        headers['X-VG-Event-Receipt'] = '1'
    return client.request(path, data, headers)


def event_races(client, binary, env, profile, alarm_wire):
    """Two real PHP kernels/DB transactions; no ordinary app or test-isolation mutation."""
    folder = Path(env['VG_LIVE_HTTP_LEASE']).parent.resolve()
    if not owned_temporary_root(folder):
        raise GateFailure('RACE_TEMPORARY_ROOT_OUTSIDE_OWNED_SCOPE')
    for case in ('v10i', 'v11i', 'v11c', 'v11n'):
        processes = []
        try:
            for role in ('a', 'b'):
                if not owned_temporary_root(folder):
                    raise GateFailure('RACE_TEMPORARY_ROOT_CHANGED')
                payload = json.loads(alarm_wire.splitlines()[0])
                payload['boot_id'] = case+'-'+profile['id']
                if case == 'v10i':
                    payload['schema_version'] = '1.0'; del payload['alarm']
                elif case == 'v11c' and role == 'b':
                    payload['alarm']['reason_code'] += 1
                path = folder/('event-race-'+case+'-'+role+'.json')
                with path.open('xb') as output:
                    output.write(json.dumps(payload).encode())
                processes.append(subprocess.Popen([binary, '-d', 'display_errors=0', '-d', 'log_errors=0',
                    str(ROOT/'scripts/live_http_event_race.php'), role, case, '--execute'],
                    cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0))
            until = time.monotonic()+15
            ready = False
            while time.monotonic() < until:
                if any(process.poll() is not None for process in processes):
                    break
                ready = all((folder/('event-race-'+case+'-'+role+'.ready')).is_file() for role in ('a', 'b'))
                if ready:
                    break
                time.sleep(0.01)
            expect('EVENT_RACE_'+case.upper()+'_BOTH_SNAPSHOTS_READY', ready)
            results = []
            for role, process in zip(('a', 'b'), processes):
                if not owned_temporary_root(folder):
                    raise GateFailure('RACE_TEMPORARY_ROOT_CHANGED')
                with (folder/('event-race-'+case+'-'+role+'.go')).open('xb') as marker:
                    marker.write(b'GO\n')
                output, error = process.communicate(timeout=15)
                match = re.search(rb'^EVENT_RACE_RESULT=(\d{3})$', output, re.M)
                if process.returncode != 0 or error or match is None:
                    raise GateFailure('EVENT_RACE_WORKER_FAILED')
                results.append(int(match.group(1)))
                isolation = re.search(rb'^EVENT_RACE_ISOLATION=([A-Z-]+)$', output, re.M)
                if isolation is None:
                    raise GateFailure('EVENT_RACE_ISOLATION_MISSING')
                print('EVENT_RACE_'+case.upper()+'_'+role.upper()+'_ISOLATION='+isolation.group(1).decode('ascii'), flush=True)
            print('EVENT_RACE_'+case.upper()+'_OBSERVED_STATUSES='+','.join(map(str, results)), flush=True)
            expect('EVENT_RACE_'+case.upper()+'_EXACT_RESULT', results == [201, 409 if case == 'v11c' else 200])
        finally:
            for process in processes:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=5)
                if process.stdout is not None: process.stdout.close()
                if process.stderr is not None: process.stderr.close()
    status, _, response = client.request('/api/v1/device/events?limit=100',
                                        headers={'Authorization': 'Bearer '+env['VG_LIVE_DEVICE_TOKEN']})
    race_boots = {case+'-'+profile['id'] for case in ('v10i', 'v11i', 'v11c', 'v11n')}
    raced = [item for item in json.loads(response).get('items', []) if item['boot_id'] in race_boots]
    expect('EVENT_RACE_FOUR_IDENTITIES_PERSIST_ONCE', status == 200 and len(raced) == 4
           and {item['boot_id'] for item in raced} == race_boots)
    conflict = next(item for item in raced if item['boot_id'].startswith('v11c-'))
    expect('EVENT_RACE_CONFLICT_DOES_NOT_OVERWRITE_METADATA', conflict['alarm']['reason_code'] == 1001)


def data_ui_extension(client, binary, env, profile, native_packet, functional):
    """Separate development integration producer; owned DB/session fixtures write.

    The later SUP015 functional review reads this source-bound record only.
    Physical-labelled variants below are synthetic JSON, never C99 acquisition.
    """
    token = env['VG_LIVE_DEVICE_TOKEN']
    original = json.loads(native_packet)

    def audit():
        result = php_run(binary, Path('scripts/live_http_fixture.php'), ['--formal-audit'], env)
        if result.returncode:
            raise GateFailure('FORMAL_DIRECT_DB_AUDIT_BLOCKED')
        value = json.loads(result.stdout)
        expect('FORMAL_AUDIT_APPROVED_DATABASE_AND_ACCOUNT', value.get('database') == 'vessel_gateway_codex_test'
               and value.get('username') == 'vgw_codex')
        return value['facts']

    initial = audit()
    expect('FRESH_FORMAL_IDENTITIES_ABSENT', set(initial) == {
        'src-simulation', 'src-bench_test', 'src-physical', 'dedup', 'authbad'}
        and all(value == {'count': 0, 'rows': []} for value in initial.values()))
    statuses = {}
    for mode in ('simulation', 'bench_test', 'physical'):
        packet = json.loads(native_packet)
        packet.update(boot_id='src-'+mode+'-'+profile['id'], sequence=1, source_mode=mode)
        status, _, _ = api(client, '/api/v1/telemetry', json.dumps(packet).encode(), token)
        statuses[mode] = status
        expect('SYNTHETIC_SOURCE_'+mode.upper()+'_CONTRACT_ACCEPTED', status == 201)
        status, _, body = api(client, '/api/v1/device/state', token=token)
        sample = json.loads(body).get('state', {})
        expect('SYNTHETIC_SOURCE_'+mode.upper()+'_READBACK', status == 200
               and all(sample.get(key) == value for key, value in packet.items()))
    rejected = []
    for mode in ('unknown', None):
        packet = json.loads(native_packet)
        packet.update(boot_id='src-invalid-'+profile['id'], sequence=1)
        if mode is None:
            del packet['source_mode']
        else:
            packet['source_mode'] = mode
        status, _, _ = api(client, '/api/v1/telemetry', json.dumps(packet).encode(), token)
        rejected.append(status)
        expect('SOURCE_'+('MISSING' if mode is None else 'UNKNOWN')+'_REJECTED', status == 422)
    packet = json.loads(native_packet)
    packet.update(boot_id='dedup-'+profile['id'], sequence=1)
    exact = json.dumps(packet).encode()
    dedup_statuses = []
    for label, raw, wanted in (('CREATE', exact, 201), ('IDENTICAL', exact, 200)):
        status, _, _ = api(client, '/api/v1/telemetry', raw, token)
        dedup_statuses.append(status)
        expect('FORMAL_DEDUP_'+label, status == wanted)
    packet['channels']['demo_channel']['value'] = 43
    status, _, _ = api(client, '/api/v1/telemetry', json.dumps(packet).encode(), token)
    dedup_statuses.append(status)
    expect('FORMAL_DEDUP_CONFLICT', status == 409)
    packet = json.loads(native_packet)
    packet.update(boot_id='authbad-'+profile['id'], sequence=1)
    auth_statuses = []
    for label, bearer in (('ABSENT', None), ('UNKNOWN', secrets.token_hex(32))):
        status, _, _ = api(client, '/api/v1/telemetry', json.dumps(packet).encode(), bearer)
        auth_statuses.append(status)
        expect('FORMAL_FRESH_AUTH_'+label, status == 401)
    facts = audit()
    for label, mode in [('src-'+x, x) for x in statuses] + [('dedup', 'simulation')]:
        expected_row = dict(source_mode=mode, schema_version=original['schema_version'],
                            firmware_version=original['firmware_version'], uptime_ms=str(original['uptime_ms']),
                            channel_count=1, quality='valid', value=42)
        expect('FORMAL_DIRECT_DB_'+label.replace('-', '_').upper(), facts[label] == {'count': 1, 'rows': [expected_row]})
    expect('FORMAL_AUTH_DIRECT_DB_ZERO_BEFORE_AND_AFTER', initial['authbad'] == facts['authbad'] == {'count': 0, 'rows': []})
    record = dict(version=1, source_sha256=hashlib.sha256(repr(sorted(source_snapshot().items())).encode()).hexdigest(),
                  producer='actual_loopback_tls_php_mariadb_owned_fixture_writes',
                  physical_acquisition=False, functional=functional, source_statuses=statuses,
                  source_rejected=rejected, dedup_statuses=dedup_statuses, auth_statuses=auth_statuses,
                  database_before=initial, database_after=facts)
    print('DATA_UI_RECORD='+json.dumps(record, sort_keys=True), flush=True)


def suite(client, binary, env, profile, wire, domain_wire, alarm_wire, replay_wire, receipt_verifier, retirement_fixture, context, port):
    token = env['VG_LIVE_DEVICE_TOKEN']

    def action(mode):
        result = php_run(binary, Path('scripts/live_http_fixture.php'), [mode, '--execute'], env)
        expect('FIXTURE_'+mode[2:].replace('-', '_').upper(), result.returncode == 0)

    def sessions():
        result = php_run(binary, Path('scripts/live_http_fixture.php'), ['--session-audit'], env)
        if result.returncode:
            raise GateFailure('SESSION_AUDIT_BLOCKED')
        return json.loads(result.stdout)['sessions']

    for label, trusted, hostname in [('TLS_UNKNOWN_CA_REJECTED', ssl.create_default_context(), '127.0.0.1'),
                                     ('TLS_WRONG_HOST_REJECTED', context, 'unrelated.invalid')]:
        rejected = False
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=3) as raw:
                with trusted.wrap_socket(raw, server_hostname=hostname):
                    pass
        except ssl.SSLCertVerificationError:
            rejected = True
        expect(label, rejected)

    with socket.create_connection(('127.0.0.1', port), timeout=3) as raw:
        raw.sendall(b'GET / HTTP/1.0\r\n\r\n')
        try:
            reply = raw.recv(64)
        except ConnectionResetError:
            reply = b''
        expect('TLS_NO_PLAINTEXT_DOWNGRADE', not reply.startswith(b'HTTP/'))

    status, _, _ = client.request('/login', headers={'Host': 'unrelated.invalid'})
    expect('TLS_PROXY_HOST_REJECTED', status == 400)
    status, _, _ = client.request('/login', headers={'User-Agent': 'unrelated'})
    expect('PRIVATE_TEST_ROUTER_REJECTS_UNOWNED_CLIENT', status == 403)
    status, headers, body = client.request('/')
    expect('PROJECT_ENTRY_GUEST_FIXED_HTTPS_NO_STORE', status == 302
           and headers.get('Location') == client.base+'/monitoring'
           and 'no-store' in headers.get('Cache-Control', '') and b'Laravel' not in body)
    status, headers, body = client.request('/?redirect=https://unrelated.invalid', method='HEAD')
    expect('PROJECT_ENTRY_HEAD_NO_BODY_OR_OPEN_REDIRECT', status == 302 and body == b''
           and headers.get('Location') == client.base+'/monitoring')
    status, headers, _ = client.request('/monitoring')
    expect('PROJECT_ENTRY_GUEST_REQUIRES_SESSION', status == 302 and headers.get('Location') == client.base+'/login')

    lines = wire.splitlines()
    for i, line in enumerate(lines, 1):
        status, headers, _ = api(client, '/api/v1/telemetry', line, token)
        expect('C99_FRAME_'+str(i)+'_CREATED_NO_STORE', status == 201 and 'no-store' in headers.get('Cache-Control', ''))
    status, _, body = api(client, '/api/v1/telemetry', lines[0], token)
    expect('EXACT_TELEMETRY_REPLAY', status == 200 and json.loads(body)['result'] == 'identical_duplicate')
    changed = json.loads(lines[0]); changed['channels']['demo_channel']['value'] = 43
    status, _, _ = api(client, '/api/v1/telemetry', json.dumps(changed).encode(), token)
    expect('CONFLICT_CANNOT_OVERWRITE', status == 409)
    status, _, _ = api(client, '/api/v1/telemetry', lines[0]+b' '*(4096-len(lines[0])), token)
    expect('EXACT_4096_BYTE_BOUNDARY', status == 200)
    for label, payload, bearer, media, expected in [
        ('AUTH_MISSING', lines[0], None, 'application/json', 401),
        ('AUTH_UNKNOWN', lines[0], secrets.token_hex(32), 'application/json', 401),
        ('PAYLOAD_4097_REJECTED', b' '*4097, token, 'application/json', 413),
        ('JSONP_REJECTED', lines[0], token, 'application/jsonp', 415),
        ('MALFORMED_JSON_REJECTED', b'{', token, 'application/json', 422),
        ('EMPTY_SCHEMA_REJECTED', b'{}', token, 'application/json', 422),
    ]:
        status, headers, _ = api(client, '/api/v1/telemetry', payload, bearer, media)
        expect(label, status == expected and 'no-store' in headers.get('Cache-Control', ''))
    changed = json.loads(lines[0]); changed['device_id'] = profile['other']
    status, _, _ = api(client, '/api/v1/telemetry', json.dumps(changed).encode(), token)
    expect('DEVICE_IDENTITY_MISMATCH', status == 403)
    status, _, body = api(client, '/api/v1/device/history', token=token)
    items = json.loads(body)['items']
    expect('PERSISTED_SIX_FRAMES_AND_NULL_QUALITY', status == 200 and len(items) == 6 and
           items[0]['sequence'] == 6 and items[-1]['channels']['demo_channel']['value'] == 42 and
           sum(item['channels']['demo_channel']['value'] is None for item in items) == 2)
    expect('NATIVE_SIX_IDENTITIES_VALUES_AND_QUALITIES_RETAINED', all(
        all(item.get(key) == value for key, value in json.loads(packet).items())
        for item, packet in zip(reversed(items), lines)))
    status, _, body = api(client, '/api/v1/device/history?limit=2', token=token)
    page = json.loads(body)
    expect('CURSOR_PAGE_ONE', status == 200 and len(page['items']) == 2 and bool(page['next_cursor']))
    status, _, body = api(client, '/api/v1/device/history?'+urllib.parse.urlencode({'limit': 2, 'cursor': page['next_cursor']}), token=token)
    expect('CURSOR_PAGE_TWO', status == 200 and [x['sequence'] for x in json.loads(body)['items']] == [4, 3])
    # Explicit synthetic HTTP boundary packet; not additional C99 fixture output.
    boundary = json.loads(lines[0])
    boundary.update(sequence=2**64-1, uptime_ms=2**64-1)
    boundary['channels']['demo_channel']['value'] = 0
    status, _, _ = api(client, '/api/v1/telemetry', json.dumps(boundary).encode(), token)
    expect('HTTP_ZERO_UINT64_BOUNDARY_ACCEPTED', status == 201)
    status, _, body = api(client, '/api/v1/device/state', token=token)
    state = json.loads(body)['state']
    expect('JSON_UINT64_EXACT_ZERO_NOT_NULL', status == 200 and state['sequence'] in (2**64-1, str(2**64-1))
           and state['uptime_ms'] in (2**64-1, str(2**64-1)) and state['channels']['demo_channel']['value'] == 0
           and state['channels']['demo_channel']['value'] is not None)

    event = {'schema_version': '1.0', 'device_id': 'runtime:demo', 'boot_id': 'synthetic-http-events',
             'event_id': 1, 'linked_alarm_id': 7, 'source_id': 101, 'source_mode': 'simulation',
             'event_type': 'alarm_raised', 'occurred_at_ms': 100}
    event_wire = json.dumps(event).encode()
    for i, kind in enumerate(('alarm_raised', 'alarm_ack', 'alarm_cleared'), 1):
        event.update(event_id=i, event_type=kind, occurred_at_ms=99+i)
        status, _, _ = api(client, '/api/v1/events', json.dumps(event).encode(), token)
        expect('HTTP_EVENT_'+str(i)+'_CREATED', status == 201)
    status, _, body = api(client, '/api/v1/events', event_wire, token)
    expect('EVENT_EXACT_REPLAY', status == 200 and json.loads(body)['result'] == 'identical_event_duplicate')
    changed = json.loads(event_wire); changed['event_type'] = 'fault'
    status, _, _ = api(client, '/api/v1/events', json.dumps(changed).encode(), token)
    expect('EVENT_CONFLICT_REJECTED', status == 409)
    status, _, body = api(client, '/api/v1/device/events', token=token)
    expect('EVENT_FACTS_RETAIN_ACK_AND_CLEAR', status == 200 and len(json.loads(body)['items']) == 3)

    status, headers, body = client.request('/login')
    expect('REAL_LOGIN_FORM_HEADERS', status == 200 and 'no-store' in headers.get('Cache-Control', '') and
           bool(headers.get('Content-Security-Policy')) and headers.get('X-Content-Type-Options') == 'nosniff')
    session_cookie = next((c for c in client.cookies if c.name == profile['cookie']), None)
    attributes = {key.lower(): value for key, value in session_cookie._rest.items()} if session_cookie is not None else {}
    expect('BROWSER_COOKIE_SECURE_HTTPONLY_SAMESITE', session_cookie is not None and session_cookie.secure and
           'httponly' in attributes and attributes.get('samesite') == 'lax')
    values = {'email': profile['email'], 'password': env['VG_LIVE_LOGIN_SECRET']}
    status, headers, _ = client.request('/login', form(values), {'Content-Type': 'application/x-www-form-urlencoded'})
    expect('REAL_CSRF_REJECTS_MISSING_TOKEN', status == 419 and 'no-store' in headers.get('Cache-Control', ''))
    status, _, body = client.request('/login')
    values['_token'] = csrf(body)
    before = {x['fingerprint'] for x in sessions()}
    status, headers, _ = client.request('/login', form(values), {'Content-Type': 'application/x-www-form-urlencoded'})
    expect('REAL_LOGIN_REDIRECT_STAYS_HTTPS', status == 302 and headers.get('Location') == client.base+'/monitoring')
    signed = sessions(); authenticated = {x['fingerprint'] for x in signed if x['authenticated']}
    expect('REAL_DATABASE_SESSION_ID_ROTATED', len(authenticated) == 1 and not authenticated.intersection(before))
    status, headers, _ = client.request('/')
    expect('PROJECT_ENTRY_AUTHENTICATED_FIXED_ROUTE', status == 302 and headers.get('Location') == client.base+'/monitoring')
    status, _, body = client.request('/monitoring')
    expect('GRANT_FILTERED_DEVICE_LIST', status == 200 and b'runtime:demo' in body and profile['other'].encode() not in body)
    device_path = '/monitoring/'+urllib.parse.quote('runtime:demo', safe='')
    status, _, body = client.request(device_path)
    expect('CONNECTED_BROWSER_DATA_AND_SIMULATION', status == 200 and b'demo_channel' in body and b'SIMULATION' in body and b'LIVE' in body
           and b'ACK bukan CLEAR' in body and b'alarm_ack' in body and b'alarm_cleared' in body)
    expect('BROWSER_VALID_ZERO_RENDERED', bool(re.search(rb'<td>demo_channel</td><td>\s*0(?:\.0)?\s*</td>', body)))
    for index, packet in enumerate(domain_wire.splitlines()):
        status, _, _ = api(client, '/api/v1/telemetry', packet, token)
        expect('CONTINUOUS_C99_FRAME_'+str(index+1), status == 201)
    status, _, body = client.request('/api/v1/device/state', headers={'Authorization': 'Bearer '+token})
    state = json.loads(body).get('state', {})
    expect('CONTINUOUS_48_CHANNELS_PERSISTED', status == 200 and state.get('schema_version') == '1.1'
           and state.get('sequence') == 24 and len(state.get('channels', {})) == 48)
    expect('NATIVE_V11_IDENTITY_AND_ALL_48_QUALITIES_RETAINED', all(
        state.get(key) == value for key, value in json.loads(domain_wire.splitlines()[-1]).items()))
    channels = state['channels']
    expect('CONTINUOUS_FULL_JOURNAL_DIAGNOSTIC', channels['runtime_journal_retained']['value'] == 8
           and channels['runtime_journal_rejected']['value'] == 58)
    status, _, body = client.request(device_path)
    expect('CONTINUOUS_BROWSER_DOMAIN_LABELS', status == 200 and b'engine_4_rpm' in body and b'RUNNING' in body
           and b'unitless surrogate; not ppm or %LEL' in body and b'low-power prototype' in body)
    status, _, _ = api(client, '/api/v1/telemetry', domain_wire.splitlines()[-1], token)
    expect('CONTINUOUS_C99_IDENTICAL_REPLAY', status == 200)
    packet = domain_wire.splitlines()[-1]
    status, _, _ = api(client, '/api/v1/telemetry', packet+b' '*(4097-len(packet)), token)
    expect('CONTINUOUS_BYTE_BOUNDARY_REJECTED', status == 413)
    for index, packet in enumerate(alarm_wire.splitlines()):
        status, _, _ = api(client, '/api/v1/events', packet, token)
        expect('ALARM_METADATA_C99_EVENT_'+str(index+1), status == 201)
    status, _, response = client.request('/api/v1/device/events?limit=100', headers={'Authorization': 'Bearer '+token})
    items = json.loads(response).get('items', [])
    complete = [item for item in items if item['schema_version'] == '1.1']
    expect('ALARM_METADATA_FACTS_PERSISTED', status == 200 and len(items) == 14 and len(complete) == 11)
    zero = {item['event_id']: item['alarm'] for item in complete if item['boot_id'] == 'synthetic-alarm-zero'}
    expect('ALARM_ZERO_ACK_NULL_CLEAR_EXACT', len(zero) == 3 and zero['1']['acknowledged_at_ms'] is None
           and zero['2']['state'] == 'active_ack' and zero['2']['acknowledged_at_ms'] == '0'
           and zero['2']['cleared_at_ms'] is None and zero['3']['cleared_at_ms'] == '0')
    packet = alarm_wire.splitlines()[-1]
    status, _, _ = api(client, '/api/v1/events', packet, token)
    expect('ALARM_METADATA_EXACT_REPLAY', status == 200)
    changed = json.loads(packet); changed['alarm']['reason_code'] += 1
    status, _, _ = api(client, '/api/v1/events', json.dumps(changed).encode(), token)
    expect('ALARM_METADATA_CONFLICT_PRESERVES_FACT', status == 409)
    duplicate = alarm_wire.splitlines()[0].replace(b'"priority_code":3', b'"priority_code":3,"\\u0070riority_code":3')
    status, _, _ = api(client, '/api/v1/events', duplicate, token)
    expect('ALARM_METADATA_ESCAPED_DUPLICATE_REJECTED', status == 422)
    bad_ack = alarm_wire.splitlines()[1].replace(b'"cleared_at_ms":null', b'"cleared_at_ms":0')
    status, _, _ = api(client, '/api/v1/events', bad_ack, token)
    expect('ALARM_METADATA_ACK_CANNOT_SMUGGLE_CLEAR', status == 422)
    status, _, body = client.request(device_path)
    expect('ALARM_METADATA_CONNECTED_BROWSER_FACTS', status == 200 and b'Alarm snapshot at transition' in body
           and b'active_ack' in body and b'Priority code (demo):' in body and b'NOT_CLEARED' in body)
    functional = functional_observation(status, body)
    expect('EIGHT_SECTIONS_ACTUAL_AUTHENTICATED_DATA_REVIEW', len(functional['section_counts']) == 8)
    def check_receipt(packet, status, headers, response, expected_status, label):
        digest = hashlib.sha256(packet).hexdigest()
        signature = hmac.new(token.encode(), ('VG_EVENT_COMMIT_V1\n'+str(expected_status)+'\n'+digest).encode(), hashlib.sha256).hexdigest()
        expected = ('VGR1:'+digest+':'+signature).encode()
        expect(label+'_STANDARD_HMAC', status == expected_status and len(response) == 134
               and headers.get('Content-Type') == 'application/vnd.vgw.event-receipt-v1'
               and 'no-store' in headers.get('Cache-Control', '') and hmac.compare_digest(response, expected))
        expect(label+'_NATIVE_VERIFIED', verify_receipt(receipt_verifier, env, packet, status, response))

    first_signed = None
    for index, packet in enumerate(replay_wire.splitlines()):
        status, headers, response = api(client, '/api/v1/events', packet, token, receipt=True)
        expect('RECOVERED_C99_CROSS_BOOT_EVENT_'+str(index+1), status == 201)
        check_receipt(packet, status, headers, response, 201, 'EVENT_RECEIPT_CREATED_'+str(index+1))
        if index == 0:
            first_signed = (packet, response)
        status, _, response = api(client, '/api/v1/events', packet, token)
        expect('RECOVERED_C99_EXACT_DUPLICATE_'+str(index+1),
               status == 200 and json.loads(response)['result'] == 'identical_event_duplicate')
        status, headers, response = api(client, '/api/v1/events', packet, token, receipt=True)
        check_receipt(packet, status, headers, response, 200, 'EVENT_RECEIPT_DUPLICATE_'+str(index+1))
    packet, signed = first_signed
    wrong_env = env.copy(); wrong_env['VG_LIVE_DEVICE_TOKEN'] = secrets.token_hex(32)
    expect('EVENT_RECEIPT_NATIVE_WRONG_KEY_REFUSED', not verify_receipt(receipt_verifier, wrong_env, packet, 201, signed))
    expect('EVENT_RECEIPT_NATIVE_WRONG_BODY_REFUSED', not verify_receipt(receipt_verifier, env, b' '+packet, 201, signed))
    expect('EVENT_RECEIPT_NATIVE_WRONG_SUCCESS_STATUS_REFUSED', not verify_receipt(receipt_verifier, env, packet, 200, signed))
    tampered = signed[:-1]+(b'0' if signed[-1:] != b'0' else b'1')
    expect('EVENT_RECEIPT_NATIVE_VALID_HEX_FORGERY_REFUSED', not verify_receipt(receipt_verifier, env, packet, 201, tampered))
    expect('EVENT_RECEIPT_NATIVE_OTHER_EVENT_REFUSED', not verify_receipt(receipt_verifier, env, replay_wire.splitlines()[1], 201, signed))
    expect('EVENT_RECEIPT_NATIVE_MISSING_CONFIRMATION_REFUSED', not verify_receipt(receipt_verifier, env, packet, 201, b''))

    # Actual C99 continuous facts -> actual PHP/MariaDB TLS commit -> exact HMAC
    # -> shared transaction/file commit/readback -> shared owner RAM retirement.
    # Private file reopen is host evidence, never ESP32 crash/power-loss proof.
    old_packet = run_retirement(retirement_fixture, env, 'prepare', profile['id'])
    old_fact = json.loads(old_packet)
    expect('RETIREMENT_REAL_C99_OLD_BOOT_FACT', old_fact['schema_version'] == '1.1'
           and old_fact['boot_id'] == 'receipt-'+profile['id'] and old_fact['event_id'] == 1)
    status, headers, signed_old = api(client, '/api/v1/events', old_packet, token, receipt=True)
    check_receipt(old_packet, status, headers, signed_old, 201, 'RETIREMENT_OLD_BOOT_COMMIT')
    current_packet = run_retirement(retirement_fixture, env, 'old', profile['id'], old_packet, status, signed_old)
    current_fact = json.loads(current_packet)
    expect('RETIREMENT_OLD_EXACT_FACT_DURABLY_REMOVED_CURRENT_RAM_UNCHANGED',
           current_fact['boot_id'] == 'receipt-next-'+profile['id'] and current_fact['event_id'] == 1)
    status, headers, signed_current = api(client, '/api/v1/events', current_packet, token, receipt=True)
    check_receipt(current_packet, status, headers, signed_current, 201, 'RETIREMENT_CURRENT_BOOT_COMMIT')
    slots = [retirement_fixture.parent/('receipt-slot'+str(i)+'.bin') for i in range(2)]
    before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in slots]
    forged = signed_current[:-1]+(b'0' if signed_current[-1:] != b'0' else b'1')
    refused = run_retirement(retirement_fixture, env, 'tamper', profile['id'], current_packet, status, forged)
    expect('RETIREMENT_FORGED_MAC_NO_FILE_WRITES_OR_RAM_RELEASE', refused == b'REFUSED'
           and before == [hashlib.sha256(path.read_bytes()).hexdigest() for path in slots])
    next_packet = run_retirement(retirement_fixture, env, 'current', profile['id'], current_packet, status, signed_current)
    next_fact = json.loads(next_packet)
    expect('RETIREMENT_CURRENT_FLOOR_RAM_RELEASE_NO_ID_REWIND_AND_NEW_FACT',
           next_fact['boot_id'] == current_fact['boot_id'] and next_fact['event_id'] > current_fact['event_id'])
    expect('RETIREMENT_HOST_FILE_REOPEN_NO_RESURRECTION_FRESH_BOOT_GUARD',
           run_retirement(retirement_fixture, env, 'inspect', profile['id']) == b'CHECKED')
    status, headers, signed_next = api(client, '/api/v1/events', next_packet, token, receipt=True)
    check_receipt(next_packet, status, headers, signed_next, 201, 'RETIREMENT_NEW_FACT_COMMIT')
    status, headers, signed_again = api(client, '/api/v1/events', next_packet, token, receipt=True)
    check_receipt(next_packet, status, headers, signed_again, 200, 'RETIREMENT_NEW_FACT_DUPLICATE')
    status, _, response = client.request('/api/v1/events', packet, {'Authorization':'Bearer '+token,
        'Content-Type':'application/json', 'Accept':'application/json', 'X-VG-Event-Receipt':'2'})
    expect('EVENT_RECEIPT_UNSUPPORTED_VERSION_NO_CONFIRMATION', status == 400
           and json.loads(response).get('error') == 'invalid_event_receipt_version')
    status, _, response = api(client, '/api/v1/device/events?limit=100', token=token)
    recovered = [item for item in json.loads(response).get('items', [])
                 if item['boot_id'] in ('boot-a', 'replay-boot-b', 'replay-boot-c')]
    expect('RECOVERED_THREE_BOOT_IDS_REMAIN_DISTINCT', status == 200 and len(recovered) == 6
           and sorted(item['boot_id'] for item in recovered if item['event_id'] == '1')
           == ['boot-a', 'replay-boot-b', 'replay-boot-c'])
    legacy = [item for item in recovered if item['schema_version'] == '1.0']
    expect('RECOVERED_LEGACY_METADATA_NOT_FABRICATED', len(legacy) == 2
           and all('alarm' not in item for item in legacy)
           and any(item['event_type'] == 'fault' and item['source_mode'] == 'bench_test'
                   and item['linked_alarm_id'] == '0' for item in legacy))
    ack = [item for item in recovered if item['boot_id'] == 'replay-boot-b' and item['event_id'] == '2']
    expect('RECOVERED_ACK_ZERO_IS_NOT_NULL_OR_CLEAR', len(ack) == 1 and ack[0]['alarm']['state'] == 'active_ack'
           and ack[0]['alarm']['acknowledged_at_ms'] == '0' and ack[0]['alarm']['cleared_at_ms'] is None)
    changed = json.loads(replay_wire.splitlines()[-1]); changed['alarm']['reason_code'] = 1003
    status, headers, response = api(client, '/api/v1/events', json.dumps(changed).encode(), token, receipt=True)
    expect('RECOVERED_VALID_METADATA_CONFLICT_REJECTED', status == 409)
    expect('EVENT_RECEIPT_CONFLICT_HAS_NO_CONFIRMATION', headers.get('Content-Type', '').startswith('application/json')
           and not response.startswith(b'VGR1:'))
    status, _, response = api(client, '/api/v1/device/state', token=token)
    expect('RECOVERED_EVENT_REPLAY_PRESERVES_LATEST_TELEMETRY', status == 200
           and json.loads(response)['state']['sequence'] == 24)
    packet = replay_wire.splitlines()[0]
    status, _, _ = api(client, '/api/v1/events', packet+b' '*(4097-len(packet)), token)
    expect('RECOVERED_REPLAY_BODY_CAP_RETAINED', status == 413)
    duplicate = packet.replace(b'"boot_id":', b'"boot_id":"spoof","\\u0062oot_id":')
    status, _, _ = api(client, '/api/v1/events', duplicate, token)
    expect('RECOVERED_REPLAY_ESCAPED_BOOT_DUPLICATE_REJECTED', status == 422)
    status, _, body = client.request(device_path)
    expect('RECOVERED_CONNECTED_BROWSER_ORIGINAL_BOOT_FACTS', status == 200
           and all(boot in body for boot in (b'boot-a', b'replay-boot-b', b'replay-boot-c'))
           and b'tidak direkonstruksi dari event lain' in body and b'ACK bukan CLEAR' in body)
    event_races(client, binary, env, profile, alarm_wire)
    data_ui_extension(client, binary, env, profile, lines[0], functional)
    logout_token = csrf(body)
    status, _, _ = client.request('/monitoring/'+profile['other'])
    expect('UNGRANTED_DEVICE_404', status == 404)
    action('--revoke')
    status, _, _ = client.request(device_path)
    expect('GRANT_REVOCATION_EFFECTIVE_NEXT_REQUEST', status == 404)
    action('--grant')
    action('--disable')
    status, _, _ = client.request('/monitoring')
    expect('USER_DISABLE_EFFECTIVE_NEXT_REQUEST', status == 403)
    action('--enable')
    status, _, body = client.request(device_path)
    expect('REENABLED_GRANT_READ', status == 200)
    logout_token = csrf(body)
    status, _, _ = client.request('/logout', form({'_token': logout_token}), {'Content-Type': 'application/x-www-form-urlencoded'})
    expect('REAL_LOGOUT_REDIRECT_STAYS_HTTPS', status == 302)
    after = sessions()
    expect('LOGOUT_DESTROYS_AUTHENTICATED_SESSION', not any(x['authenticated'] for x in after) and
           not authenticated.intersection({x['fingerprint'] for x in after}))
    status, headers, _ = client.request('/monitoring')
    expect('LOGGED_OUT_BROWSER_DENIED', status == 302 and headers.get('Location') == client.base+'/login')
    action('--clear-cache')  # Independent rate-limit case starts with its own empty namespaced cache.
    for attempt in range(5):
        _, _, body = client.request('/login')
        wrong = secrets.token_hex(20)
        status, _, _ = client.request('/login', form({'_token': csrf(body), 'email': profile['email'], 'password': wrong}),
                                      {'Content-Type': 'application/x-www-form-urlencoded'})
        expect('LOGIN_FAILURE_'+str(attempt+1), status == 302)
        _, _, body = client.request('/login')
        expect('LOGIN_FAILURE_NO_PASSWORD_ECHO_'+str(attempt+1), wrong.encode() not in body)
    status, headers, _ = client.request('/login', form({'_token': csrf(body), 'email': profile['email'], 'password': secrets.token_hex(20)}),
                                       {'Content-Type': 'application/x-www-form-urlencoded'})
    expect('REAL_PERSISTENT_RATE_LIMIT', status == 429 and headers.get('Retry-After', '').isdigit() and
           'no-store' in headers.get('Cache-Control', ''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--php-binary', required=True)
    parser.add_argument('--testing-env', action='store_true')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    code = 0
    server = proxy = thread = log = None
    attempted_fixture = False
    folder = Path(tempfile.mkdtemp(prefix='vg-live-http-')).resolve()
    # Validate the owned target before any eventual recursive temporary cleanup.
    if not owned_temporary_root(folder):
        raise GateFailure('TEMPORARY_ROOT_OUTSIDE_OWNED_SCOPE')
    inputs = source_snapshot()
    identity = secrets.token_hex(16)
    profile = {'id': identity, 'agent': 'vg-live/'+identity, 'cookie': 'live_'+identity,
               'email': 'live-'+identity+'@example.test', 'other': 'live-other-'+identity}
    (folder/'vg-live-lease.json').write_text(json.dumps({'id': identity}), encoding='utf-8')
    env = os.environ.copy()
    env.update(VG_LIVE_HTTP_LEASE=str(folder/'vg-live-lease.json'), VG_PHP_CLI=args.php_binary,
               SESSION_DRIVER='database', CACHE_STORE='database', CACHE_PREFIX='live_'+identity+':',
               SESSION_COOKIE=profile['cookie'], SESSION_SECURE_COOKIE='true', SESSION_HTTP_ONLY='true',
               SESSION_SAME_SITE='lax', SESSION_PATH='/', SESSION_DOMAIN='', LOG_CHANNEL='"null"',
               QUEUE_CONNECTION='sync', APP_DEBUG='false', VG_TEST_EPHEMERAL_KEY='1',
               PULSE_ENABLED='false', TELESCOPE_ENABLED='false', NIGHTWATCH_ENABLED='false')
    # Explicit integration-fixture age policy, never an operational default/SLA.
    env.update(MONITORING_STALE_AFTER_SECONDS='60', MONITORING_OFFLINE_AFTER_SECONDS='120',
               MONITORING_PRESENTATION_PROFILE='continuous_simulation_v11')
    env['APP_KEY'] = 'base64:'+base64.b64encode(secrets.token_bytes(32)).decode()
    env['VG_LIVE_LOGIN_SECRET'] = secrets.token_hex(20)
    env['VG_LIVE_DEVICE_TOKEN'] = secrets.token_hex(32)
    if args.testing_env:
        env['VG_USE_TESTING_ENV'] = '1'
    try:
        preflight = php_run(args.php_binary, Path('scripts/live_http_fixture.php'), ['--check'], env)
        if preflight.returncode:
            print('LIVE_HTTP_GATE=BLOCKED_PREFLIGHT_NO_FIXTURES', flush=True)
            code = 3
        elif not args.execute:
            print(preflight.stdout, end='')
            print('LIVE_HTTP_GATE=NOT_RUN_READ_ONLY', flush=True)
        else:
            print(preflight.stdout, end='')
            wire = build_bytes()
            print('LIVE_HTTP_C99_WIRE_SHA256='+hashlib.sha256(wire).hexdigest(), flush=True)
            domain_wire = build_domain_bytes('runtime:demo')
            print('LIVE_HTTP_CONTINUOUS_C99_WIRE_SHA256='+hashlib.sha256(domain_wire).hexdigest(), flush=True)
            alarm_wire = build_alarm_bytes('runtime:demo')
            print('LIVE_HTTP_ALARM_METADATA_C99_WIRE_SHA256='+hashlib.sha256(alarm_wire).hexdigest(), flush=True)
            replay_wire = build_replay_bytes('runtime:demo')
            print('LIVE_HTTP_RECOVERED_REPLAY_C99_WIRE_SHA256='+hashlib.sha256(replay_wire).hexdigest(), flush=True)
            receipt_verifier = build_verifier(folder, env)
            print('LIVE_HTTP_RECEIPT_NATIVE_VERIFIER=BUILT_BEFORE_DATABASE_FIXTURES', flush=True)
            retirement_fixture = build_retirement_fixture(folder, env)
            print('LIVE_HTTP_RETIREMENT_NATIVE_FILE_DRIVER=BUILT_BEFORE_DATABASE_FIXTURES', flush=True)
            cert = php_run(args.php_binary, Path('scripts/live_http_tls.php'), [str(folder)], env)
            if cert.returncode:
                raise GateBlocked('TLS_PREREQUISITE_NO_FIXTURES')
            server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            server_context.minimum_version = ssl.TLSVersion.TLSv1_2
            server_context.load_cert_chain(str(folder/'server.pem'), str(folder/'server-key.pem'))
            context = ssl.create_default_context(cafile=str(folder/'ca.pem'))
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1', 0)); backend_port = reservation.getsockname()[1]
            proxy = LoopbackTLSProxy(('127.0.0.1', 0), ProxyHandler)
            proxy.backend_port = backend_port
            proxy.socket = server_context.wrap_socket(proxy.socket, server_side=True)
            port = proxy.server_port
            base = 'https://127.0.0.1:'+str(port)
            env['APP_URL'] = base
            log = (folder/'php-server.log').open('wb')
            server = subprocess.Popen([args.php_binary, '-d', 'display_errors=0', '-d', 'log_errors=0',
                '-S', '127.0.0.1:'+str(backend_port), '-t', str(ROOT/'backend/laravel/public'),
                str(ROOT/'scripts/live_http_router.php')], cwd=ROOT, env=env, stdout=log, stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            thread = threading.Thread(target=proxy.serve_forever, kwargs={'poll_interval': 0.1}, daemon=True)
            thread.start()
            client = Client(base, context, profile['agent'], [env['APP_KEY'], env['VG_LIVE_LOGIN_SECRET'], env['VG_LIVE_DEVICE_TOKEN']])
            ready = False
            until = time.monotonic()+15
            while time.monotonic() < until:
                if server.poll() is not None:
                    break
                try:
                    status, _, _ = client.request('/up')
                    if status == 200:
                        ready = True
                        break
                except (OSError, urllib.error.URLError):
                    pass
                time.sleep(0.05)
            if not ready and server.poll() is not None:
                log.flush()
                diagnostic = (folder/'php-server.log').read_text(encoding='utf-8', errors='replace')[:65536].lower()
                print('LIVE_HTTP_SERVER_EXIT='+str(server.returncode)+'_PERMISSION_DENIED_'+str(
                    any(marker in diagnostic for marker in ('permission', 'access permissions', 'forbidden'))).upper(), flush=True)
            expect('REAL_LOOPBACK_TLS_AND_PHP_READY', ready and server.poll() is None)
            attempted_fixture = True
            prepared = php_run(args.php_binary, Path('scripts/live_http_fixture.php'), ['--prepare', '--execute'], env)
            expect('VERIFIED_ISOLATED_FIXTURE_PREPARATION', prepared.returncode == 0)
            suite(client, args.php_binary, env, profile, wire, domain_wire, alarm_wire, replay_wire, receipt_verifier, retirement_fixture, context, port)
    except GateBlocked as exception:
        print('LIVE_HTTP_GATE=BLOCKED_'+str(exception), flush=True)
        code = 3
    except GateFailure as exception:
        print('LIVE_HTTP_GATE=FAIL_'+str(exception), flush=True)
        code = 1
    except AssertionError:
        print('LIVE_HTTP_GATE=FAIL_PREREQUISITE_ASSERTION', flush=True)
        code = 1
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, ssl.SSLError, RuntimeError) as exception:
        print('LIVE_HTTP_GATE=BLOCKED_'+type(exception).__name__, flush=True)
        code = 3
    except Exception as exception:
        print('LIVE_HTTP_GATE=FAIL_UNEXPECTED_'+type(exception).__name__, flush=True)
        code = 1
    finally:
        if proxy is not None:
            if thread is not None:
                proxy.shutdown(); thread.join(timeout=5)
            proxy.server_close()
        if server is not None:
            if server.poll() is None:
                server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill(); server.wait(timeout=5)
        if log is not None:
            log.close()
        cleanup_ok = True
        if attempted_fixture:
            try:
                cleaned = php_run(args.php_binary, Path('scripts/live_http_fixture.php'), ['--cleanup', '--execute'], env)
                cleanup_ok = cleaned.returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                cleanup_ok = False
            if not cleanup_ok:
                print('LIVE_HTTP_CLEANUP=BLOCKED_NO_BROAD_DELETION', flush=True); code = 3
            else:
                print('LIVE_HTTP_CLEANUP=PASS_EXACT_OWNERSHIP_ZERO_APPLICATION_ROWS', flush=True)
        if not owned_temporary_root(folder):
            raise GateFailure('REFUSE_TEMPORARY_CLEANUP_OUTSIDE_OWNED_ROOT')
        if not cleanup_ok:
            # Retain the nonsecret lease/diagnostic context for explicit recovery.
            # Never leave a generated private TLS key behind on this path.
            key = folder/'server-key.pem'
            if key.exists():
                key.unlink()
            print('LIVE_HTTP_RECOVERY_CONTEXT='+folder.name+'_RETAINED_NO_PRIVATE_KEY', flush=True)
        else:
            shutil.rmtree(folder)
    if code == 0 and args.execute:
        if inputs != source_snapshot():
            print('LIVE_HTTP_GATE=FAIL_SOURCE_CHANGED_DURING_TEST', flush=True)
            code = 1
        else:
            digest = hashlib.sha256(repr(sorted(inputs.items())).encode()).hexdigest()
            print('LIVE_HTTP_SOURCE_STABILITY=PASS_SHA256_'+digest, flush=True)
            print('LIVE_HTTP_GATE=PASS_LOCAL_ONLY_HARDWARE_DEPLOYED_TLS_NOT_RUN', flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
