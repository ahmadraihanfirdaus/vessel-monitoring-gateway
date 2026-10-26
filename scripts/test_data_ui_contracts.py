"""Negative/boundary oracles; synthetic inputs are not formal/runtime evidence."""
import copy
import json
import unittest

from data_ui_contracts import native_contract, functional_observation, SECTIONS, Sections, strict_json


class ContractsTest(unittest.TestCase):
    def packet(self):
        return dict(schema_version='1.1', device_id='runtime:demo', firmware_version='test-1',
                    boot_id='synthetic', sequence=1, uptime_ms=0, source_mode='simulation',
                    channels={'zero': {'quality': 'valid', 'value': 0},
                              'absent': {'quality': 'missing', 'value': None}})

    def wire(self, packet):
        return (json.dumps(packet)+'\n').encode()

    def test_real_zero_and_null_are_distinct(self):
        result = native_contract(self.wire(self.packet()))
        self.assertEqual((result['valid_zero'], result['unavailable']), (1, 1))

    def test_all_required_identity_fields(self):
        for key in self.packet():
            packet = self.packet(); del packet[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                native_contract(self.wire(packet))

    def test_uint64_boundaries_and_bool(self):
        for key in ('sequence', 'uptime_ms'):
            packet = self.packet(); packet[key] = 2**64-1
            native_contract(self.wire(packet))
            for value in (-1, 2**64, True, 1.0, '1', None):
                packet[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    native_contract(self.wire(packet))

    def test_quality_null_zero_nonfinite_matrix(self):
        for quality in ('valid', 'invalid', 'missing', 'unknown', 'stale', 'VALID', None):
            for value in (None, 0, 4.5, True, '0', float('nan'), float('inf')):
                packet = self.packet(); packet['channels']['zero'] = dict(quality=quality, value=value)
                permitted = ((quality in ('valid', 'stale') and type(value) in (int, float)
                              and value == value and value not in (float('inf'), -float('inf')))
                             or (quality in ('stale', 'invalid', 'missing', 'unknown') and value is None))
                with self.subTest(quality=quality, value=value):
                    if permitted:
                        native_contract(self.wire(packet))
                    else:
                        with self.assertRaises(ValueError):
                            native_contract(self.wire(packet))

    def test_strict_json_and_sequence_no_vacuous_pass(self):
        for raw in (b'{}\n', b'[]\n', b'', b'{"a":1,"a":2}', b'{"a":NaN}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                native_contract(raw)
        packet = self.packet()
        with self.assertRaises(ValueError):
            native_contract(self.wire(packet)*2)
        packet['channels'] = {}
        with self.assertRaises(ValueError):
            native_contract(self.wire(packet))

    def test_channel_capacity_and_identity(self):
        packet = self.packet()
        for version, count in (('1.0', 16), ('1.1', 72)):
            packet['schema_version'] = version
            packet['channels'] = {'ch_'+str(i): dict(value=0, quality='valid') for i in range(count)}
            native_contract(self.wire(packet))
            packet['channels']['excess'] = dict(value=0, quality='valid')
            with self.assertRaises(ValueError):
                native_contract(self.wire(packet))

    def test_synthetic_physical_label_is_not_native_provenance(self):
        for mode in ('physical', 'bench_test', 'SIMULATION', '', None):
            packet = self.packet(); packet['source_mode'] = mode
            with self.assertRaises(ValueError):
                native_contract(self.wire(packet))

    def test_empty_or_placeholder_sections_are_rejected(self):
        labels = ''.join('<section aria-label="'+name+'"><h2>'+name+'</h2></section>' for name in SECTIONS).encode()
        for status, body in ((200, labels), (302, labels), (200, labels+labels), (200, b''), (200, b'\xff')):
            with self.subTest(status=status, body=body[:20]), self.assertRaises(ValueError):
                functional_observation(status, body)

    def test_parser_cannot_count_comment_or_attribute_as_section(self):
        parser = Sections(); parser.feed('<!-- <section aria-label="Overview"> -->'
                                        '<p title="Safety">Overview</p>')
        self.assertEqual(sum(parser.counts.values()), 0)
        with self.assertRaises(ValueError):
            parser.feed('<section aria-label="Overview" aria-label="Safety">')


if __name__ == '__main__':
    unittest.main()
