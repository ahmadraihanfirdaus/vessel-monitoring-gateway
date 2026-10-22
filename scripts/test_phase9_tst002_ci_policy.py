#!/usr/bin/env python3
"""TST-002 workflow source-policy tests, NOT hosted CI execution evidence."""
import unittest
from pathlib import Path
F=Path(__file__).resolve().parents[1]/'.github/workflows/phase9-multi-context-ci.yml'
class WorkflowSourceTests(unittest.TestCase):
    def test_pr_trigger_and_two_jobs(self):
        s=F.read_text();self.assertIn('pull_request:',s)
        self.assertIn('firmware-host:',s);self.assertIn('backend-mysql-isolated:',s)
    def test_build_and_backend_tests(self):
        s=F.read_text()
        for v in ('test_firmware_core_host.py','test_phase9_net001_host_adapter.py','test_phase9_sys003_local_guard.py','php artisan test'):
            self.assertIn(v,s)
    def test_ephemeral_mysql_only(self):
        s=F.read_text()
        for v in ('MYSQL_DATABASE: vessel_gateway_ci','DB_CONNECTION: mysql','php artisan migrate --force','APP_ENV: testing'):
            self.assertIn(v,s)
        self.assertNotIn('sqlite',s.lower())
    def test_no_secret_embedded_or_push_event(self):
        s=F.read_text();self.assertNotIn('  push:',s)
        self.assertNotIn('production',s.lower())
        self.assertNotIn('DB_HOST: production',s)
if __name__=='__main__':unittest.main()
