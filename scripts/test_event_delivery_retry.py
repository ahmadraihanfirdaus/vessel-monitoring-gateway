"""Native parent/current oracle and private one-shot fault admission units.

Injected unit outcomes are not real HTTP; the separate owned TLS gate executes
actual commit/response-loss/duplicate/receipt/file integration.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest

from phase9_b4_testlib import compile_c
import run_live_http_integration as gate

ROOT = Path(__file__).resolve().parents[1]
PARENT = '69c33710a0cf1aa1cd3ecfec4773b06a66bc0029'
PARENT_HEADER_SHA = 'f4d59dce4c8a7931a8df3da543d79abd4f4fbe8a8af30c8c4c094d839f7fdf45'


class DeliveryRetryTest(unittest.TestCase):
    def test_pinned_parent_reproduces_skipped_prefix_without_mutating_working_header(self):
        header = subprocess.check_output(['git', 'show', PARENT+':firmware/src/event_delivery.h'], cwd=ROOT)
        self.assertEqual(hashlib.sha256(header).hexdigest(), PARENT_HEADER_SHA)
        before = (ROOT/'firmware/src/event_delivery.h').read_bytes()
        with tempfile.TemporaryDirectory(prefix='vg-retry-reference-') as directory:
            folder = Path(directory).resolve()
            self.assertEqual(folder.parent, Path(tempfile.gettempdir()).resolve())
            self.assertTrue(folder.name.startswith('vg-retry-reference-'))
            self.assertFalse(folder.is_symlink())
            (folder/'event_delivery.h').write_bytes(header)
            observed = json.loads(compile_c((ROOT/'scripts/event_delivery_retry_fixture.c').read_text(encoding='utf-8'),
                                           extra_flags=('-I', str(folder))))
        self.assertEqual(observed['retained'], 2)
        self.assertEqual(observed['cursor'], 1)
        self.assertEqual(observed['head_event_id'], '1')
        self.assertEqual(observed['next_event_id'], '2')
        self.assertEqual((ROOT/'firmware/src/event_delivery.h').read_bytes(), before)

    def test_identical_current_composition_retries_unconfirmed_head_with_new_context_argument(self):
        source = (ROOT/'scripts/event_delivery_retry_fixture.c').read_text(encoding='utf-8')
        old = 'vg_delivery_receive_http(&owner, &failed)'
        self.assertEqual(source.count(old), 1)
        source = source.replace(old, 'vg_delivery_receive_http(&owner, &failed, &context)')
        observed = json.loads(compile_c(source))
        self.assertEqual(observed, dict(retained=2, metadata_retained=2, cursor=0,
            head_event_id='1', next_event_id='1', active_alarm=True, next_tag='2'))

    @staticmethod
    def server():
        # No socket/thread/listener created in these pure admission units.
        server = object.__new__(gate.LoopbackTLSProxy)
        server._reply_fault_lock = threading.Lock()
        server._reply_fault = None
        server.commit_reply_drops = 0
        return server

    def test_drop_requires_exact_owned_request_and_committed_status_then_consumes_once(self):
        server = self.server(); agent = 'vg-live/'+'a'*32
        server.arm_commit_reply_drop('/api/v1/events', agent, b'{}')
        cases = [('GET','/api/v1/events',agent,b'{}',201),
                 ('POST','/api/v1/telemetry',agent,b'{}',201),
                 ('POST','/api/v1/events','foreign',b'{}',201),
                 ('POST','/api/v1/events',agent,b'{ }',201)]
        cases += [('POST','/api/v1/events',agent,b'{}',status) for status in (0,301,401,409,422,503,201.0,True)]
        cases += [('POST','/api/v1/events',agent,'{}',201)]
        for case in cases:
            self.assertFalse(server.consume_commit_reply_drop(*case))
            self.assertEqual(server.commit_reply_drops, 0)
            self.assertIsNotNone(server._reply_fault)
        self.assertTrue(server.consume_commit_reply_drop('POST','/api/v1/events',agent,b'{}',201))
        self.assertFalse(server.consume_commit_reply_drop('POST','/api/v1/events',agent,b'{}',201))
        self.assertEqual(server.commit_reply_drops, 1)

    def test_foreign_path_agent_empty_oversized_or_nonbytes_body_cannot_arm_or_replace_fault(self):
        server = self.server(); agent = 'vg-live/'+'a'*32
        for path, ua, body in [('/api/v1/telemetry',agent,b'{}'),('/api/v1/events','foreign',b'{}'),
                              ('/api/v1/events',None,b'{}'),
                              ('/api/v1/events',agent,b''),('/api/v1/events',agent,b'x'*8193),
                              ('/api/v1/events',agent,'{}')]:
            with self.assertRaises(gate.GateFailure): server.arm_commit_reply_drop(path, ua, body)
            self.assertIsNone(server._reply_fault)
        server.arm_commit_reply_drop('/api/v1/events',agent,b'{}')
        old = server._reply_fault
        with self.assertRaises(gate.GateFailure): server.arm_commit_reply_drop('/api/v1/events',agent,b'new')
        self.assertEqual(server._reply_fault, old)
        self.assertEqual(server.commit_reply_drops, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
