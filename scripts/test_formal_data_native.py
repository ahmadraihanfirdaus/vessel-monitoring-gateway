"""Fail-closed native orchestrator tests, independent of actual evidence."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import run_formal_data_native as gate


class NativeGateTest(unittest.TestCase):
    def invoke(self, args):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['native-test', *args]), redirect_stdout(output):
            code = gate.main()
        return code, output.getvalue()

    def test_default_does_not_hash_compile_or_boot_anything(self):
        with patch.object(gate, 'source_snapshot') as snapshot, patch.object(gate, 'build_bytes') as builder:
            code, output = self.invoke([])
        self.assertEqual(code, 0); self.assertIn('NOT_RUN_READ_ONLY', output)
        snapshot.assert_not_called(); builder.assert_not_called()

    def test_missing_or_unreviewed_protocol_blocks_before_compiler(self):
        for fault in ('', OSError('synthetic'), UnicodeError('synthetic')):
            with patch.object(gate, 'source_snapshot', return_value={}), \
                 patch.object(Path, 'read_text', **({'side_effect': fault} if isinstance(fault, Exception) else {'return_value': fault})), \
                 patch.object(gate, 'build_bytes') as builder:
                code, output = self.invoke(['--execute'])
            self.assertEqual(code, 3); self.assertIn('BLOCKED_', output)
            builder.assert_not_called()

    def test_native_failure_and_source_drift_never_pass(self):
        with patch.object(gate, 'build_bytes', side_effect=AssertionError('synthetic')):
            code, output = self.invoke(['--execute'])
        self.assertEqual(code, 1); self.assertIn('FAIL_CONTRACT', output)
        with patch.object(gate, 'source_snapshot', side_effect=[{}, {'changed':'x'}]), \
             patch.object(gate, 'build_bytes', return_value=b'x'), \
             patch.object(gate, 'domain_bytes', return_value=b'x'), \
             patch.object(gate, 'native_contract', return_value={'valid_zero':1,'unavailable':1}):
            code, output = self.invoke(['--execute'])
        self.assertEqual(code, 1); self.assertNotIn('DATA_NATIVE_RECORD=', output)


if __name__ == '__main__':
    unittest.main()
