#!/usr/bin/env python3
"""Fail-closed real C99/Laravel/MySQL gate. No local dotenv or database provisioning.

Default is read-only. --execute permits migration apply and transactional test
fixtures on a verified EMPTY isolated approved catalog. --migration-roundtrip also
permits rollback/reapply of those newly applied migrations. Never use real data.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import os
import re
import secrets
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from build_esp32_port import source_snapshot as firmware_source_snapshot

ROOT = Path(__file__).resolve().parents[1]
WIRE_FIXTURES = (
    ('phase9_b14_wire_bridge.py', 'wire.jsonl', 'VG_B14_WIRE_JSONL'),
    ('phase9_b15_event_bridge.py', 'events.jsonl', 'VG_B15_EVENT_JSONL'),
    ('runtime_uplink_wire_bridge.py', 'runtime.jsonl', 'VG_RUNTIME_WIRE_JSONL'),
    ('continuous_simulation_wire_bridge.py', 'continuous.jsonl', 'VG_CONTINUOUS_WIRE_JSONL'),
    ('alarm_metadata_wire_bridge.py', 'alarms.jsonl', 'VG_ALARM_METADATA_WIRE_JSONL'),
    ('recovered_replay_wire_bridge.py', 'replayed.jsonl', 'VG_RECOVERED_REPLAY_WIRE_JSONL'),
    ('fault_isolation_wire_bridge.py', 'isolated.jsonl', 'VG_FAULT_ISOLATION_WIRE_JSONL'),
)


def source_snapshot():
    """Public execution inputs only. Never read/hash dotenv, generated keys or DB."""
    records = firmware_source_snapshot()
    paths = [Path(__file__), ROOT/'scripts/mysql_test_gate.php', ROOT/'scripts/test_mysql_integration_gate.py']
    paths += [ROOT/'scripts'/script for script, _, _ in WIRE_FIXTURES]
    paths += [ROOT/'scripts'/name for name in ('phase9_b14_wire_fixture.c', 'phase9_b15_event_wire_fixture.c',
        'runtime_uplink_wire_fixture.c', 'continuous_simulation_fixture.c', 'alarm_metadata_wire_fixture.c',
        'recovered_replay_wire_fixture.c', 'fault_isolation_fixture.c', 'data_ui_contracts.py',
        'phase9_b4_testlib.py', 'test_offline_transaction.py', 'phase9_b17_receipt_crosscheck.py')]
    base = ROOT/'backend/laravel'
    paths += [base/'bootstrap/app.php', base/'composer.json', base/'composer.lock', base/'phpunit.xml']
    for directory in ('app', 'config', 'routes', 'resources/views', 'database/migrations', 'tests'):
        paths += list((base/directory).rglob('*.php'))
    paths += list((base/'public/assets').glob('*.js'))
    for path in sorted(set(paths)):
        if (path.is_symlink() or not path.resolve().is_relative_to(ROOT) or not path.is_file()
                or path.name.startswith('.env') or path.stat().st_size > 1024*1024):
            raise OSError('PUBLIC_SOURCE_SNAPSHOT_UNAVAILABLE')
        records[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return records


def run(command, env, cwd=ROOT):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True,
                            errors='replace', timeout=240)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--migration-roundtrip', action='store_true')
    parser.add_argument('--testing-env', action='store_true',
                        help='explicitly load the approved ignored .env.testing in PHP processes only')
    parser.add_argument('--php-binary', default=os.environ.get('VG_PHP_CLI', 'php'),
                        help='explicit PHP CLI executable; never modifies PATH')
    parser.add_argument('--existing-schema', action='store_true',
                        help='inspect exact migrated empty schema and run tests without migration reset')
    parser.add_argument('--upgrade-previous', action='store_true',
                        help='explicitly admit the exact empty five-migration profile, then apply the sixth migration')
    args = parser.parse_args()
    if args.migration_roundtrip and not args.execute:
        parser.error('--migration-roundtrip requires --execute')
    if args.existing_schema and not args.execute:
        parser.error('--existing-schema requires --execute')
    if args.upgrade_previous and (not args.execute or not args.existing_schema):
        parser.error('--upgrade-previous requires --execute --existing-schema')
    env = os.environ.copy()
    env['VG_PHP_CLI'] = args.php_binary
    if args.testing_env:
        env['VG_USE_TESTING_ENV'] = '1'
    # Explicit process config is mandatory; never load or copy local dotenv.
    env.update(CACHE_STORE='array', SESSION_DRIVER='array',
               QUEUE_CONNECTION='sync', LOG_CHANNEL='null', DB_URL='', DATABASE_URL='', DB_SOCKET='')
    env['APP_KEY'] = 'base64:'+base64.b64encode(secrets.token_bytes(32)).decode('ascii')
    env['VG_TEST_EPHEMERAL_KEY'] = '1'
    # Preserve connection overrides for guard rejection instead of hiding them.
    for key in ('DB_URL', 'DATABASE_URL', 'DB_SOCKET'):
        if key in os.environ:
            env[key] = os.environ[key]
    try:
        preflight = run([args.php_binary, 'scripts/mysql_test_gate.php',
                         '--inspect-previous' if args.upgrade_previous else '--inspect' if args.existing_schema else '--check'], env)
        if preflight.returncode:
            for line in preflight.stderr.splitlines():
                if line.startswith('MYSQL_TEST_BLOCKED:'):
                    print(line)
            print('MYSQL_INTEGRATION=BLOCKED_PREFLIGHT_NO_MIGRATIONS_NO_TEST_FIXTURES')
            return 3
        print(preflight.stdout, end='')
        if not args.execute:
            print('MYSQL_INTEGRATION=NOT_RUN_READ_ONLY_MODE')
            return 0
        inputs = source_snapshot()
        # Generate all existing fixture dependencies before any schema mutation.
        with tempfile.TemporaryDirectory(prefix='vg-mysql-wire-') as folder:
            temp = Path(folder)
            for script, name, variable in WIRE_FIXTURES:
                output = temp / name
                generated = run([sys.executable, '-B', 'scripts/'+script, '--output', str(output)], env)
                if generated.returncode:
                    print('MYSQL_INTEGRATION=BLOCKED_C99_FIXTURE_BUILD_NO_MIGRATIONS')
                    return 3
                print(generated.stdout, end='')
                env[variable] = str(output)
            env['VG_B17_RECEIPTS_JSONL'] = str(temp / 'receipts.jsonl')
            if not args.existing_schema or args.migration_roundtrip or args.upgrade_previous:
                mode = ('--upgrade-previous-roundtrip' if args.upgrade_previous and args.migration_roundtrip else
                        '--upgrade-previous' if args.upgrade_previous else
                        '--roundtrip-existing' if args.existing_schema else
                        '--migration-roundtrip' if args.migration_roundtrip else '--migrate')
                migrated = run([args.php_binary, 'scripts/mysql_test_gate.php', mode], env)
                print(migrated.stdout, end='')
                if migrated.returncode:
                    print('MYSQL_INTEGRATION=BLOCKED_MIGRATION_GATE')
                    return 3
            else:
                print('MYSQL_MIGRATION=NOT_RUN_EXISTING_SCHEMA_MODE')
            report = temp / 'phpunit.xml'
            tests = run([args.php_binary, 'vendor/bin/phpunit', '--colors=never', '--do-not-cache-result',
                         '--log-junit', str(report)],
                        env, ROOT / 'backend/laravel')
            # PHPUnit failures can contain SQL bindings or synthetic auth tokens.
            # Keep public output to status; inspect failures locally with care.
            if report.is_file():
                root = ET.parse(report).getroot()
                cases = list(root.iter('testcase'))
                failed = [case for case in cases if any(case.find(tag) is not None for tag in ('error', 'failure'))]
                skipped = sum(case.find('skipped') is not None for case in cases)
                print(f'MYSQL_LARAVEL_CASES={len(cases)} FAILED={len(failed)} SKIPPED={skipped}')
                for case in failed:
                    name = (case.get('classname', '')+'::'+case.get('name', ''))[:200]
                    print('MYSQL_FAILED_CASE='+re.sub(r'[^A-Za-z0-9_:.\\-]', '_', name))
                if failed:
                    print('MYSQL_LARAVEL_SUITE=FAIL')
                    return 1
                if not cases or skipped:
                    print('MYSQL_LARAVEL_SUITE=BLOCKED_EMPTY_OR_SKIPPED_TESTS')
                    return 3
            elif tests.returncode == 0:
                print('MYSQL_LARAVEL_SUITE=BLOCKED_MISSING_REPORT')
                return 3
            print('MYSQL_LARAVEL_SUITE='+('PASS' if tests.returncode == 0 else 'FAIL'))
            if tests.returncode:
                return 1
            crosscheck = run([sys.executable, '-B', 'scripts/phase9_b17_receipt_crosscheck.py',
                              '--input', env['VG_B17_RECEIPTS_JSONL'], '--evidence-dir', str(temp)], env)
            print('MYSQL_HTTP_ACK_CROSSCHECK='+('PASS' if crosscheck.returncode == 0 else 'FAIL'))
            if crosscheck.returncode:
                return 1
            # Verify final catalog/row cleanup independently of PHPUnit's report.
            # A failed/foreign catalog is retained for explicit recovery, never erased.
            postflight = run([args.php_binary, 'scripts/mysql_test_gate.php', '--inspect'], env)
            if (postflight.returncode or
                    'DATABASE_POSTCHECK=PASS_TEN_TABLES_SIX_MIGRATIONS_ZERO_APPLICATION_ROWS' not in postflight.stdout):
                print('MYSQL_INTEGRATION=BLOCKED_POSTFLIGHT_CATALOG_NO_CLEANUP')
                return 3
            print(postflight.stdout, end='')
            print('MYSQL_POSTFLIGHT=PASS_EXACT_EMPTY_APPROVED_CATALOG')
            if inputs != source_snapshot():
                print('MYSQL_INTEGRATION=FAIL_SOURCE_CHANGED_DURING_TEST')
                return 1
            print('MYSQL_SOURCE_STABILITY=PASS_SHA256_'+hashlib.sha256(repr(sorted(inputs.items())).encode()).hexdigest())
            print('MYSQL_INTEGRATION=PASS_ISOLATED_LOCAL_ONLY')
            return 0
    except (OSError, subprocess.TimeoutExpired, ET.ParseError):
        print('MYSQL_INTEGRATION=BLOCKED_TOOL_OR_TIMEOUT')
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
