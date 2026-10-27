"""Synthetic contract tests; hosted Docker/MySQL execution is not implied."""
import copy
import json
import unittest
from live_database_identity import TARGETS, audit_identity_matches, bind_preflight


class DatabaseIdentityTest(unittest.TestCase):
    def fixture(self, name='LOCAL_WINDOWS'):
        target = TARGETS[name]
        profile = {'id': 'a'*32}
        identity = dict(target, profile=name, lease_id=profile['id'], device='runtime:demo', server_fingerprint='b'*64)
        env = {'APP_ENV': 'testing', 'DB_CONNECTION': 'mysql', 'VG_MYSQL_TEST_ACK': target['database']}
        env.update({'DB_'+k.upper(): v for k, v in target.items()})
        if name == 'HOSTED_GITHUB_CI':
            env['GITHUB_ACTIONS'] = 'true'
        output = 'LIVE_HTTP_CONFIG_AUDIT='+json.dumps({'identity': identity, 'target': target})+'\n'
        return profile, identity, env, output

    def test_both_fixed_profiles_bind_to_verified_preflight(self):
        for name in TARGETS:
            with self.subTest(profile=name):
                profile, identity, env, output = self.fixture(name)
                profile['database_identity'] = bind_preflight(output, env, profile)
                self.assertTrue(audit_identity_matches(dict(identity=identity, database=identity['database'],
                                                           username=identity['username']), profile))

    def test_old_windows_only_predicate_rejects_approved_ci_identity(self):
        # Reproduces the independently observed hosted failure without a database write.
        _, identity, _, _ = self.fixture('HOSTED_GITHUB_CI')
        self.assertFalse(identity['database'] == 'vessel_gateway_codex_test' and identity['username'] == 'vgw_codex')

    def test_unknown_or_drifted_identity_fields_are_denied_after_preflight(self):
        for name in TARGETS:
            profile, identity, env, output = self.fixture(name)
            profile['database_identity'] = bind_preflight(output, env, profile)
            for field, bad in {'profile': 'OTHER', 'host': 'localhost', 'port': '3308', 'database': 'vessel_gateway',
                               'username': 'other', 'server_fingerprint': 'c'*64, 'device': 'another-device',
                               'lease_id': 'c'*32}.items():
                with self.subTest(profile=name, field=field):
                    changed = dict(identity, **{field: bad})
                    observation = dict(identity=changed, database=changed['database'], username=changed['username'])
                    self.assertFalse(audit_identity_matches(observation, profile))

    def test_unpinned_or_mutually_changed_preflight_and_audit_cannot_authorize_target(self):
        profile, identity, env, output = self.fixture()
        self.assertFalse(audit_identity_matches(dict(identity=identity), profile))
        identity['database'] = 'vessel_gateway'
        profile['database_identity'] = identity
        self.assertFalse(audit_identity_matches(dict(identity=identity, database='vessel_gateway', username='vgw_codex'), profile))

    def test_configuration_and_ack_must_agree_with_fixed_target_before_fixtures(self):
        for name in TARGETS:
            profile, _, env, output = self.fixture(name)
            for key in ['APP_ENV', 'DB_CONNECTION', 'DB_HOST', 'DB_PORT', 'DB_DATABASE', 'DB_USERNAME', 'VG_MYSQL_TEST_ACK']:
                with self.subTest(profile=name, key=key):
                    with self.assertRaisesRegex(ValueError, '^VERIFIED_DATABASE_IDENTITY_PREFLIGHT_REQUIRED$'):
                        bind_preflight(output, dict(env, **{key: 'unapproved'}), profile)

    def test_ci_record_cannot_be_selected_on_local_profile(self):
        profile, _, env, output = self.fixture('HOSTED_GITHUB_CI')
        env.pop('GITHUB_ACTIONS')
        with self.assertRaises(ValueError):
            bind_preflight(output, env, profile)

    def test_missing_duplicate_malformed_or_extra_identity_fields_fail_closed(self):
        profile, identity, env, output = self.fixture()
        bad = copy.deepcopy(identity)
        bad['extra'] = 'synthetic-sensitive-marker'
        for text in ['', output+output, 'LIVE_HTTP_CONFIG_AUDIT=not-json',
                     'LIVE_HTTP_CONFIG_AUDIT='+json.dumps({'identity': bad, 'target': TARGETS['LOCAL_WINDOWS']})]:
            with self.subTest(record=text[:24]), self.assertRaisesRegex(ValueError, '^VERIFIED_DATABASE_IDENTITY_PREFLIGHT_REQUIRED$'):
                bind_preflight(text, env, profile)

    def test_echoed_database_or_account_cannot_differ_from_attested_identity(self):
        profile, identity, env, output = self.fixture()
        profile['database_identity'] = bind_preflight(output, env, profile)
        for fields in [{'database': 'vessel_gateway'}, {'username': 'root'}]:
            value = dict(identity=identity, database=identity['database'], username=identity['username'])
            value.update(fields)
            self.assertFalse(audit_identity_matches(value, profile))


if __name__ == '__main__':
    unittest.main(verbosity=2)
