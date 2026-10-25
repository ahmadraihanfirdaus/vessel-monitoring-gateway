"""Real native two-slot transaction recovery -> shared runtime replay bytes."""
import argparse
import hashlib
import json
from pathlib import Path
from phase9_b4_testlib import compile_c
from test_offline_transaction import COMMON

ROOT = Path(__file__).resolve().parents[1]


def build_bytes(device='replay:demo'):
    if device not in ('replay:demo', 'runtime:demo'):
        raise ValueError('unsupported synthetic fixture identity')
    # Reuse the existing deterministic IO fixture; no parallel storage model.
    common = COMMON.split('int main(void)', 1)[0].replace('"disk:demo"', 'VG_REPLAY_FIXTURE_DEVICE')
    source = common+(ROOT/'scripts/recovered_replay_wire_fixture.c').read_text(encoding='utf-8')
    output = compile_c(source, extra_flags=('-Os', '-DVG_REPLAY_FIXTURE_DEVICE="'+device+'"'))
    lines = output.splitlines()
    assert len(lines) == 6
    packets = [json.loads(line) for line in lines]
    assert all(p['device_id'] == device and 0 < len(line.encode()) <= 4096 for p, line in zip(packets, lines))
    assert [p['boot_id'] for p in packets] == ['boot-a']*2+['replay-boot-b']*3+['replay-boot-c']
    assert [p['event_id'] for p in packets] == [1, 2, 1, 2, 3, 1]
    assert [p['schema_version'] for p in packets] == ['1.0']*2+['1.1']*4
    assert all(('alarm' in p) == (p['schema_version'] == '1.1') for p in packets)
    assert packets[1]['source_mode'] == 'bench_test' and packets[1]['linked_alarm_id'] == 0
    assert packets[3]['alarm']['acknowledged_at_ms'] == 0 and packets[3]['alarm']['cleared_at_ms'] is None
    return ('\n'.join(lines)+'\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('refusing to overwrite an existing artifact')
    raw = build_bytes()
    args.output.write_bytes(raw)
    print('RECOVERED_REPLAY_C99_WIRE=PASS_6_CROSS_BOOT_EVENTS_SHA256_'+hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
