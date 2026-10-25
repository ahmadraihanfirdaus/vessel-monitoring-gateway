"""Actual C99 all-domain frames, canonical checkpoint/recovery, no DB/network."""
import argparse
import hashlib
import json
from pathlib import Path
from phase9_b4_testlib import compile_c

ROOT = Path(__file__).resolve().parents[1]


def build_bytes(device="continuous:demo"):
    if device not in ("continuous:demo", "runtime:demo"):
        raise ValueError("unsupported synthetic fixture identity")
    output = compile_c((ROOT/'scripts/continuous_simulation_fixture.c').read_text(encoding='utf-8'), extra_flags=('-Os', '-DVG_CONTINUOUS_FIXTURE_DEVICE=\"'+device+'\"'))
    lines = output.splitlines()
    assert len(lines) == 24
    for index, line in enumerate(lines):
        data = json.loads(line)
        assert len(line.encode('utf-8')) <= 4096
        assert data['schema_version'] == '1.1' and data['device_id'] == device
        assert data['source_mode'] == 'simulation' and data['sequence'] == index + 1
        assert data['uptime_ms'] == (index + 1) * 200
        assert len(data['channels']) == 48
        for channel in data['channels'].values():
            if channel['quality'] in ('invalid', 'missing', 'unknown'):
                assert channel['value'] is None
    return ('\n'.join(lines)+'\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('refusing to overwrite an existing artifact')
    raw = build_bytes()
    args.output.write_bytes(raw)
    print('CONTINUOUS_C99_WIRE=PASS_24_RECOVERED_FRAMES_SHA256_'+hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
