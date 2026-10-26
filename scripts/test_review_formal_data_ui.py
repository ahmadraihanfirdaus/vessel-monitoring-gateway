"""Adversarial evidence review; fixtures here never represent actual runtime PASS."""
import copy
import json
import unittest

from data_ui_contracts import SECTIONS, SECTION_MARKERS, PROVENANCE_MARKERS
from review_formal_data_ui import review, REQUIRED_CASES


class EvidenceReviewTest(unittest.TestCase):
    def fixture(self):
        labels = ('src-simulation', 'src-bench_test', 'src-physical', 'dedup', 'authbad')
        before = {key: dict(count=0, rows=[]) for key in labels}
        after = copy.deepcopy(before)
        for key in labels[:-1]:
            after[key] = dict(count=1, rows=[dict(source_mode=key[4:] if key.startswith('src-') else 'simulation',
                schema_version='1.0', firmware_version='synthetic', uptime_ms='200', channel_count=1,
                quality='valid', value=42)])
        record = dict(version=1, source_sha256='a'*64, physical_acquisition=False,
            producer='actual_loopback_tls_php_mariadb_owned_fixture_writes',
            source_statuses=dict(simulation=201, bench_test=201, physical=201), source_rejected=[422, 422],
            dedup_statuses=[201, 200, 409], auth_statuses=[401, 401], database_before=before, database_after=after,
            functional=dict(status=200, body_sha256='b'*64, section_counts=dict.fromkeys(SECTIONS, 1),
                section_markers={name: dict.fromkeys(markers, True) for name, markers in SECTION_MARKERS.items()},
                provenance_markers=dict.fromkeys(PROVENANCE_MARKERS, True)))
        unit = dict(source_sha256='c'*64, database_access=False, physical_acquisition=False,
            cases=['SUP-011', 'SUP-012'], observations=[dict(frames=6, channels=6, valid_zero=0, unavailable=2, stale=1, wire_sha256='d'*64),
                dict(frames=24, channels=1152, valid_zero=166, unavailable=173, stale=68, wire_sha256='e'*64)])
        return record, unit

    def logs(self, record, unit):
        names = REQUIRED_CASES
        http = '\n'.join('LIVE_HTTP_CASE='+name+'=PASS' for name in names)+'\n'
        http += 'DATA_UI_RECORD='+json.dumps(record)+'\n'
        http += 'LIVE_HTTP_CLEANUP=PASS_EXACT_OWNERSHIP_ZERO_APPLICATION_ROWS\n'
        http += 'LIVE_HTTP_SOURCE_STABILITY=PASS_SHA256_'+'a'*64+'\n'
        http += 'LIVE_HTTP_GATE=PASS_LOCAL_ONLY_HARDWARE_DEPLOYED_TLS_NOT_RUN\n'
        native = 'DATA_NATIVE_RECORD='+json.dumps(unit)+'\nDATA_NATIVE=PASS_ACTUAL_C99_UNIT_NO_DB_WRITE\n'
        return http, native

    def test_complete_synthetic_record_is_parsed_without_database(self):
        result = review(*self.logs(*self.fixture()), 'a'*64, 'c'*64)
        self.assertFalse(result['review_database_access'])
        self.assertTrue(result['producer_database_writes'])

    def test_status_only_fabrication_cannot_replace_direct_row_proof(self):
        for changed in ('count', 'value', 'mode', 'auth', 'freshness'):
            record, unit = self.fixture()
            if changed == 'count': record['database_after']['dedup']['count'] = 2
            if changed == 'value': record['database_after']['dedup']['rows'][0]['value'] = 43
            if changed == 'mode': record['database_after']['src-physical']['rows'][0]['source_mode'] = 'simulation'
            if changed == 'auth': record['database_after']['authbad']['count'] = 1
            if changed == 'freshness': record['database_before']['dedup']['count'] = 1
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                review(*self.logs(record, unit), 'a'*64, 'c'*64)

    def test_missing_duplicate_placeholder_section_and_marker_fail(self):
        for changed in ('missing', 'duplicate', 'bool', 'false_marker', 'missing_marker', 'provenance'):
            record, unit = self.fixture(); page = record['functional']
            if changed == 'missing': del page['section_counts']['Safety']
            if changed == 'duplicate': page['section_counts']['Safety'] = 2
            if changed == 'bool': page['section_counts']['Safety'] = True
            if changed == 'false_marker': page['section_markers']['Safety']['bilge_state'] = False
            if changed == 'missing_marker': del page['section_markers']['Safety']['bilge_state']
            if changed == 'provenance': page['provenance_markers'] = {}
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                review(*self.logs(record, unit), 'a'*64, 'c'*64)

    def test_drift_truncation_failures_duplicate_record_and_cleanup_are_refused(self):
        http, native = self.logs(*self.fixture())
        for bad in (http.replace('a'*64, 'f'*64), http+'FAIL=FAIL\n', http+'EXTRA\n',
                    http.replace('LIVE_HTTP_CLEANUP=', 'MISSING_CLEANUP='),
                    http.replace('DATA_UI_RECORD=', 'DATA_UI_RECORD={}\nDATA_UI_RECORD=')):
            with self.subTest(bad=bad[:20]), self.assertRaises(ValueError):
                review(bad, native, 'a'*64, 'c'*64)

    def test_native_nonvacuous_zero_null_and_provenance_required(self):
        for change in ('zero', 'unavailable', 'source', 'db', 'bool', 'count', 'impossible_count'):
            record, unit = self.fixture()
            if change == 'zero':
                for observation in unit['observations']: observation['valid_zero'] = 0
            if change == 'unavailable':
                for observation in unit['observations']: observation['unavailable'] = 0
            if change == 'source': unit['source_sha256'] = 'f'*64
            if change == 'db': unit['database_access'] = True
            if change == 'bool': unit['observations'][0]['frames'] = True
            if change == 'count': unit['observations'].pop()
            if change == 'impossible_count': unit['observations'][0]['valid_zero'] = 7
            with self.subTest(change=change), self.assertRaises(ValueError):
                review(*self.logs(record, unit), 'a'*64, 'c'*64)

    def test_duplicate_fields_nonfinite_and_unperformed_gate_cannot_pass(self):
        http, native = self.logs(*self.fixture())
        for bad in (http.replace('"version": 1', '"version": 1,"version": 1'),
                    http.replace('"value": 42', '"value": NaN'),
                    http.replace('LIVE_HTTP_CASE=TLS_WRONG_HOST_REJECTED=PASS\n', ''),
                    http.replace('=PASS_LOCAL_ONLY', '=NOT_RUN_LOCAL_ONLY'),
                    http.replace('USER_DISABLE_EFFECTIVE_NEXT_REQUEST=PASS', 'USER_DISABLE_EFFECTIVE_NEXT_REQUEST=BLOCKED')):
            with self.subTest(bad=bad[:20]), self.assertRaises(ValueError):
                review(bad, native, 'a'*64, 'c'*64)


if __name__ == '__main__':
    unittest.main()
