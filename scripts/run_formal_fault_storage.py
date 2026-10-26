"""SIM011/SUP013 dedicated actual host gates; default read-only, no DB/network."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from fault_isolation_wire_bridge import build_bytes, observe
from formal_offline_file import execute

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT/'docs/testing/formal-fault-storage-cases-20261026.md'


def source_snapshot():
    paths = list((ROOT/'firmware/src').glob('*.h')) + [ROOT/'scripts'/name for name in (
        'fault_isolation_fixture.c', 'fault_isolation_wire_bridge.py', 'formal_offline_file.py',
        'host_offline_file_io.h', 'offline_bounded_file_fixture.c', 'run_formal_fault_storage.py',
        'test_formal_fault_storage.py', 'continuous_simulation_fixture.c', 'data_ui_contracts.py', 'phase9_b4_testlib.py')]
    paths += [PROTOCOL]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        print('FAULT_STORAGE=NOT_RUN_READ_ONLY')
        return 0
    try:
        if 'PROTOCOL_CASE_BY_CASE_REVIEW=PASS_FOR_SIM011_SUP013_SUP014_WITH_BOUNDARIES_ABOVE' not in PROTOCOL.read_text(encoding='utf-8'):
            raise RuntimeError('CASE_REVIEW_REQUIRED')
        before = source_snapshot()
        fault = observe(build_bytes())
        offline = execute()
        if before != source_snapshot():
            raise ValueError('SOURCE_CHANGED')
        print('FAULT_STORAGE_RECORD='+json.dumps(dict(cases=['SIM-011', 'SUP-013'], fault=fault, offline=offline,
            source_sha256=hashlib.sha256(repr(sorted(before.items())).encode()).hexdigest(),
            database_access=False, physical_durability=False),sort_keys=True))
        print('FAULT_STORAGE=PASS_ACTUAL_C99_HOST_FILE_ONLY')
        return 0
    except (OSError, UnicodeError, RuntimeError, subprocess.TimeoutExpired) as error:
        print('FAULT_STORAGE=BLOCKED_'+type(error).__name__)
        return 3
    except (ValueError, AssertionError, TypeError, KeyError, IndexError):
        print('FAULT_STORAGE=FAIL_NATIVE_OR_INDEPENDENT_ORACLE')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
