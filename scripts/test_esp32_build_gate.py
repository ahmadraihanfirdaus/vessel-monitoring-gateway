"""Adversarial build-evidence tests in temporary directories; never build/upload."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import build_esp32_port as build


class BuildEvidenceTest(unittest.TestCase):
    def test_security_config_rejects_each_missing_guard_and_insecure_switch(self):
        required = ('MBEDTLS_CERTIFICATE_BUNDLE', 'MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL',
                    'COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE', 'MBEDTLS_HAVE_TIME_DATE',
                    'MBEDTLS_HAVE_TIME', 'ESP_HTTP_CLIENT_ENABLE_HTTPS')
        valid = ''.join('CONFIG_'+name+'=y\n' for name in required)
        self.assertTrue(build.security_config_valid(valid))
        for name in required:
            self.assertFalse(build.security_config_valid(valid.replace('CONFIG_'+name+'=y\n', '')))
        for name in ('ESP_TLS_INSECURE', 'ESP_TLS_SKIP_SERVER_CERT_VERIFY'):
            self.assertFalse(build.security_config_valid(valid+'CONFIG_'+name+'=y\n'))
        self.assertFalse(build.security_config_valid(valid.replace('CONFIG_MBEDTLS_HAVE_TIME_DATE=y', '# CONFIG_MBEDTLS_HAVE_TIME_DATE=y')))

    def test_successful_tool_exit_cannot_certify_mutated_inputs(self):
        with tempfile.TemporaryDirectory(prefix='vg-build-gate-') as folder:
            root = Path(folder)
            (root/'firmware/src').mkdir(parents=True)
            (root/'evidence/test-results').mkdir(parents=True)
            header = root/'firmware/src/test.h'
            header.write_bytes(b'#define SYNTHETIC 1\n')
            def mutate(*args, **kwargs):
                header.write_bytes(b'#define SYNTHETIC 2\n')
                return subprocess.CompletedProcess(args[0], 0, '[SUCCESS]\n', '')
            with patch.object(build, 'ROOT', root), patch.object(sys, 'argv', ['build', '--evidence-name', 'esp32-transport-sdk-build-test.txt']), patch.object(build.subprocess, 'run', side_effect=mutate) as command, redirect_stdout(io.StringIO()):
                self.assertEqual(build.main(), 1)
            self.assertEqual(command.call_count, 1)
            evidence = (root/'evidence/test-results/esp32-transport-sdk-build-test.txt').read_text()
            self.assertIn('FAIL_CHANGED_DURING_BUILD', evidence)
            self.assertNotIn('ESP32_SIM_MERGE=PASS', evidence)

    def test_existing_evidence_is_never_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='vg-build-gate-') as folder:
            root = Path(folder)
            (root/'evidence/test-results').mkdir(parents=True)
            evidence = root/'evidence/test-results/esp32-transport-sdk-build-test.txt'
            evidence.write_bytes(b'existing evidence\n')
            with patch.object(build, 'ROOT', root), patch.object(sys, 'argv', ['build', '--evidence-name', evidence.name]), patch.object(build.subprocess, 'run') as command, redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
                build.main()
            command.assert_not_called()
            self.assertEqual(evidence.read_bytes(), b'existing evidence\n')


if __name__ == '__main__':
    unittest.main()
