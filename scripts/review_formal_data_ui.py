"""Read-only review of fresh source-bound actual gate logs. Never boot PHP/DB."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from data_ui_contracts import strict_json, SECTIONS, SECTION_MARKERS, PROVENANCE_MARKERS
from run_live_http_integration import source_snapshot
from run_formal_data_native import source_snapshot as native_snapshot

REQUIRED_CASES = (
    'REAL_LOOPBACK_TLS_AND_PHP_READY', 'VERIFIED_ISOLATED_FIXTURE_PREPARATION',
    'TLS_UNKNOWN_CA_REJECTED', 'TLS_WRONG_HOST_REJECTED', 'TLS_NO_PLAINTEXT_DOWNGRADE',
    'EIGHT_SECTIONS_ACTUAL_AUTHENTICATED_DATA_REVIEW', 'GRANT_REVOCATION_EFFECTIVE_NEXT_REQUEST',
    'USER_DISABLE_EFFECTIVE_NEXT_REQUEST', 'UNGRANTED_DEVICE_404', 'REAL_DATABASE_SESSION_ID_ROTATED',
    'PROJECT_ENTRY_GUEST_REQUIRES_SESSION', 'FORMAL_AUTH_DIRECT_DB_ZERO_BEFORE_AND_AFTER',
    'NATIVE_SIX_IDENTITIES_VALUES_AND_QUALITIES_RETAINED', 'NATIVE_V11_IDENTITY_AND_ALL_48_QUALITIES_RETAINED',
    'AUTH_MISSING', 'AUTH_UNKNOWN', 'PAYLOAD_4097_REJECTED', 'MALFORMED_JSON_REJECTED',
    'EMPTY_SCHEMA_REJECTED', 'DEVICE_IDENTITY_MISMATCH', 'SOURCE_MISSING_REJECTED', 'SOURCE_UNKNOWN_REJECTED',
    'FORMAL_DEDUP_CREATE', 'FORMAL_DEDUP_IDENTICAL', 'FORMAL_DEDUP_CONFLICT',
    'FORMAL_DIRECT_DB_DEDUP', 'FORMAL_FRESH_AUTH_ABSENT', 'FORMAL_FRESH_AUTH_UNKNOWN',
    'FORMAL_DIRECT_DB_SRC_SIMULATION', 'FORMAL_DIRECT_DB_SRC_BENCH_TEST', 'FORMAL_DIRECT_DB_SRC_PHYSICAL')


def digest(records):
    return hashlib.sha256(repr(sorted(records.items())).encode()).hexdigest()


def one_record(text, prefix):
    lines = [line[len(prefix):] for line in text.splitlines() if line.startswith(prefix)]
    if len(lines) != 1:
        raise ValueError('EXACT_ONE_RECORD_REQUIRED')
    return strict_json(lines[0])


def review(http, native, current_source, current_native):
    for text in (http, native):
        if len(text) > 1024 * 1024 or re.search(r'=(?:FAIL|BLOCKED)', text):
            raise ValueError('NONPASS_OR_OVERSIZE_EVIDENCE')
    terminal = 'LIVE_HTTP_GATE=PASS_LOCAL_ONLY_HARDWARE_DEPLOYED_TLS_NOT_RUN'
    cleanup = 'LIVE_HTTP_CLEANUP=PASS_EXACT_OWNERSHIP_ZERO_APPLICATION_ROWS'
    stability = 'LIVE_HTTP_SOURCE_STABILITY=PASS_SHA256_'+current_source
    lines = http.splitlines()
    if lines[-2:] != [stability, terminal] or lines.count(cleanup) != 1 or lines.count(terminal) != 1:
        raise ValueError('INCOMPLETE_OR_STALE_RUNTIME_GATE')
    record = one_record(http, 'DATA_UI_RECORD=')
    if lines.index(cleanup) <= next(i for i, x in enumerate(lines) if x.startswith('DATA_UI_RECORD=')):
        raise ValueError('CLEANUP_ORDER')
    if (record.get('version') != 1 or type(record['version']) is not int
            or record.get('source_sha256') != current_source or record.get('physical_acquisition') is not False
            or record.get('producer') != 'actual_loopback_tls_php_mariadb_owned_fixture_writes'):
        raise ValueError('RUNTIME_PROVENANCE')
    expected_statuses = dict(simulation=201, bench_test=201, physical=201)
    for name, expected in dict(source_statuses=expected_statuses, source_rejected=[422, 422],
                               dedup_statuses=[201, 200, 409], auth_statuses=[401, 401]).items():
        if record.get(name) != expected or json.dumps(record[name], sort_keys=True) != json.dumps(expected, sort_keys=True):
            raise ValueError('HTTP_'+name.upper())
    before, after = record['database_before'], record['database_after']
    labels = {'src-simulation', 'src-bench_test', 'src-physical', 'dedup', 'authbad'}
    if set(before) != labels or set(after) != labels:
        raise ValueError('DIRECT_DATABASE_IDENTITIES')
    if any(value != {'count': 0, 'rows': []} or type(value['count']) is not int for value in before.values()):
        raise ValueError('FRESH_IDENTITIES_REQUIRED')
    if after['authbad'] != {'count': 0, 'rows': []} or type(after['authbad']['count']) is not int:
        raise ValueError('UNAUTHORIZED_PERSISTENCE')
    firmware = None
    for label in sorted(labels - {'authbad'}):
        fact = after[label]
        if fact.get('count') != 1 or type(fact['count']) is not int or not isinstance(fact.get('rows'), list) or len(fact['rows']) != 1:
            raise ValueError('ONE_CANONICAL_ROW_REQUIRED')
        row = fact['rows'][0]
        wanted_mode = label[4:] if label.startswith('src-') else 'simulation'
        if set(row) != {'source_mode', 'schema_version', 'firmware_version', 'uptime_ms', 'channel_count', 'quality', 'value'}:
            raise ValueError('DATABASE_FIELDS')
        if (row['source_mode'] != wanted_mode or row['schema_version'] != '1.0' or row['quality'] != 'valid'
                or type(row['channel_count']) is not int or row['channel_count'] != 1
                or type(row['value']) not in (int, float) or row['value'] != 42 or row['uptime_ms'] != '200'
                or not isinstance(row['firmware_version'], str) or not re.fullmatch(r'[A-Za-z0-9._:-]{1,48}', row['firmware_version'])):
            raise ValueError('CANONICAL_DATABASE_VALUES')
        if firmware is not None and row['firmware_version'] != firmware:
            raise ValueError('FIRMWARE_NOT_RETAINED')
        firmware = row['firmware_version']
    functional = record['functional']
    if (type(functional.get('status')) is not int or functional['status'] != 200
            or not re.fullmatch('[a-f0-9]{64}', functional.get('body_sha256', ''))
            or set(functional.get('section_counts', {})) != set(SECTIONS)
            or any(type(x) is not int or x != 1 for x in functional['section_counts'].values())):
        raise ValueError('EIGHT_FUNCTIONAL_SECTIONS')
    markers = functional.get('section_markers', {})
    if set(markers) != set(SECTIONS) or any(not isinstance(x, dict) or set(x) != set(SECTION_MARKERS[name])
                                         or any(v is not True for v in x.values()) for name, x in markers.items()):
        raise ValueError('SECTION_NOT_CONNECTED')
    provenance = functional.get('provenance_markers', {})
    if set(provenance) != set(PROVENANCE_MARKERS) or any(x is not True for x in provenance.values()):
        raise ValueError('FUNCTIONAL_PROVENANCE')
    if any(lines.count('LIVE_HTTP_CASE='+name+'=PASS') != 1 for name in REQUIRED_CASES):
        raise ValueError('FUNCTIONAL_SECURITY_GATES_REQUIRED')
    unit = one_record(native, 'DATA_NATIVE_RECORD=')
    if (native.splitlines()[-1] != 'DATA_NATIVE=PASS_ACTUAL_C99_UNIT_NO_DB_WRITE'
            or unit.get('source_sha256') != current_native or unit.get('database_access') is not False
            or unit.get('physical_acquisition') is not False or unit.get('cases') != ['SUP-011', 'SUP-012']):
        raise ValueError('UNIT_PROVENANCE')
    observations = unit.get('observations')
    if not isinstance(observations, list) or len(observations) != 2:
        raise ValueError('NATIVE_OBSERVATIONS')
    for item, frames, channels in zip(observations, (6, 24), (6, 1152)):
        if (set(item) != {'frames', 'channels', 'valid_zero', 'unavailable', 'stale', 'wire_sha256'}
                or item['frames'] != frames or item['channels'] != channels
                or any(type(item[k]) is not int or item[k] < 0 for k in ('frames', 'channels', 'valid_zero', 'unavailable', 'stale'))
                or item['valid_zero'] + item['unavailable'] + item['stale'] > item['channels']
                or not re.fullmatch('[a-f0-9]{64}', item['wire_sha256'])):
            raise ValueError('NONVACUOUS_NATIVE_OBSERVATIONS')
    if sum(x['valid_zero'] for x in observations) < 1 or sum(x['unavailable'] for x in observations) < 1:
        raise ValueError('NONVACUOUS_UNIT_ORACLE')
    return {'cases': ['SUP-002', 'SUP-011', 'SUP-012', 'SUP-015', 'SIM-014', 'SIM-015'],
            'review_database_access': False, 'producer_database_writes': True,
            'physical_acquisition': False, 'source_sha256': current_source,
            'native_source_sha256': current_native}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--http-log', type=Path, required=True)
    parser.add_argument('--native-log', type=Path, required=True)
    args = parser.parse_args()
    try:
        raw_http, raw_native = args.http_log.read_bytes(), args.native_log.read_bytes()
        result = review(raw_http.decode('utf-8'), raw_native.decode('utf-8'), digest(source_snapshot()), digest(native_snapshot()))
        result.update(http_log_sha256=hashlib.sha256(raw_http).hexdigest(), native_log_sha256=hashlib.sha256(raw_native).hexdigest())
        print('DATA_UI_READ_ONLY_REVIEW='+json.dumps(result, sort_keys=True))
        print('DATA_UI_REVIEW=PASS_SIX_DEDICATED_CASES_LOCAL_ONLY')
        return 0
    except (OSError, UnicodeError) as error:
        print('DATA_UI_REVIEW=BLOCKED_'+type(error).__name__)
        return 3
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, OverflowError):
        print('DATA_UI_REVIEW=FAIL_INVALID_INCOMPLETE_OR_STALE_EVIDENCE')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
