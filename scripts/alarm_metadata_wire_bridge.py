"""Actual native lifecycle/coordinator/VGS2-recovered event 1.1 bytes; no DB."""
import argparse
import hashlib
import json
from pathlib import Path
from phase9_b4_testlib import compile_c

ROOT = Path(__file__).resolve().parents[1]


def build_bytes(device='alarm:demo'):
    if device not in ('alarm:demo', 'runtime:demo'):
        raise ValueError('unsupported synthetic fixture identity')
    output = compile_c((ROOT/'scripts/alarm_metadata_wire_fixture.c').read_text(encoding='utf-8'),
        extra_flags=('-Os', '-I', str(ROOT/'scripts'), '-DVG_CONTINUOUS_FIXTURE_DEVICE="'+device+'"'))
    lines = output.splitlines()
    assert len(lines) == 11
    for line in lines:
        assert 0 < len(line.encode()) <= 4096
        packet = json.loads(line)
        assert packet['schema_version'] == '1.1' and packet['device_id'] == device
        assert packet['source_mode'] == 'simulation'
        assert set(packet['alarm']) == {'priority_code', 'reason_code', 'state', 'raised_at_ms',
                                        'acknowledged_at_ms', 'cleared_at_ms'}
    zero = [json.loads(line) for line in lines[:3]]
    assert [p['alarm']['acknowledged_at_ms'] for p in zero] == [None, 0, 0]
    assert [p['alarm']['cleared_at_ms'] for p in zero] == [None, None, 0]
    return ('\n'.join(lines)+'\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('refusing to overwrite an existing artifact')
    raw = build_bytes()
    args.output.write_bytes(raw)
    print('ALARM_METADATA_C99_WIRE=PASS_11_RECOVERED_EVENTS_SHA256_'+hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
