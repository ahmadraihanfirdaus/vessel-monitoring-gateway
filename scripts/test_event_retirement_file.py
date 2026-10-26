"""Actual host files/standard independent HMAC/continuous facts/shared owner."""
import hashlib
import hmac
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from event_receipt_native_bridge import build_retirement_fixture, run_retirement


class RetirementFileTest(unittest.TestCase):
    def test_actual_loss_retry_and_duplicate_status200_retire_with_same_owner_next_tag(self):
        env = os.environ.copy()
        env['VG_LIVE_DEVICE_TOKEN'] = 'public-synthetic-host-test-input-key-123456789'
        def sign(body, status):
            digest = hashlib.sha256(body).hexdigest()
            mac = hmac.new(env['VG_LIVE_DEVICE_TOKEN'].encode(),
                           ('VG_EVENT_COMMIT_V1\n'+str(status)+'\n'+digest).encode(), hashlib.sha256).hexdigest()
            return ('VGR1:'+digest+':'+mac).encode()
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as root:
            binary = build_retirement_fixture(Path(root).resolve(), env)
            identity = 'c'*32
            old = run_retirement(binary, env, 'prepare', identity)
            current = run_retirement(binary, env, 'old', identity, old, 201, sign(old, 201))
            paths = [binary.parent/('receipt-slot'+str(i)+'.bin') for i in range(2)]
            before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
            retried = run_retirement(binary, env, 'retry', identity, current, 0)
            self.assertEqual(retried, current)
            self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
            next_fact = run_retirement(binary, env, 'retry-current', identity, retried, 200, sign(retried, 200))
            self.assertEqual(run_retirement(binary, env, 'inspect', identity), b'CHECKED')
            self.assertGreater(json.loads(next_fact)['event_id'], json.loads(current)['event_id'])
            self.assertEqual(json.loads(next_fact)['boot_id'], json.loads(current)['boot_id'])

    def test_actual_file_reopen_old_current_forgery_capacity_and_monotonic_new_fact(self):
        env = os.environ.copy()
        env['VG_LIVE_DEVICE_TOKEN'] = 'public-synthetic-host-test-input-key-123456789'
        def sign(body):
            digest = hashlib.sha256(body).hexdigest()
            mac = hmac.new(env['VG_LIVE_DEVICE_TOKEN'].encode(),
                           ('VG_EVENT_COMMIT_V1\n201\n'+digest).encode(), hashlib.sha256).hexdigest()
            return ('VGR1:'+digest+':'+mac).encode()
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as root:
            binary = build_retirement_fixture(Path(root).resolve(), env)
            identity = 'b'*32
            old = run_retirement(binary, env, 'prepare', identity)
            current = run_retirement(binary, env, 'old', identity, old, 201, sign(old))
            paths = [binary.parent/('receipt-slot'+str(i)+'.bin') for i in range(2)]
            before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
            self.assertEqual(run_retirement(binary, env, 'retry', identity, current, 0), current)
            self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
            receipt = sign(current)
            bad = receipt[:-1]+(b'0' if receipt[-1:] != b'0' else b'1')
            self.assertEqual(run_retirement(binary, env, 'tamper', identity, current, 201, bad), b'REFUSED')
            self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
            next_fact = run_retirement(binary, env, 'current', identity, current, 201, receipt)
            self.assertEqual(run_retirement(binary, env, 'inspect', identity), b'CHECKED')
            old, current, next_fact = map(json.loads, (old, current, next_fact))
            self.assertNotEqual(old['boot_id'], current['boot_id'])
            self.assertEqual(current['boot_id'], next_fact['boot_id'])
            self.assertEqual(current['event_id'], 1)
            self.assertGreater(next_fact['event_id'], current['event_id'])

    def test_unowned_root_cannot_compile_or_change_files(self):
        with tempfile.TemporaryDirectory(prefix='vg-foreign-') as root, patch('event_receipt_native_bridge.subprocess.run') as run:
            with self.assertRaisesRegex(RuntimeError, 'UNOWNED_ROOT'):
                build_retirement_fixture(Path(root).resolve(), {})
            run.assert_not_called()
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_existing_binary_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as root, patch('event_receipt_native_bridge.subprocess.run') as run:
            binary = Path(root)/('receipt-retire.exe' if os.name == 'nt' else 'receipt-retire')
            binary.write_bytes(b'owned-existing-sentinel')
            with self.assertRaisesRegex(RuntimeError, 'FRESH_PATH'):
                build_retirement_fixture(Path(root).resolve(), {})
            run.assert_not_called()
            self.assertEqual(binary.read_bytes(), b'owned-existing-sentinel')

    def test_existing_slot_bad_identity_phase_and_bounds_refuse_without_child_process(self):
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as root, patch('event_receipt_native_bridge.subprocess.run') as run:
            binary = Path(root).resolve()/('receipt-retire.exe' if os.name == 'nt' else 'receipt-retire')
            binary.write_bytes(b'synthetic-not-executed')
            slot = binary.parent/'receipt-slot0.bin'; slot.write_bytes(b'preserve')
            for phase, identity, body in [('prepare', 'a'*32, b''), ('unknown', 'a'*32, b''),
                                          ('current', '../unsafe', b''), ('current', 'a'*32, b'x'*4097)]:
                with self.assertRaises(ValueError):
                    run_retirement(binary, {}, phase, identity, body)
            run.assert_not_called()
            self.assertEqual(slot.read_bytes(), b'preserve')

    def test_negative_retry_phase_requires_status_zero_original_body_and_no_receipt(self):
        with tempfile.TemporaryDirectory(prefix='vg-live-http-') as root, patch('event_receipt_native_bridge.subprocess.run') as run:
            binary = Path(root).resolve()/('receipt-retire.exe' if os.name == 'nt' else 'receipt-retire')
            binary.write_bytes(b'synthetic-not-executed')
            for phase, status, body, receipt in [('retry', 201, b'{}', b''), ('retry', 0, b'', b''),
                                                ('retry', 0, b'{}', b'x'*134), ('current', 0, b'{}', b'x'*134),
                                                ('retry-current', 201, b'{}', b'x'*134), ('retry-current', 200, b'{}', b''),
                                                ('retry', False, b'{}', b'')]:
                with self.assertRaises(ValueError):
                    run_retirement(binary, {}, phase, 'a'*32, body, status, receipt)
            run.assert_not_called()
            self.assertEqual(binary.read_bytes(), b'synthetic-not-executed')


if __name__ == '__main__':
    unittest.main(verbosity=2)
