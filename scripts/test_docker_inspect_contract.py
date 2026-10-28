#!/usr/bin/env python3
"""Real Docker formatter + PHP admission against owned synthetic API, never a daemon."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
ID = 'a' * 64
UUID = '12345678-abcd-abcd-abcd-123456789abc'
MARKER = 'synthetic-sensitive-marker'


def selected_template():
    source = (ROOT/'backend/laravel/tests/Support/HostedMySqlService.php').read_text()
    chunk = source.split('$format = ', 1)[1].split(';', 1)[0]
    return ''.join(re.findall(r"'([^']*)'", chunk))


@contextmanager
def owned_api(binds, *, identity=ID, status=200, delay=0, malformed=False, missing_binds=False):
    fixture = {'Id': identity, 'Config': {'Image': 'mysql:8.0', 'Env': [MARKER]},
               'State': {'Running': True}, 'HostConfig': {'Binds': binds, 'Privileged': False, 'NetworkMode': 'owned-ci-network'},
               'NetworkSettings': {'Ports': {'3306/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '3306'}], '33060/tcp': None}},
               'Mounts': [{'Type': 'volume', 'Destination': '/var/lib/mysql', 'Source': MARKER}]}
    if missing_binds:
        del fixture['HostConfig']['Binds']

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_HEAD(self):
            self.respond(True)

        def do_GET(self):
            self.respond(False)

        def respond(self, head):
            if self.path.endswith('/_ping'):
                code, body = 200, b'OK'
            elif self.path.endswith('/containers/'+ID+'/json'):
                if delay:
                    time.sleep(delay)
                code = status
                body = (b'{' if malformed else json.dumps(fixture).encode()) if status == 200 else b'{"message":"No such container: owned-fixture"}'
            elif self.path.endswith('/version'):
                code, body = 200, b'{"ApiVersion":"1.48","MinAPIVersion":"1.24","Version":"28.0.4","Os":"linux"}'
            else:
                code, body = 404, b'{"message":"No such object: owned-fixture"}'
            try:
                self.send_response(code)
                for k, v in [('Content-Type', 'application/json'), ('Api-Version', '1.48'), ('Ostype', 'linux'), ('Content-Length', str(len(body)))]:
                    self.send_header(k, v)
                self.end_headers()
                if not head:
                    self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with tempfile.TemporaryDirectory(prefix='vg-owned-docker-config-') as config:
        env = {k: v for k, v in os.environ.items() if k.upper() in ('SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP')}
        env.update(DOCKER_CONFIG=config, DOCKER_API_VERSION='1.48')
        try:
            yield 'tcp://127.0.0.1:'+str(server.server_port), env
        finally:
            server.shutdown()
            server.server_close()
            thread.join(2)
            if thread.is_alive():
                raise RuntimeError('OWNED_API_CLEANUP_FAILED')


class DockerInspectContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docker = shutil.which(os.environ.get('VG_DOCKER_CLI', 'docker'))
        cls.php = shutil.which(os.environ.get('VG_PHP_CLI', 'php'))
        if not cls.docker or not cls.php:
            raise RuntimeError('FORMATTER_GATE_BLOCKED_REQUIRED_CLI_UNAVAILABLE_NO_TEST_SKIP')
        cls.template = selected_template()

    def docker_call(self, host, env, template, timeout=5):
        args = [self.docker, '--host='+host, 'inspect']
        if template is not None:
            args += ['--format', template]
        return subprocess.run([*args, ID], env=env, capture_output=True, timeout=timeout)

    def admit(self, output):
        source = '''require $argv[1].'/backend/laravel/vendor/autoload.php';
        $method=new ReflectionMethod(Tests\\Support\\HostedMySqlService::class,'serviceProof');$n=0;
        try {$method->invoke(null,str_repeat('a',64),static function()use(&$n,$argv){return ++$n===1?$argv[2]:'12345678-abcd-abcd-abcd-123456789abc';});echo 'ADMITTED';}
        catch(Throwable $e){echo $e->getMessage();exit(3);}'''
        return subprocess.run([self.php, '-r', source, str(ROOT), output.decode()], capture_output=True, timeout=5)

    def assert_safe(self, result):
        self.assertEqual(result.returncode, 0, 'DOCKER_FORMATTER_UNEXPECTED_NONZERO_RAW_DETAILS_WITHHELD')
        self.assertNotIn(MARKER.encode(), result.stdout)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, dict)
        self.assertEqual(set(data), {'id','image','running','binds','privileged','network','ports','mounts'})
        return data

    def test_published_template_negative_oracle_reproduces_null_length_error(self):
        old = self.template.replace('{{if .HostConfig.Binds}}{{len .HostConfig.Binds}}{{else}}0{{end}}', '{{len .HostConfig.Binds}}')
        self.assertEqual(hashlib.sha256(old.encode()).hexdigest(), '9431b8a442fa6e818f8369505b296224cad6f72f8ed14ca10158b26605f384cb')
        with owned_api(None) as (host, env):
            result = self.docker_call(host, env, old)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b'error calling len:', result.stderr)
        self.assertEqual(result.stdout.strip(), b'')

    def test_null_binds_renders_zero_and_passes_unchanged_php_guard(self):
        with owned_api(None) as (host, env):
            result = self.docker_call(host, env, self.template)
        self.assertEqual(self.assert_safe(result)['binds'], 0)
        admitted = self.admit(result.stdout)
        self.assertEqual((admitted.returncode, admitted.stdout), (0, b'ADMITTED'))

    def test_empty_array_binds_renders_zero_and_passes_php_guard(self):
        with owned_api([]) as (host, env):
            result = self.docker_call(host, env, self.template)
        self.assertEqual(self.assert_safe(result)['binds'], 0)
        admitted = self.admit(result.stdout)
        self.assertEqual((admitted.returncode, admitted.stdout), (0, b'ADMITTED'))

    def test_nonempty_binds_still_rejected_by_php_guard(self):
        with owned_api([MARKER]) as (host, env):
            result = self.docker_call(host, env, self.template)
        self.assertEqual(self.assert_safe(result)['binds'], 1)
        admitted = self.admit(result.stdout)
        self.assertEqual((admitted.returncode, admitted.stdout), (3, b'MYSQL_TEST_BLOCKED: SERVICE_PROPERTY_MISMATCH BINDS.'))

    def test_malformed_bind_types_are_not_normalized_to_no_binds(self):
        for value in [False, 0, {}, '', MARKER]:
            with self.subTest(kind=type(value).__name__), owned_api(value) as (host, env):
                result = self.docker_call(host, env, self.template)
            self.assertNotEqual(result.returncode, 0)

    def test_missing_bind_property_is_not_normalized_to_null(self):
        with owned_api(None, missing_binds=True) as (host, env):
            result = self.docker_call(host, env, self.template)
        self.assertNotEqual(result.returncode, 0)

    def test_inspected_identity_mismatch_still_denied(self):
        with owned_api(None, identity='b'*64) as (host, env):
            result = self.docker_call(host, env, self.template)
        self.assert_safe(result)
        admitted = self.admit(result.stdout)
        self.assertEqual((admitted.returncode, admitted.stdout), (3, b'MYSQL_TEST_BLOCKED: SERVICE_IDENTITY_MISMATCH.'))

    def test_unformatted_array_is_rejected_by_object_parser(self):
        with owned_api(None) as (host, env):
            result = self.docker_call(host, env, None)
        self.assertEqual(result.returncode, 0)
        self.assertIsInstance(json.loads(result.stdout), list)
        admitted = self.admit(result.stdout)
        self.assertEqual((admitted.returncode, admitted.stdout), (3, b'MYSQL_TEST_BLOCKED: DOCKER_INSPECT_JSON_INVALID.'))

    def test_missing_container_is_nonzero(self):
        with owned_api(None, status=404) as (host, env):
            result = self.docker_call(host, env, self.template)
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stderr, rb'No such (?:container|object):')

    def test_malformed_api_output_is_nonzero(self):
        with owned_api(None, malformed=True) as (host, env):
            result = self.docker_call(host, env, self.template)
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_go_template_is_nonzero(self):
        with owned_api(None) as (host, env):
            result = self.docker_call(host, env, '{{')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'template parsing error:', result.stderr)

    def test_owned_slow_api_times_out_and_cleans_resources(self):
        with owned_api(None, delay=1) as (host, env):
            with self.assertRaises(subprocess.TimeoutExpired):
                self.docker_call(host, env, self.template, timeout=0.2)

    def test_argv_template_does_not_read_environment_or_private_mount_source(self):
        self.assertNotIn('Config.Env', self.template)
        self.assertNotIn('$m.Source', self.template)
        self.assertIn('{{if .HostConfig.Binds}}', self.template)
        self.assertIn('{{json .NetworkSettings.Ports}}', self.template)


if __name__ == '__main__':
    unittest.main()
