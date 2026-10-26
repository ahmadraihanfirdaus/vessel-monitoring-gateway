"""Dedicated actual C99 single-channel fault wire and independent oracle, no DB."""
import argparse
import hashlib
from pathlib import Path

from data_ui_contracts import native_contract, strict_json
from phase9_b4_testlib import compile_c

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'compartment_temperature_c'


def observe(raw):
    native_contract(raw)
    packets = [strict_json(line) for line in raw.splitlines()]
    if len(packets) != 4:
        raise ValueError('FOUR_ISOLATION_STEPS_REQUIRED')
    baseline = packets[0]['channels']
    if len(baseline) != 44 or TARGET not in baseline:
        raise ValueError('ACTUAL_DOMAIN_CHANNELS_REQUIRED')
    references = {'engine_1_rpm': 2000, 'engine_4_rpm': 1990, 'hatch_state': 1,
                  'nav_fix': 1, 'nav_age_ms': 0}
    for name, value in references.items():
        if baseline.get(name) != {'value': value, 'quality': 'valid'}:
            raise ValueError('BASELINE_PROVIDER_VALUES')
    expected_faults = [dict(value=25, quality='valid'), dict(value=None, quality='invalid'),
                       dict(value=None, quality='invalid'), dict(value=30, quality='valid')]
    unaffected = set(baseline) - {TARGET}
    for index, packet in enumerate(packets):
        if (packet['device_id'] != 'fault:demo' or packet['boot_id'] != 'synthetic-isolation'
                or packet['firmware_version'] != 'fault-sim-1.1' or packet['schema_version'] != '1.1'
                or packet['sequence'] != index + 1 or packet['uptime_ms'] != (index + 1) * 200
                or set(packet['channels']) != set(baseline) or packet['channels'][TARGET] != expected_faults[index]):
            raise ValueError('ISOLATED_FAULT_OR_IDENTITY')
        for name in unaffected:
            expected = baseline[name] if name != 'engine_1_rpm' else dict(value=2000+index, quality='valid')
            if expected['quality'] != 'valid' or packet['channels'][name] != expected:
                raise ValueError('OTHER_CHANNEL_CHANGED_OR_STOPPED')
    return {'frames': 4, 'channels_per_frame': 44, 'unaffected_current_channels': 43,
            'invalid_frames': 2, 'last_temperature': 30, 'last_engine_1_rpm': 2003,
            'wire_sha256': hashlib.sha256(raw).hexdigest(), 'database_access': False,
            'shared_bus_fault': False, 'physical_acquisition': False}


def build_bytes():
    # Include the repository fixture by header path; no copied runtime algorithm.
    output = compile_c('#include "fault_isolation_fixture.c"\n',
                       extra_flags=('-Os', '-I'+str(ROOT/'scripts')))
    raw = output.encode('utf-8')
    observe(raw)
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('refusing to overwrite an existing artifact')
    raw = build_bytes()
    args.output.write_bytes(raw)
    print('ISOLATION_C99_WIRE=PASS_4_FRAMES_SHA256_'+hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
