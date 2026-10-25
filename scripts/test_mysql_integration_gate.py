#!/usr/bin/env python3
"""Exercise runner refusal/ordering without connecting to a database."""
from contextlib import redirect_stdout
import io
import base64
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest.mock import patch

import run_mysql_integration as gate


class RunnerSafetyTest(unittest.TestCase):
    def invoke(self, args, results):
        stream = io.StringIO()
        with patch.object(sys, 'argv', ['gate', *args]), patch.object(gate, 'run', side_effect=results) as calls:
            with redirect_stdout(stream):
                status = gate.main()
        return status, calls.call_args_list, stream.getvalue()

    @staticmethod
    def result(code=0, stdout='', stderr=''):
        return subprocess.CompletedProcess([], code, stdout, stderr)

    def test_failed_preflight_never_builds_fixtures_or_migrates_even_when_execute_requested(self):
        status, calls, output = self.invoke(['--execute', '--migration-roundtrip'], [self.result(3)])
        self.assertEqual(status, 3)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].args[0][-1], '--check')
        self.assertIn('NO_MIGRATIONS_NO_TEST_FIXTURES', output)

    def test_default_mode_is_read_only(self):
        status, calls, output = self.invoke([], [self.result(0, 'MYSQL_TEST_PREFLIGHT=PASS\n')])
        self.assertEqual(status, 0)
        self.assertEqual(len(calls), 1)
        self.assertIn('NOT_RUN_READ_ONLY_MODE', output)

    def test_testing_file_requires_explicit_opt_in_flag_in_clean_process(self):
        with patch.dict(os.environ, {}, clear=True):
            status, calls, _ = self.invoke(['--testing-env'], [self.result()])
            self.assertEqual(status, 0)
            self.assertEqual(calls[0].args[1]['VG_USE_TESTING_ENV'], '1')
            _, calls, _ = self.invoke([], [self.result()])
            self.assertNotIn('VG_USE_TESTING_ENV', calls[0].args[1])

    def test_explicit_php_binary_is_used_and_test_key_is_generated_per_process(self):
        target='C:/tools/php-8.2.35/php.exe'
        _, calls, _=self.invoke(['--php-binary',target],[self.result()])
        self.assertEqual(calls[0].args[0][0],target)
        first=calls[0].args[1]['APP_KEY']
        _, calls, _=self.invoke(['--php-binary',target],[self.result()])
        self.assertNotEqual(first,calls[0].args[1]['APP_KEY'])

    def test_missing_explicit_php_binary_does_not_fall_back(self):
        status,calls,_=self.invoke(['--php-binary','missing-explicit-php'],[FileNotFoundError()])
        self.assertEqual(status,3)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0].args[0][0],'missing-explicit-php')

    def test_ci_key_generator_is_executable_ephemeral_and_loopback_is_required(self):
        source=(gate.ROOT/'.github/workflows/phase9-multi-context-ci.yml').read_text()
        self.assertIn("ports: ['127.0.0.1:3306:3306']",source)
        code=textwrap.dedent(source.split("python3 - <<'PY'\n",1)[1].split('\n          PY',1)[0])
        keys=[]
        with tempfile.TemporaryDirectory(prefix='vg-ci-key-') as folder:
            for i in range(2):
                target=Path(folder)/str(i)
                with patch.dict(os.environ,{'GITHUB_ENV':str(target)}), redirect_stdout(io.StringIO()):
                    exec(compile(code,'ci-key-generator','exec'),{})
                name,value=target.read_text().strip().split('=',1)
                self.assertEqual(name,'APP_KEY')
                self.assertTrue(value.startswith('base64:'))
                self.assertTrue(len(base64.b64decode(value[7:],validate=True))==32)
                keys.append(value)
        self.assertTrue(keys[0]!=keys[1])

    def test_existing_schema_mode_uses_inspection_without_migration_reset(self):
        xml='<testsuites><testcase name="executed_case"/></testsuites>'
        status,calls,output=self.invoke(['--execute','--existing-schema'],self.report_result(xml))
        self.assertEqual(status,0)
        self.assertEqual(calls[0].args[0][-1],'--inspect')
        self.assertEqual(len(calls),8)
        self.assertNotIn('--migrate',[x for call in calls for x in call.args[0]])
        self.assertIn('NOT_RUN_EXISTING_SCHEMA_MODE',output)

    def test_existing_schema_roundtrip_requires_verified_mode(self):
        status,calls,_=self.invoke(['--execute','--existing-schema','--migration-roundtrip'],
                                  [self.result(),self.result(),self.result(),self.result(),self.result(),self.result(),self.result(3)])
        self.assertEqual(status,3)
        self.assertEqual(calls[0].args[0][-1],'--inspect')
        self.assertEqual(calls[6].args[0][-1],'--roundtrip-existing')

    def test_missing_c99_tool_blocks_before_schema_mutation(self):
        status, calls, output = self.invoke(['--execute'], [self.result(), self.result(1)])
        self.assertEqual(status, 3)
        self.assertEqual(len(calls), 2)
        self.assertIn('BLOCKED_C99_FIXTURE_BUILD_NO_MIGRATIONS', output)

    def test_second_fixture_failure_also_blocks_before_migration(self):
        status, calls, _ = self.invoke(['--execute'], [self.result(), self.result(), self.result(1)])
        self.assertEqual(status, 3)
        self.assertEqual(len(calls), 3)

    def test_runtime_fixture_failure_also_blocks_before_migration(self):
        status, calls, output = self.invoke(['--execute'], [self.result(), self.result(), self.result(), self.result(1)])
        self.assertEqual(status, 3)
        self.assertEqual(len(calls), 4)
        self.assertEqual(calls[3].args[0][2], 'scripts/runtime_uplink_wire_bridge.py')
        self.assertIn('BLOCKED_C99_FIXTURE_BUILD_NO_MIGRATIONS', output)

    def test_continuous_fixture_failure_blocks_before_migration(self):
        status, calls, output = self.invoke(['--execute'], [self.result()] * 4 + [self.result(1)])
        self.assertEqual(status, 3)
        self.assertEqual(len(calls), 5)
        self.assertEqual(calls[4].args[0][2], 'scripts/continuous_simulation_wire_bridge.py')
        self.assertIn('BLOCKED_C99_FIXTURE_BUILD_NO_MIGRATIONS', output)

    def test_alarm_metadata_fixture_failure_blocks_before_migration(self):
        status, calls, output = self.invoke(['--execute'], [self.result()] * 5 + [self.result(1)])
        self.assertEqual(status, 3)
        self.assertEqual(len(calls), 6)
        self.assertEqual(calls[5].args[0][2], 'scripts/alarm_metadata_wire_bridge.py')
        self.assertIn('BLOCKED_C99_FIXTURE_BUILD_NO_MIGRATIONS', output)

    def test_previous_upgrade_uses_exact_previous_inspection_and_explicit_roundtrip(self):
        status, calls, _ = self.invoke(['--execute', '--existing-schema', '--upgrade-previous', '--migration-roundtrip'],
                                     [self.result()] * 6 + [self.result(3)])
        self.assertEqual(status, 3)
        self.assertEqual(calls[0].args[0][-1], '--inspect-previous')
        self.assertEqual(calls[6].args[0][-1], '--upgrade-previous-roundtrip')
        self.assertEqual(len(calls), 7)

    def test_previous_upgrade_cannot_imply_execution_or_missing_existing_schema(self):
        for args in (['--upgrade-previous'], ['--execute', '--upgrade-previous']):
            with patch.object(sys, 'argv', ['gate', *args]), patch.object(gate, 'run') as command, self.assertRaises(SystemExit):
                gate.main()
            command.assert_not_called()

    def test_migration_failure_blocks_phpunit(self):
        status, calls, output = self.invoke(['--execute', '--migration-roundtrip'],
            [self.result(), self.result(), self.result(), self.result(), self.result(), self.result(), self.result(3)])
        self.assertEqual(status, 3)
        self.assertEqual(len(calls), 7)
        self.assertEqual(calls[-1].args[0][-1], '--migration-roundtrip')
        self.assertIn('BLOCKED_MIGRATION_GATE', output)

    def test_test_failure_blocks_receipt_crosscheck_and_does_not_echo_bindings(self):
        status, calls, output = self.invoke(['--execute'],
            [self.result(), self.result(), self.result(), self.result(), self.result(), self.result(), self.result(),
             self.result(1, 'synthetic-sensitive-marker', 'synthetic-sensitive-marker')])
        self.assertEqual(status, 1)
        self.assertEqual(len(calls), 8)
        self.assertEqual(calls[6].args[0][-1], '--migrate')
        self.assertNotIn('synthetic-sensitive-marker', output)

    def test_missing_junit_report_cannot_be_pass(self):
        status, calls, output = self.invoke(['--execute'], [self.result()] * 8)
        self.assertEqual(status, 3)
        self.assertEqual(len(calls), 8)
        self.assertIn('BLOCKED_MISSING_REPORT', output)

    def test_timeout_is_blocked(self):
        status, _, output = self.invoke([], [subprocess.TimeoutExpired('php', 1)])
        self.assertEqual(status, 3)
        self.assertIn('BLOCKED_TOOL_OR_TIMEOUT', output)

    def report_result(self, xml, crosscheck_code=0):
        def execute(command, env, cwd=gate.ROOT):
            if '--log-junit' in command:
                Path(command[command.index('--log-junit') + 1]).write_text(xml)
            return self.result(crosscheck_code if 'scripts/phase9_b17_receipt_crosscheck.py' in command else 0)
        return execute

    def test_skipped_empty_or_malformed_reports_cannot_be_pass(self):
        for xml in ('<testsuites/>', '<testsuites><testcase><skipped/></testcase></testsuites>', '<bad'):
            status, calls, _ = self.invoke(['--execute'], self.report_result(xml))
            self.assertEqual(status, 3)
            self.assertEqual(len(calls), 8)

    def test_junit_failure_blocks_even_if_subprocess_claims_success(self):
        status, calls, output = self.invoke(['--execute'], self.report_result(
            '<testsuites><testcase name="failure_case"><failure>synthetic-sensitive-marker</failure></testcase></testsuites>'))
        self.assertEqual(status, 1)
        self.assertEqual(len(calls), 8)
        self.assertNotIn('synthetic-sensitive-marker', output)

    def test_success_requires_migrations_phpunit_and_receipt_crosscheck(self):
        status, calls, output = self.invoke(['--execute'], self.report_result(
            '<testsuites><testcase name="executed_case"/></testsuites>'))
        self.assertEqual(status, 0)
        self.assertEqual(len(calls), 9)
        self.assertIn('MYSQL_HTTP_ACK_CROSSCHECK=PASS', output)

    def test_failed_receipt_crosscheck_fails_batch(self):
        status, calls, output = self.invoke(['--execute'], self.report_result(
            '<testsuites><testcase name="executed_case"/></testsuites>', 1))
        self.assertEqual(status, 1)
        self.assertEqual(len(calls), 9)
        self.assertIn('MYSQL_HTTP_ACK_CROSSCHECK=FAIL', output)

    def test_real_php_guard_denies_missing_environment_without_dotenv_fallback(self):
        env = {key: value for key, value in os.environ.items()
               if key.upper() in {'PATH', 'SYSTEMROOT', 'TEMP', 'TMP', 'WINDIR'}}
        cp = subprocess.run([os.environ.get('VG_PHP_CLI', 'php'), str(gate.ROOT / 'scripts/mysql_test_gate.php'), '--check'],
                            cwd=gate.ROOT, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(cp.returncode, 3)
        self.assertIn('explicit isolated test configuration required', cp.stderr)
        self.assertNotIn('MYSQL_TEST_PREFLIGHT=PASS', cp.stdout)

    def test_all_database_tests_use_guard_and_transactions_instead_of_schema_reset(self):
        folder = gate.ROOT / 'backend/laravel/tests/Feature'
        names = [path.name for path in folder.glob('*.php')
                 if 'extends MySqlTestCase' in path.read_text(encoding='utf-8')]
        self.assertGreaterEqual(len(names), 4)
        self.assertIn('RuntimeUplinkIntegrationTest.php', names)
        for name in names:
            source = (folder / name).read_text(encoding='utf-8')
            self.assertIn('extends MySqlTestCase', source)
            self.assertRegex(source, r'\buse\s+DatabaseTransactions(?:\s*[,;])')
            self.assertNotIn('RefreshDatabase', source)

        integration = (folder / 'FirmwareMySqlIntegrationTest.php').read_text(encoding='utf-8')
        self.assertNotIn('Mockery', integration)
        self.assertNotIn('mock(', integration)


if __name__ == '__main__':
    unittest.main()
