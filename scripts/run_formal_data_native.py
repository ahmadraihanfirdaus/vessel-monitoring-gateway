"""SUP011/012 dedicated native unit observations; no application/DB bootstrap."""
import argparse
import hashlib
import json
from pathlib import Path

from data_ui_contracts import native_contract
from continuous_simulation_wire_bridge import build_bytes as domain_bytes
from runtime_uplink_wire_bridge import build_bytes

ROOT = Path(__file__).resolve().parents[1]


def source_snapshot():
    paths = list((ROOT/'firmware/src').glob('*.h')) + [ROOT/'scripts'/name for name in (
        'data_ui_contracts.py', 'test_data_ui_contracts.py', 'run_formal_data_native.py', 'test_formal_data_native.py',
        'runtime_uplink_wire_bridge.py', 'runtime_uplink_wire_fixture.c',
        'continuous_simulation_wire_bridge.py', 'continuous_simulation_fixture.c', 'phase9_b4_testlib.py')]
    paths += [ROOT/'docs/testing/formal-data-ui-cases-20261026.md']
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        print('DATA_NATIVE=NOT_RUN_READ_ONLY')
        return 0
    try:
        before = source_snapshot()
        # Protocol must be available/decodable before compiler execution.
        protocol = (ROOT/'docs/testing/formal-data-ui-cases-20261026.md').read_text(encoding='utf-8')
        if 'PROTOCOL_CASE_BY_CASE_REVIEW=PASS_FOR_SIX_SPECIFIED_EXECUTION_OR_REVIEW_CLASSES' not in protocol:
            raise RuntimeError('PROTOCOL_REVIEW_REQUIRED')
        observations = [native_contract(raw) for raw in (build_bytes(), domain_bytes('runtime:demo'))]
        if sum(x['valid_zero'] for x in observations) < 1 or sum(x['unavailable'] for x in observations) < 1:
            raise ValueError('NONVACUOUS_ZERO_AND_UNAVAILABLE_REQUIRED')
        if before != source_snapshot():
            raise ValueError('SOURCE_DRIFT')
        print('DATA_NATIVE_RECORD='+json.dumps({'cases': ['SUP-011', 'SUP-012'], 'observations': observations,
              'source_sha256': hashlib.sha256(repr(sorted(before.items())).encode()).hexdigest(),
              'database_access': False, 'physical_acquisition': False}, sort_keys=True))
        print('DATA_NATIVE=PASS_ACTUAL_C99_UNIT_NO_DB_WRITE')
        return 0
    except (OSError, UnicodeError, RuntimeError) as error:
        print('DATA_NATIVE=BLOCKED_'+type(error).__name__)
        return 3
    except (ValueError, AssertionError, TypeError):
        print('DATA_NATIVE=FAIL_CONTRACT')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
