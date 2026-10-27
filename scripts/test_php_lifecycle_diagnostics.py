"""Owned local PHP/TCP lifecycle reproductions; no Laravel/database/environment dump."""
from contextlib import redirect_stdout, redirect_stderr
import http.client
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock

from php_lifecycle_diagnostics import PhpLifecycle, ServerLogCapture
import run_live_http_integration as gate

PHP = os.environ.get('VG_PHP_CLI', 'php')
HOOK = Path(__file__).resolve().parent/'live_http_lifecycle.php'


def records(output):
    return [json.loads(line.split('=', 1)[1]) for line in output.splitlines()
            if line.startswith('LIVE_HTTP_PHP_LIFECYCLE=')]


def spawn(code, *args, stdin=None):
    # No inherited application or database credentials in these standalone fixtures.
    env = {k:v for k,v in os.environ.items() if k.upper() in ('PATH', 'SYSTEMROOT', 'TEMP', 'TMP', 'WINDIR')}
    return subprocess.Popen([PHP, '-d', 'display_errors=0', '-d', 'log_errors=0', '-r', code, '--', *args],
        stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)


class PhpLifecycleTest(unittest.TestCase):
    def test_classifier_retains_only_static_categories_and_bounds_lines_and_count(self):
        capture = ServerLogCapture()
        capture.feed(b'synthetic-private\nVG_LIVE_STAGE=ROWS_ADMITTED\nVG_LIVE_CAUGHT=OTHER\n')
        capture.feed(b'PHP Fatal error: synthetic-private\nVG_LIVE_SHUTDOWN=MEMORY_LIMIT\n')
        capture.feed(b'x'*4096)
        capture.feed(b'synthetic-private\n')
        capture.bytes_seen = capture.COUNT_LIMIT-1
        capture.feed(b'xx\n')
        self.assertLessEqual(len(capture.pending), 4096)
        self.assertTrue(capture.snapshot()['log_line_truncated'])
        self.assertTrue(capture.snapshot()['log_count_capped'])
        self.assertEqual(capture.snapshot()['error_categories'], ['FATAL_ERROR', 'MEMORY_LIMIT'])
        self.assertEqual(capture.snapshot()['caught_categories'], ['OTHER'])
        self.assertNotIn('synthetic-private', json.dumps(capture.snapshot()))
        with self.assertRaises(ValueError):
            capture.feed(b'x'*4097)

    def test_pipe_read_and_close_failure_never_print_raw_thread_exceptions(self):
        class BrokenStream(io.BytesIO):
            def read1(self, size):
                raise OSError('synthetic-private')
            def close(self):
                super().close()
                raise OSError('synthetic-private')
        capture = ServerLogCapture()
        error = io.StringIO()
        with redirect_stderr(error):
            capture.start(BrokenStream())
            self.assertFalse(capture.finish())
        self.assertEqual(capture.snapshot()['capture_status'], 'READ_ERROR')
        self.assertEqual(error.getvalue(), '')

    def test_observer_distinguishes_dead_before_cleanup_and_normal_cleanup_intent(self):
        capture = ServerLogCapture()
        lifecycle = PhpLifecycle(capture, clock=lambda: 1)
        process = MagicMock()
        process.poll.return_value = 37
        lifecycle.process = process
        lifecycle.phase = 'FAILURE'
        output = io.StringIO()
        with redirect_stdout(output):
            lifecycle.observe('GATE_FAILED', 'UPSTREAM_DISCONNECTED')
            lifecycle.observe('BEFORE_CLEANUP')
            lifecycle.phase = 'CLEANUP'
            lifecycle.shutdown = 'ALREADY_EXITED'
            lifecycle.observe('CLEANUP_COMPLETE')
        r = records(output.getvalue())
        self.assertEqual([x['sequence'] for x in r], [1, 2, 3])
        self.assertEqual(r[0]['exit_code'], 37)
        self.assertEqual(r[0]['process_state'], 'EXITED')
        self.assertEqual(r[0]['shutdown'], 'NONE_REQUESTED')
        self.assertEqual(r[-1]['shutdown'], 'ALREADY_EXITED')
        process.terminate.assert_not_called()

    def test_alive_disconnect_does_not_invent_exit_or_fatal_error(self):
        lifecycle = PhpLifecycle(ServerLogCapture())
        lifecycle.process = MagicMock()
        lifecycle.process.poll.return_value = None
        lifecycle.phase = 'REQUEST'
        output = io.StringIO()
        with redirect_stdout(output):
            lifecycle.observe('PROXY_FAILURE', 'UPSTREAM_DISCONNECTED')
        r = records(output.getvalue())[0]
        self.assertEqual(r['process_state'], 'ALIVE')
        self.assertIsNone(r['exit_code'])
        self.assertEqual(r['error_categories'], [])
        self.assertEqual(r['capture_scope'], 'PROCESS_CUMULATIVE_ASYNCHRONOUS_BEST_EFFORT')

    def test_invalid_categories_and_event_flood_never_leak_arbitrary_values(self):
        lifecycle = PhpLifecycle(ServerLogCapture(), clock=lambda: 1)
        output = io.StringIO()
        with redirect_stdout(output):
            for event, reason in [('synthetic-private', 'NONE'), ('PROXY_FAILURE', 'synthetic-private')]:
                with self.assertRaises(ValueError):
                    lifecycle.observe(event, reason)
            for _ in range(140):
                lifecycle.observe('PROXY_FAILURE', 'UPSTREAM_DISCONNECTED')
        r = records(output.getvalue())
        self.assertEqual(len(r), 96)
        self.assertTrue(r[-1]['event_limit_reached'])
        self.assertNotIn('synthetic-private', output.getvalue())

    def test_proxy_error_flood_cannot_hide_failure_and_cleanup_checkpoints(self):
        lifecycle = PhpLifecycle(ServerLogCapture(), clock=lambda: 1)
        output = io.StringIO()
        with redirect_stdout(output):
            for _ in range(140):
                lifecycle.observe('PROXY_FAILURE', 'UPSTREAM_CONNECTION_ERROR')
            lifecycle.phase = 'FAILURE'
            lifecycle.observe('GATE_FAILED')
            lifecycle.observe('BEFORE_CLEANUP')
        r = records(output.getvalue())
        self.assertEqual([x['event'] for x in r[-2:]], ['GATE_FAILED', 'BEFORE_CLEANUP'])
        self.assertLessEqual(len(r), 128)
        self.assertEqual(r[-1]['proxy_events_suppressed'], 44)

    def test_real_php_fatal_and_uncaught_are_classified_even_with_error_logging_disabled(self):
        for code, category in [("trigger_error('synthetic-private', E_USER_ERROR);", 'USER_ERROR'),
                               ('undefined_lifecycle_fixture();', 'FATAL_ERROR')]:
            with self.subTest(category=category):
                process = spawn('require $argv[1]; vgLiveRegisterShutdownDiagnostics(); '+code, str(HOOK))
                capture = ServerLogCapture()
                capture.start(process.stdout)
                try:
                    self.assertNotEqual(process.wait(timeout=5), 0)
                    self.assertTrue(capture.finish())
                    self.assertIn(category, capture.snapshot()['error_categories'])
                    self.assertEqual(capture.snapshot()['request_shutdown'], category)
                    self.assertNotIn('synthetic-private', json.dumps(capture.snapshot()))
                finally:
                    if process.poll() is None:
                        process.kill(); process.wait(timeout=5)
                    capture.finish()

    def test_real_php_startup_exit_before_readiness_is_not_cleanup_termination(self):
        process = spawn('exit(7);')
        capture = ServerLogCapture(); capture.start(process.stdout)
        try:
            self.assertEqual(process.wait(timeout=5), 7)
            self.assertTrue(capture.finish())
            lifecycle = PhpLifecycle(capture); lifecycle.process = process; lifecycle.phase = 'READINESS'
            output = io.StringIO()
            with redirect_stdout(output):
                lifecycle.observe('READINESS_FAILED')
            r = records(output.getvalue())[0]
            self.assertEqual((r['process_state'], r['exit_code'], r['shutdown']), ('EXITED', 7, 'NONE_REQUESTED'))
        finally:
            if process.poll() is None:
                process.kill(); process.wait(timeout=5)
            capture.finish()

    def test_real_php_large_stderr_is_drained_and_normal_cleanup_keeps_distinct_order(self):
        process = spawn('fwrite(STDERR,str_repeat("x",2097152)."\nVG_LIVE_STAGE=ROWS_ADMITTED\n"); fgets(STDIN);', stdin=subprocess.PIPE)
        capture = ServerLogCapture(); capture.start(process.stdout)
        lifecycle = PhpLifecycle(capture); lifecycle.process = process; lifecycle.phase = 'REQUEST'
        output = io.StringIO()
        try:
            until = time.monotonic()+5
            while 'ROWS_ADMITTED' not in capture.snapshot()['observed_stages'] and time.monotonic() < until:
                time.sleep(0.005)
            self.assertIn('ROWS_ADMITTED', capture.snapshot()['observed_stages'])
            self.assertIsNone(process.poll())
            with redirect_stdout(output):
                lifecycle.observe('BEFORE_CLEANUP')
                lifecycle.phase = 'CLEANUP'; lifecycle.shutdown = 'TERMINATE_REQUESTED'
                lifecycle.observe('CLEANUP_TERMINATE')
                process.terminate(); process.wait(timeout=5)
                self.assertTrue(capture.finish())
                lifecycle.observe('CLEANUP_COMPLETE')
            r = records(output.getvalue())
            self.assertEqual([x['event'] for x in r], ['BEFORE_CLEANUP', 'CLEANUP_TERMINATE', 'CLEANUP_COMPLETE'])
            self.assertEqual(r[0]['process_state'], 'ALIVE')
            self.assertEqual(r[0]['shutdown'], 'NONE_REQUESTED')
            self.assertEqual(r[-1]['process_state'], 'EXITED')
            self.assertEqual(r[-1]['shutdown'], 'TERMINATE_REQUESTED')
            self.assertTrue(capture.snapshot()['log_line_truncated'])
            self.assertLessEqual(len(capture.pending), 4096)
        finally:
            if process.poll() is None:
                process.kill(); process.wait(timeout=5)
            process.stdin.close(); capture.finish()

    def php_socket_disconnect(self, action, stays_alive=False):
        with tempfile.TemporaryDirectory(prefix='vg-lifecycle-fixture-') as folder:
            ready = Path(folder)/'ready'
            with socket.socket() as reserved:
                reserved.bind(('127.0.0.1', 0)); port = reserved.getsockname()[1]
            code = ('require $argv[3]; vgLiveRegisterShutdownDiagnostics(); '
                    '$s=stream_socket_server("tcp://127.0.0.1:".$argv[1]); '
                    'if(!$s){exit(9);} file_put_contents($argv[2],"READY"); '
                    '$c=stream_socket_accept($s,5); if(!$c){exit(10);} fread($c,8192); '+action)
            process = spawn(code, str(port), str(ready), str(HOOK), stdin=subprocess.PIPE)
            capture = ServerLogCapture(); capture.start(process.stdout)
            lifecycle = PhpLifecycle(capture); lifecycle.process = process; lifecycle.phase = 'REQUEST'
            proxy = gate.LoopbackTLSProxy(('127.0.0.1', 0), gate.ProxyHandler)
            proxy.backend_port = port; proxy.relay_error_categories = set(); proxy.php_lifecycle = lifecycle
            thread = threading.Thread(target=proxy.serve_forever, kwargs={'poll_interval': 0.01}); thread.start()
            client = http.client.HTTPConnection('127.0.0.1', proxy.server_port, timeout=3)
            output = io.StringIO()
            try:
                until = time.monotonic()+5
                while not ready.exists() and process.poll() is None and time.monotonic() < until:
                    time.sleep(0.005)
                self.assertTrue(ready.exists())
                with redirect_stdout(output):
                    client.request('GET', '/owned-fixture')
                    response = client.getresponse(); response.read(gate.MAX_REPLY+1)
                    self.assertEqual(response.status, 502)
                    if stays_alive:
                        self.assertIsNone(process.poll())
                    else:
                        process.wait(timeout=5); capture.finish()
                    lifecycle.observe('GATE_FAILED', 'UPSTREAM_DISCONNECTED')
                r = records(output.getvalue())
                self.assertEqual(r[0]['event'], 'PROXY_FAILURE')
                self.assertEqual(r[0]['connection'], 'UPSTREAM_DISCONNECTED')
                self.assertEqual(r[-1]['shutdown'], 'NONE_REQUESTED')
                self.assertNotIn('synthetic-private', output.getvalue())
                return r[-1], capture.snapshot()
            finally:
                client.close(); proxy.shutdown(); proxy.server_close(); thread.join(timeout=3)
                if process.poll() is None:
                    process.stdin.write(b'\n'); process.stdin.flush()
                    process.wait(timeout=5)
                process.stdin.close(); capture.finish()
                self.assertFalse(thread.is_alive())

    def test_real_php_exit_before_header(self):
        r, _ = self.php_socket_disconnect('exit(37);')
        self.assertEqual((r['process_state'], r['exit_code']), ('EXITED', 37))

    def test_real_php_fatal_during_request_before_header(self):
        r, capture = self.php_socket_disconnect('undefined_lifecycle_fixture();')
        self.assertEqual(r['process_state'], 'EXITED')
        self.assertNotEqual(r['exit_code'], 0)
        self.assertIn('FATAL_ERROR', capture['error_categories'])

    def test_real_php_connection_closed_while_process_remains_alive(self):
        r, _ = self.php_socket_disconnect('fclose($c); fgets(STDIN);', stays_alive=True)
        self.assertEqual(r['process_state'], 'ALIVE')
        self.assertIsNone(r['exit_code'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
