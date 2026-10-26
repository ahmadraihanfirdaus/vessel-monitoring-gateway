"""Real native fixtures plus adversarial host evidence/parser/guard regressions."""
import binascii
import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

import formal_offline_file as storage
import run_formal_fault_storage as gate
from fault_isolation_wire_bridge import build_bytes, observe, TARGET


class FaultStorageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = build_bytes()
        cls.packets = [json.loads(line) for line in cls.raw.splitlines()]
        cls.slot_bytes = []
        real = storage.inspect_slot
        def capture(raw):
            cls.slot_bytes.append(raw)
            return real(raw)
        with patch.object(storage, 'inspect_slot', side_effect=capture):
            cls.actual = storage.execute()

    @staticmethod
    def wire(packets):
        return ('\n'.join(json.dumps(p) for p in packets)+'\n').encode()

    def test_real_isolation_and_actual_host_reopen_are_nonvacuous(self):
        self.assertEqual(observe(self.raw)['unaffected_current_channels'], 43)
        self.assertEqual(self.actual['retained'], 8)
        self.assertEqual(self.actual['latest_sequence'], 8)
        self.assertEqual(self.actual['generation'], 72)
        self.assertTrue(self.actual['older_corruption_preserved_latest'])
        self.assertLessEqual(sum(self.actual['slot_bytes']), 2*5184)
        self.assertGreater(self.actual['disk_rejected'], 0)
        self.assertFalse(self.actual['physical_durability'])

    def test_fault_cannot_silently_invalidate_any_unaffected_channel(self):
        for name in set(self.packets[0]['channels'])-{TARGET}:
            packets=copy.deepcopy(self.packets)
            packets[1]['channels'][name]=dict(value=None,quality='invalid')
            with self.subTest(channel=name), self.assertRaises(ValueError):
                observe(self.wire(packets))

    def test_zero_null_quality_identity_and_stopped_engine_are_rejected(self):
        for kind in ('zero','early_recovery','stopped_engine','lost_channel','rewound_sequence','bool_uptime'):
            packets=copy.deepcopy(self.packets)
            if kind=='zero':packets[1]['channels'][TARGET]['value']=0
            if kind=='early_recovery':packets[1]['channels'][TARGET]=dict(value=30,quality='valid')
            if kind=='stopped_engine':packets[2]['channels']['engine_1_rpm']['value']=2000
            if kind=='lost_channel':del packets[2]['channels']['power_w']
            if kind=='rewound_sequence':packets[2]['sequence']=1
            if kind=='bool_uptime':packets[2]['uptime_ms']=True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                observe(self.wire(packets))

    def test_every_truncation_and_distributed_corruption_of_actual_slot_fails(self):
        raw=self.slot_bytes[0]
        for end in range(len(raw)):
            with self.assertRaises(ValueError):storage.inspect_slot(raw[:end])
        for offset in range(0,len(raw),17):
            bad=bytearray(raw);bad[offset]^=1
            with self.assertRaises(ValueError):storage.inspect_slot(bytes(bad))

    def test_crc_repair_does_not_authorize_bad_capacity_identity_or_trailing_bytes(self):
        raw=self.slot_bytes[0]
        for mutation in ('count','length','version','trailing'):
            bad=bytearray(raw[:-4])
            if mutation=='count':bad[31]=9
            if mutation=='length':bad[29:31]=struct.pack('<H',4097)
            if mutation=='version':bad[4]=3
            if mutation=='trailing':bad+=b'X'
            bad+=struct.pack('<I',binascii.crc32(bad)&0xffffffff)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                storage.inspect_slot(bytes(bad))

    def test_default_never_hashes_builds_or_writes(self):
        output=io.StringIO()
        with patch.object(sys,'argv',['gate']),patch.object(gate,'source_snapshot') as snapshot, \
             patch.object(gate,'build_bytes') as builder,patch.object(gate,'execute') as execute,redirect_stdout(output):
            self.assertEqual(gate.main(),0)
        snapshot.assert_not_called();builder.assert_not_called();execute.assert_not_called()
        self.assertIn('NOT_RUN_READ_ONLY',output.getvalue())

    def test_foreign_root_cannot_compile_write_or_be_cleaned(self):
        with patch.object(storage.tempfile,'mkdtemp',return_value=str(gate.ROOT)), \
             patch.object(storage.subprocess,'run') as process,patch.object(storage.shutil,'rmtree') as cleanup:
            with self.assertRaises(RuntimeError):storage.execute()
        process.assert_not_called();cleanup.assert_not_called()

    def test_fake_native_counts_floor_and_changed_original_metadata_fail(self):
        facts=dict(generation=72,latest_sequence=8,retained=8,confirmed_floor=0,
                   original_first_id=1,original_last_id=8,older_corruption_preserved_latest=True,
                   healthy_reopen=True,ram_rejected=self.actual['ram_rejected'],disk_rejected=self.actual['disk_rejected'])
        slots=[storage.inspect_slot(raw) for raw in self.slot_bytes]
        for change in ('floor','capacity','bool','no_refusal','generation','metadata','lost_latest'):
            changed=copy.deepcopy(facts); images=copy.deepcopy(slots)
            if change=='floor':changed['confirmed_floor']=1
            if change=='capacity':changed['retained']=9
            if change=='bool':changed['generation']=True
            if change=='no_refusal':changed['disk_rejected']=0
            if change=='generation':images[0]['generation']=70
            if change=='metadata':images[0]['records'][0]=('bounded-boot-a',1,'altered',True)
            if change=='lost_latest':images[0]['latest']['channels']={}
            with self.subTest(change=change),self.assertRaises(ValueError):storage.observe(changed,images)

    def test_missing_protocol_or_compiler_blocks_without_false_pass(self):
        for error in (OSError('synthetic'),UnicodeError('synthetic')):
            with patch.object(sys,'argv',['gate','--execute']),patch.object(Path,'read_text',side_effect=error), \
                 patch.object(gate,'build_bytes') as builder,redirect_stdout(io.StringIO()):
                self.assertEqual(gate.main(),3)
            builder.assert_not_called()
        with patch.object(sys,'argv',['gate','--execute']),patch.object(gate,'build_bytes',side_effect=FileNotFoundError('synthetic')), \
             patch.object(gate,'execute') as execute,redirect_stdout(io.StringIO()):
            self.assertEqual(gate.main(),3)
        execute.assert_not_called()

    def test_unreviewed_protocol_blocks_before_hash_or_compiler(self):
        with patch.object(sys,'argv',['gate','--execute']),patch.object(Path,'read_text',return_value=''), \
             patch.object(gate,'source_snapshot') as snapshot,patch.object(gate,'build_bytes') as builder,redirect_stdout(io.StringIO()):
            self.assertEqual(gate.main(),3)
        snapshot.assert_not_called();builder.assert_not_called()

    def test_source_drift_or_failed_assertion_cannot_publish_execution_record(self):
        for error in (False,True):
            output=io.StringIO()
            with patch.object(sys,'argv',['gate','--execute']),patch.object(gate,'source_snapshot',side_effect=[{}, {'drift':'x'}]), \
                 patch.object(gate,'build_bytes',side_effect=AssertionError('synthetic') if error else None,return_value=self.raw), \
                 patch.object(gate,'execute',return_value=self.actual),redirect_stdout(output):
                self.assertEqual(gate.main(),1)
            self.assertNotIn('FAULT_STORAGE_RECORD=',output.getvalue())


if __name__=='__main__':
    unittest.main()
