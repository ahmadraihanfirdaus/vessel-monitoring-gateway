"""Causality contracts, actual local PHP exit and redaction; no Linux/debugger PASS claim."""
from contextlib import redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import MagicMock

from php_native_causality import native_state, finish_failed_upstream
from php_lifecycle_diagnostics import PhpLifecycle, ServerLogCapture, valid_runtime
from test_php_lifecycle_diagnostics import spawn


class NativeCausalityTest(unittest.TestCase):
    def run_cleanup(self, initial, waits, after, times=(0,0,5)):
        process = MagicMock(pid=123)
        process.poll.return_value = initial
        lifecycle = PhpLifecycle(ServerLogCapture()); lifecycle.process = process; lifecycle.phase = 'CLEANUP'
        calls = []
        def wait(timeout):
            calls.append(timeout)
            action = waits[len(calls)-1]
            if action == 'TIMEOUT':
                raise subprocess.TimeoutExpired('withheld', timeout)
            process.poll.return_value = action
            return action
        process.wait.side_effect = wait
        process.terminate.side_effect = lambda: setattr(process.poll, 'return_value', after)
        clock = iter(times)
        output = io.StringIO()
        with redirect_stdout(output):
            finish_failed_upstream(process, lifecycle, clock=lambda: next(clock))
        return process, lifecycle, calls, output.getvalue()

    def test_already_exited_signal_is_observed_without_any_termination_request(self):
        process, life, calls, output = self.run_cleanup(-11, [], None)
        self.assertEqual(life.native_outcome, 'SIGNAL_EXIT_BEFORE_TERMINATE')
        self.assertEqual(calls, [])
        process.terminate.assert_not_called(); process.kill.assert_not_called()
        self.assertIn('EXIT_BEFORE_TERMINATE', output)

    def test_passive_natural_signal_does_not_get_misattributed_to_cleanup(self):
        process, life, calls, _ = self.run_cleanup(None, [-11], None)
        self.assertEqual(calls, [5])
        self.assertEqual(life.native_outcome, 'SIGNAL_EXIT_BEFORE_TERMINATE')
        process.terminate.assert_not_called(); process.kill.assert_not_called()

    def test_post_terminate_segv_remains_causally_unresolved(self):
        process, life, calls, output = self.run_cleanup(None, ['TIMEOUT',-11], -11)
        self.assertEqual(calls, [5,5])  # Shared10s budget, not an extra timeout.
        self.assertEqual(life.native_outcome, 'SIGNAL_AFTER_TERMINATE_CAUSE_UNRESOLVED')
        process.terminate.assert_called_once(); process.kill.assert_not_called()
        self.assertIn('PASSIVE_WINDOW_EXPIRED', output)
        self.assertIn('PRE_TERMINATE', output)

    def test_normal_term_after_passive_window_has_separate_classification(self):
        process, life, calls, _ = self.run_cleanup(None, ['TIMEOUT',-15], -15)
        self.assertEqual(calls, [5,5])
        self.assertEqual(life.native_outcome, 'EXIT_AFTER_PASSIVE_WINDOW_AND_TERMINATE')
        process.terminate.assert_called_once(); process.kill.assert_not_called()

    def test_existing_force_kill_budget_is_retained_after_both_windows_expire(self):
        process, life, calls, _ = self.run_cleanup(None, ['TIMEOUT','TIMEOUT',-9], None)
        self.assertEqual(calls, [5,5,5])
        process.kill.assert_called_once()
        self.assertEqual(life.native_outcome, 'KILLED_AFTER_EXISTING_CLEANUP_BUDGET')

    def test_remaining_wait_accounts_for_elapsed_time_instead_of_extending_budget(self):
        _, _, calls, _ = self.run_cleanup(None, ['TIMEOUT',0], 0, times=(0,0,9))
        self.assertEqual(calls, [5,1])

    def test_metadata_overhead_cannot_add_time_to_the_existing_cleanup_budget(self):
        _, _, calls, _ = self.run_cleanup(None, ['TIMEOUT',0], 0, times=(0,9,10))
        self.assertEqual(calls, [1,0])

    def test_real_php_exit37_is_reaped_without_sending_cleanup_signal(self):
        process = spawn('exit(37);')
        capture = ServerLogCapture(); capture.start(process.stdout)
        life = PhpLifecycle(capture); life.process = process; life.phase = 'CLEANUP'
        try:
            with redirect_stdout(io.StringIO()):
                finish_failed_upstream(process, life)
            self.assertEqual(process.poll(), 37)
            self.assertEqual(life.shutdown, 'ALREADY_EXITED')
            self.assertEqual(life.native_outcome, 'EXIT_BEFORE_TERMINATE')
            self.assertTrue(capture.finish())
        finally:
            if process.poll() is None:
                process.kill(); process.wait(timeout=5)
            capture.finish()

    def test_proc_selected_fields_never_retain_pid_uid_paths_or_arbitrary_values(self):
        raw=(b'Name:\tsynthetic-private\nUid:\t123\nState:\tD (synthetic-private)\nCoreDumping:\t1\n'
             b'SigPnd:\t0000000000000400\nShdPnd:\t0\nSigCgt:\t4000\nSigIgn:\t0\n')
        result=native_state(MagicMock(pid=123), platform='linux', reader=lambda _:raw)
        self.assertEqual(result['kernel_state'], 'DISK_WAIT')
        self.assertTrue(result['core_dumping']); self.assertTrue(result['segv_pending'])
        self.assertTrue(result['term_caught']); self.assertFalse(result['segv_caught'])
        self.assertNotIn('synthetic-private', json.dumps(result))
        self.assertNotIn('123', json.dumps(result))

    def test_proc_unavailable_oversize_and_non_linux_are_honest_and_bounded(self):
        def denied(_):raise PermissionError('synthetic-private')
        for reader in (denied, lambda _:b'x'*8193):
            result=native_state(MagicMock(pid=123), platform='linux', reader=reader)
            self.assertEqual(result['availability'], 'UNAVAILABLE')
            self.assertIsNone(result['core_dumping'])
        reader=MagicMock()
        self.assertEqual(native_state(MagicMock(pid=123), platform='win32', reader=reader)['availability'], 'NOT_SUPPORTED')
        reader.assert_not_called()

    def test_actual_php_runtime_fingerprint_and_log_collector_admit_only_safe_schema(self):
        helper=Path(__file__).resolve().parent/'live_http_runtime.php'
        process=spawn('require $argv[1]; echo json_encode(vgLiveRuntimeFingerprint());', str(helper))
        raw,_=process.communicate(timeout=5)
        self.assertEqual(process.returncode,0)
        data=json.loads(raw); self.assertTrue(valid_runtime(data)); self.assertEqual(data['sapi'],'CLI')
        capture=ServerLogCapture(); capture.feed(b'VG_PHP_RUNTIME='+raw+b'\n')
        self.assertEqual(capture.snapshot()['runtime'],data)
        for key,value in [('memory_limit','synthetic-private'),('sapi','synthetic-private'),('raw_error','synthetic-private')]:
            bad=copy.deepcopy(data);bad[key]=value
            self.assertFalse(valid_runtime(bad))
            capture=ServerLogCapture();capture.feed(b'VG_PHP_RUNTIME='+json.dumps(bad).encode()+b'\n')
            self.assertIsNone(capture.snapshot()['runtime'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
