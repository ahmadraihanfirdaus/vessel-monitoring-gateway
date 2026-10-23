#!/usr/bin/env python3
"""B10 scoped CI registration check; no DB calls."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Workflow(unittest.TestCase):
    def test_b10_job_is_isolated_and_registered(self):
        s=(ROOT/'.github/workflows/phase9-multi-context-ci.yml').read_text()
        self.assertIn('backend-http-no-db-b9:',s)
        self.assertIn('Phase9B9HttpBoundaryTest',s)
        self.assertIn('Phase9B10HttpResilienceTest',s)
        self.assertIn('test_phase9_b10_contract.py',s)
        self.assertNotIn('  push:',s)
    def test_trace_is_scoped_and_formal_open(self):
        s=(ROOT/'docs/testing/phase9-b10-scoped-trace.csv').read_text()
        for identifier in ('API-001','SEC-002','SYS-003','UI-002','TST-001','TST-002'):
            self.assertIn(identifier,s)
        self.assertIn('FORMAL_OPEN',s)
if __name__=='__main__':unittest.main(verbosity=2)
