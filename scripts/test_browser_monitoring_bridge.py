"""Browser admission/secret-output lifecycle units; no GUI or database execution."""
from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import browser_monitoring_bridge as bridge
import run_live_http_integration as gate


class BrowserBridgeTest(unittest.TestCase):
    def test_environment_refuses_node_certificate_and_code_injection_overrides(self):
        for name in ('NODE_OPTIONS', 'NODE_TLS_REJECT_UNAUTHORIZED'):
            with self.assertRaises(RuntimeError):
                bridge.environment({name:'synthetic'}, 'synthetic-browser')

    def test_child_environment_does_not_inherit_application_or_db_secrets(self):
        sentinel=object()
        env=bridge.environment({'APP_KEY':sentinel,'DB_PASSWORD':sentinel, 'PATH':'owned','SYSTEMROOT':'owned'}, 'synthetic-browser')
        self.assertEqual(set(env), {'PATH','SYSTEMROOT','VG_BROWSER_BINARY'})

    def test_prerequisite_requires_exact_quiet_success_and_never_launches_browser_directly(self):
        for result in [subprocess.CompletedProcess([],3,b'',b''),subprocess.CompletedProcess([],0,b'OTHER',b''),
                       subprocess.CompletedProcess([],0,b'BROWSER_PREREQUISITE=PASS_NO_LAUNCH',b'unreviewed diagnostic')]:
            with patch.object(bridge.subprocess,'run',return_value=result) as run, self.assertRaises(RuntimeError):
                bridge.preflight('node','synthetic-browser',{})
            self.assertEqual(run.call_args.args[0][-1],'--check')

    def test_unowned_root_refused_before_seed_or_subprocess(self):
        with tempfile.TemporaryDirectory(prefix='vg-foreign-browser-') as folder:
            with patch.object(bridge.subprocess,'run') as run, self.assertRaises(RuntimeError):
                bridge.execute('node','synthetic',{},Path(folder).resolve(),{},b'{}','https://127.0.0.1:1234')
            run.assert_not_called();self.assertFalse(list(Path(folder).iterdir()))

    def test_invalid_upstream_refused_even_for_owned_root(self):
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as folder:
            with patch.object(bridge.subprocess,'run') as run, self.assertRaises(RuntimeError):
                bridge.execute('node','synthetic',{},Path(folder).resolve(),{},b'{}','http://127.0.0.1:1234')
            run.assert_not_called()

    def test_preexisting_seed_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as folder:
            seed=Path(folder)/'browser-native-seed.jsonl';seed.write_bytes(b'keep')
            with patch.object(bridge.subprocess,'run') as run, self.assertRaises(RuntimeError):
                bridge.execute('node','synthetic',{},Path(folder).resolve(),{},b'{}','https://127.0.0.1:1234')
            run.assert_not_called();self.assertEqual(seed.read_bytes(),b'keep')

    def test_browser_missing_binary_never_boots_php_or_creates_fixtures(self):
        with patch('sys.argv',['gate','--php-binary','synthetic','--browser-only','--execute']), patch.object(gate,'php_run') as php, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(gate.main(),3)
        php.assert_not_called();self.assertIn('BROWSER_BINARY_REQUIRED_NO_FIXTURES',output.getvalue())

    def test_node_preflight_rejection_precedes_database_check(self):
        with patch('sys.argv',['gate','--php-binary','synthetic','--browser-only','--browser-binary','synthetic','--execute']), patch.object(bridge,'preflight',side_effect=RuntimeError()), patch.object(gate,'php_run') as php, redirect_stdout(io.StringIO()):
            self.assertEqual(gate.main(),3)
        php.assert_not_called()


if __name__=='__main__':
    unittest.main()
