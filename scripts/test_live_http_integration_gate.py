"""Adversarial lifecycle tests; synthetic subprocesses never count as network PASS."""
from contextlib import ExitStack, redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import run_live_http_integration as gate


class LiveHttpGateTest(unittest.TestCase):
    @staticmethod
    def result(code=0, output=''):
        return subprocess.CompletedProcess([], code, output, '')

    def invoke(self, args, results, fixture=None, live=False, suite_error=None, snapshots=None):
        with ExitStack() as stack:
            stack.enter_context(patch.object(sys, 'argv', ['live-test', '--php-binary', 'synthetic-php', *args]))
            command = stack.enter_context(patch.object(gate, 'php_run', side_effect=results))
            builder = stack.enter_context(patch.object(gate, 'build_bytes', side_effect=fixture) if fixture else
                                          patch.object(gate, 'build_bytes', return_value=b'synthetic-wire\n'))
            stack.enter_context(patch.object(gate, 'build_domain_bytes', return_value=b'synthetic-domain-wire\n'))
            stack.enter_context(patch.object(gate, 'build_alarm_bytes', return_value=b'synthetic-alarm-wire\n'))
            popen = stack.enter_context(patch.object(gate.subprocess, 'Popen'))
            suite = stack.enter_context(patch.object(gate, 'suite', side_effect=suite_error))
            if snapshots is not None:
                stack.enter_context(patch.object(gate, 'source_snapshot', side_effect=snapshots))
            if live:
                stack.enter_context(patch.object(gate.ssl, 'SSLContext'))
                stack.enter_context(patch.object(gate.ssl, 'create_default_context'))
                sock = stack.enter_context(patch.object(gate.socket, 'socket'))
                sock.return_value.__enter__.return_value.getsockname.return_value = ('127.0.0.1', 12345)
                proxy = stack.enter_context(patch.object(gate, 'LoopbackTLSProxy'))
                proxy.return_value.server_port = 23456
                stack.enter_context(patch.object(gate.threading, 'Thread'))
                client = stack.enter_context(patch.object(gate, 'Client'))
                client.return_value.request.return_value = (200, {}, b'')
                popen.return_value.poll.return_value = None
            output = io.StringIO()
            with redirect_stdout(output):
                code = gate.main()
            return code, command, builder, popen, suite, output.getvalue()

    def test_race_helper_refuses_an_unowned_temporary_root_before_process_or_file_changes(self):
        with tempfile.TemporaryDirectory(prefix='vg-foreign-race-') as folder:
            marker = Path(folder)/'keep.txt'; marker.write_bytes(b'keep')
            with patch.object(gate.subprocess, 'Popen') as process, self.assertRaises(gate.GateFailure):
                gate.event_races(None, 'synthetic-php', {'VG_LIVE_HTTP_LEASE':str(Path(folder)/'vg-live-lease.json')}, {}, b'{}')
            process.assert_not_called()
            self.assertEqual(marker.read_bytes(), b'keep')

    def test_second_race_process_spawn_failure_stops_and_closes_the_first(self):
        packet = b'{"schema_version":"1.1","alarm":{"reason_code":1001}}'
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as folder:
            process = MagicMock(); process.poll.return_value = None
            with patch.object(gate.subprocess, 'Popen', side_effect=[process, OSError('synthetic')]), self.assertRaises(OSError):
                gate.event_races(None, 'synthetic-php', {'VG_LIVE_HTTP_LEASE':str(Path(folder)/'vg-live-lease.json')}, {'id':'a'*32}, packet)
            process.terminate.assert_called_once()
            process.wait.assert_called_once()
            process.stdout.close.assert_called_once(); process.stderr.close.assert_called_once()
            self.assertFalse(list(Path(folder).glob('*.go')))

    def test_race_barrier_failure_cannot_release_or_leave_a_live_worker(self):
        packet = b'{"schema_version":"1.1","alarm":{"reason_code":1001}}'
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as folder:
            first, second = MagicMock(), MagicMock()
            first.poll.return_value = 0; second.poll.return_value = None
            with patch.object(gate.subprocess, 'Popen', side_effect=[first, second]), redirect_stdout(io.StringIO()), self.assertRaises(gate.GateFailure):
                gate.event_races(None, 'synthetic-php', {'VG_LIVE_HTTP_LEASE':str(Path(folder)/'vg-live-lease.json')}, {'id':'a'*32}, packet)
            second.terminate.assert_called_once()
            first.wait.assert_called_once(); second.wait.assert_called_once()
            self.assertFalse(list(Path(folder).glob('*.go')))

    def test_real_php_race_fixture_requires_execute_before_bootstrap_or_environment(self):
        env = {key:value for key,value in os.environ.items() if key.upper() in {'PATH','SYSTEMROOT','TEMP','TMP','WINDIR'}}
        result = subprocess.run([os.environ.get('VG_PHP_CLI','php'),str(gate.ROOT/'scripts/live_http_event_race.php'),'a','v11i'],
                                env=env,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,3)
        self.assertEqual(result.stdout,'')
        self.assertIn('explicit supported CLI fixture action required',result.stderr)

    def test_default_is_read_only_and_conflicting_connection_overrides_are_preserved(self):
        with patch.dict(os.environ, {'DB_URL': 'synthetic-conflicting-override'}):
            code, command, builder, popen, suite, output = self.invoke([], [self.result()])
        self.assertEqual(code, 0)
        self.assertEqual(command.call_count, 1)
        self.assertEqual(command.call_args.args[2], ['--check'])
        self.assertEqual(command.call_args.args[3]['DB_URL'], 'synthetic-conflicting-override')
        self.assertEqual(command.call_args.args[3]['LOG_CHANNEL'], '"null"')
        self.assertIn('NOT_RUN_READ_ONLY', output)
        builder.assert_not_called(); popen.assert_not_called(); suite.assert_not_called()

    def test_rejected_preflight_never_builds_launches_or_prepares_fixtures(self):
        code, command, builder, popen, suite, output = self.invoke(['--execute'], [self.result(3)])
        self.assertEqual(code, 3)
        self.assertEqual(command.call_count, 1)
        builder.assert_not_called(); popen.assert_not_called(); suite.assert_not_called()
        self.assertIn('BLOCKED_PREFLIGHT_NO_FIXTURES', output)

    def test_failed_c99_assertion_is_fail_and_precedes_any_fixture_mutation(self):
        code, command, _, popen, suite, output = self.invoke(['--execute'], [self.result()], fixture=AssertionError('synthetic'))
        self.assertEqual(code, 1)
        self.assertEqual(command.call_count, 1)
        popen.assert_not_called(); suite.assert_not_called()
        self.assertIn('FAIL_PREREQUISITE_ASSERTION', output)

    def test_failed_domain_c99_build_precedes_any_live_fixture(self):
        with patch.object(gate, 'build_domain_bytes', side_effect=AssertionError('synthetic-domain')):
            # Invoke's normal fixture patch is intentionally bypassed here.
            stream = io.StringIO()
            with patch.object(sys, 'argv', ['gate', '--php-binary', 'synthetic-php', '--execute']), \
                 patch.object(gate, 'php_run', return_value=self.result()) as command, \
                 patch.object(gate, 'build_bytes', return_value=b'legacy'), \
                 patch.object(gate.subprocess, 'Popen') as process, redirect_stdout(stream):
                self.assertEqual(gate.main(), 1)
            self.assertEqual(command.call_count, 1)
            process.assert_not_called()
            self.assertIn('FAIL_PREREQUISITE_ASSERTION', stream.getvalue())

    def test_failed_alarm_c99_build_precedes_live_fixture_mutation(self):
        stream = io.StringIO()
        with patch.object(sys, 'argv', ['gate', '--php-binary', 'synthetic-php', '--execute']), \
             patch.object(gate, 'php_run', return_value=self.result()) as command, \
             patch.object(gate, 'build_bytes', return_value=b'legacy'), \
             patch.object(gate, 'build_domain_bytes', return_value=b'domain'), \
             patch.object(gate, 'build_alarm_bytes', side_effect=AssertionError('synthetic-alarm')), \
             patch.object(gate.subprocess, 'Popen') as process, redirect_stdout(stream):
            self.assertEqual(gate.main(), 1)
        self.assertEqual(command.call_count, 1)
        process.assert_not_called()
        self.assertIn('FAIL_PREREQUISITE_ASSERTION', stream.getvalue())

    def test_unavailable_tls_prerequisite_blocks_before_server_or_database_fixtures(self):
        code, command, _, popen, suite, output = self.invoke(['--execute'], [self.result(), self.result(3)])
        self.assertEqual(code, 3)
        self.assertEqual(command.call_count, 2)
        popen.assert_not_called(); suite.assert_not_called()
        self.assertIn('BLOCKED_TLS_PREREQUISITE_NO_FIXTURES', output)

    def test_failed_network_case_stops_owned_process_and_cleans_only_through_guard(self):
        code, command, _, popen, _, output = self.invoke(['--execute'], [self.result()] * 4,
            live=True, suite_error=gate.GateFailure('SYNTHETIC_CASE'))
        self.assertEqual(code, 1)
        self.assertEqual([call.args[2] for call in command.call_args_list][2:],
                         [['--prepare', '--execute'], ['--cleanup', '--execute']])
        popen.return_value.terminate.assert_called_once()
        self.assertIn('CLEANUP=PASS_EXACT_OWNERSHIP_ZERO_APPLICATION_ROWS', output)
        self.assertNotIn('GATE=PASS_LOCAL_ONLY', output)

    def test_blocked_cleanup_cannot_be_a_pass_and_retains_lease_without_private_key(self):
        captured = {}
        def execute(binary, script, args, env):
            captured['folder'] = Path(env['VG_LIVE_HTTP_LEASE']).parent
            if script.name == 'live_http_tls.php':
                (captured['folder']/'server-key.pem').write_bytes(b'synthetic-key-fixture')
            return self.result(3 if args == ['--cleanup', '--execute'] else 0)
        try:
            code, _, _, _, _, output = self.invoke(['--execute'], execute, live=True)
            self.assertEqual(code, 3)
            self.assertTrue((captured['folder']/'vg-live-lease.json').is_file())
            self.assertFalse((captured['folder']/'server-key.pem').exists())
            self.assertNotIn('GATE=PASS_LOCAL_ONLY', output)
            self.assertIn('BLOCKED_NO_BROAD_DELETION', output)
        finally:
            if 'folder' in captured and gate.owned_temporary_root(captured['folder']):
                shutil.rmtree(captured['folder'])

    def test_arbitrary_temporary_directory_is_never_removed(self):
        with tempfile.TemporaryDirectory(prefix='vg-unrelated-owner-test-') as folder:
            target = Path(folder).resolve()
            self.assertEqual(target.parent, Path(tempfile.gettempdir()).resolve())
            self.assertTrue(target.name.startswith('vg-unrelated-owner-test-'))
            with patch.object(sys, 'argv', ['live', '--php-binary', 'synthetic-php']), \
                 patch.object(gate.tempfile, 'mkdtemp', return_value=str(target)), \
                 patch.object(gate.shutil, 'rmtree') as remove, self.assertRaises(gate.GateFailure):
                gate.main()
            remove.assert_not_called()

    def test_source_change_cannot_be_certified_by_successful_requests_and_cleanup(self):
        code, _, _, _, _, output = self.invoke(['--execute'], [self.result()] * 4, live=True,
            snapshots=[{'synthetic-input': 'before'}, {'synthetic-input': 'after'}])
        self.assertEqual(code, 1)
        self.assertIn('FAIL_SOURCE_CHANGED_DURING_TEST', output)
        self.assertNotIn('GATE=PASS_LOCAL_ONLY', output)

    def test_response_leak_guard_also_covers_per_request_unknown_bearer(self):
        material = 'synthetic-'+str(id(self))
        client = gate.Client('https://127.0.0.1:1', None, 'synthetic', [])
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = 401
        response.read.return_value = material.encode()
        with patch.object(client.opener, 'open', return_value=response), self.assertRaises(gate.GateFailure):
            client.request('/api/v1/device/state', headers={'Authorization': 'Bearer '+material})

    def test_fixture_write_requires_execute_before_any_environment_or_database_boot(self):
        env = {key: value for key, value in os.environ.items() if key.upper() in {'PATH', 'SYSTEMROOT', 'TEMP', 'TMP', 'WINDIR'}}
        command = [os.environ.get('VG_PHP_CLI', 'php'), '-d', 'display_errors=0',
                   str(gate.ROOT/'scripts/live_http_fixture.php'), '--prepare']
        result = subprocess.run(command, cwd=gate.ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn('explicit supported fixture action required', result.stderr)
        self.assertNotIn('PREPARE_PASS', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
