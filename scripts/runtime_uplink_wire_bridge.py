"""Compile actual C99 core-to-wire fixture; no credentials, DB or network."""
import argparse
import hashlib
import json
from pathlib import Path
from phase9_b4_testlib import compile_c

ROOT = Path(__file__).resolve().parents[1]


def build_bytes():
    output = compile_c((ROOT/'scripts/runtime_uplink_wire_fixture.c').read_text(encoding='utf-8'), extra_flags=('-Os',))
    lines = output.splitlines()
    assert len(lines) == 6
    expected = ['valid', 'missing', 'invalid', 'valid', 'stale', 'valid']
    for i, line in enumerate(lines):
        assert 0 < len(line.encode('utf-8')) <= 4096
        data = json.loads(line)
        assert data['device_id'] == 'runtime:demo' and data['source_mode'] == 'simulation'
        assert data['sequence'] == i+1 and data['uptime_ms'] == (i+1)*200
        channel = data['channels']['demo_channel']
        assert channel['quality'] == expected[i]
        assert channel['value'] == (None if i in (1, 2) else 42)
    return ('\n'.join(lines)+'\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = build_bytes()
    args.output.write_bytes(raw)
    print('RUNTIME_C99_WIRE=PASS_6_CASES_SHA256_'+hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
