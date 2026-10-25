"""Actual loopback PHP/TLS/session gate. Default read-only; isolated fixtures only.

Never boot the normal dotenv app or print response bodies, cookies, keys or test
inputs. --execute admits a known empty isolated catalog, then cleans only rows
owned by its random fixture namespace. This is not deployed/ESP32 TLS evidence.
"""
import argparse
import base64
import hashlib
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
from build_esp32_port import source_snapshot as firmware_source_snapshot

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
        'live_http_router.php', 'live_http_tls.php', 'runtime_uplink_wire_bridge.py',
        'runtime_uplink_wire_fixture.c', 'phase9_b4_testlib.py')]
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


def api(client, path, data=None, token=None, media='application/json'):
    headers = {'Accept': 'application/json'}
    if token is not None:
        headers['Authorization'] = 'Bearer '+token
    if data is not None:
        headers['Content-Type'] = media
    return client.request(path, data, headers)


def suite(client, binary, env, profile, wire, context, port):
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
    status, _, body = client.request('/monitoring')
    expect('GRANT_FILTERED_DEVICE_LIST', status == 200 and b'runtime:demo' in body and profile['other'].encode() not in body)
    device_path = '/monitoring/'+urllib.parse.quote('runtime:demo', safe='')
    status, _, body = client.request(device_path)
    expect('CONNECTED_BROWSER_DATA_AND_SIMULATION', status == 200 and b'demo_channel' in body and b'SIMULATION' in body and b'LIVE' in body
           and b'ACK bukan CLEAR' in body and b'alarm_ack' in body and b'alarm_cleared' in body)
    expect('BROWSER_VALID_ZERO_RENDERED', bool(re.search(rb'<td>demo_channel</td><td>\s*0(?:\.0)?\s*</td>', body)))
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
    env.update(MONITORING_STALE_AFTER_SECONDS='60', MONITORING_OFFLINE_AFTER_SECONDS='120')
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
            suite(client, args.php_binary, env, profile, wire, context, port)
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
