"""Independent fixed target oracle plus the PHP-verified, lease-bound preflight pin.

This consumer cannot authorize a connection: PHP must first verify runtime/service,
effective Laravel configuration, real MySQL identity/grants and fixture ownership.
No value learned from a database can create a new approved target.
"""
import json
import re

TARGETS = {
    'LOCAL_WINDOWS': {'host': '127.0.0.1', 'port': '3307',
                      'database': 'vessel_gateway_codex_test', 'username': 'vgw_codex'},
    'HOSTED_GITHUB_CI': {'host': '127.0.0.1', 'port': '3306',
                         'database': 'vessel_gateway_ci', 'username': 'root'},
}


def valid_identity(identity, profile):
    if not isinstance(identity, dict) or set(identity) != {
            'profile', 'host', 'port', 'database', 'username', 'server_fingerprint', 'lease_id', 'device'}:
        return False
    if not isinstance(identity.get('profile'), str):
        return False
    target = TARGETS.get(identity['profile'])
    return (target is not None and all(identity.get(k) == v for k, v in target.items())
            and isinstance(identity.get('server_fingerprint'), str)
            and re.fullmatch('[a-f0-9]{64}', identity['server_fingerprint']) is not None
            and isinstance(profile.get('id'), str) and re.fullmatch('[a-f0-9]{32}', profile['id']) is not None
            and identity.get('lease_id') == profile['id']
            and identity.get('device') == profile.get('device', 'runtime:demo') == 'runtime:demo')


def bind_preflight(output, env, profile):
    try:
        rows = [json.loads(line.split('=', 1)[1]) for line in output.splitlines()
                if line.startswith('LIVE_HTTP_CONFIG_AUDIT=')]
        if len(rows) != 1:
            raise ValueError()
        identity = rows[0]['identity']
        if env.get('GITHUB_ACTIONS') not in (None, '', 'false', 'true'):
            raise ValueError()
        selected = 'HOSTED_GITHUB_CI' if env.get('GITHUB_ACTIONS') == 'true' else 'LOCAL_WINDOWS'
        target = TARGETS[selected]
        if (not valid_identity(identity, profile) or identity['profile'] != selected
                or rows[0]['target'] != target
                or env.get('APP_ENV') != 'testing' or env.get('DB_CONNECTION') != 'mysql'
                or any(env.get('DB_' + key.upper()) != value for key, value in target.items())
                or env.get('VG_MYSQL_TEST_ACK') != target['database']):
            raise ValueError()
        return dict(identity)
    except (KeyError, TypeError, ValueError, AttributeError):
        # Never echo malformed records, connection values or arbitrary exception text.
        raise ValueError('VERIFIED_DATABASE_IDENTITY_PREFLIGHT_REQUIRED') from None


def audit_identity_matches(observation, profile):
    pinned = profile.get('database_identity')
    identity = observation.get('identity') if isinstance(observation, dict) else None
    return (valid_identity(pinned, profile) and valid_identity(identity, profile)
            and identity == pinned
            and observation.get('database') == pinned['database']
            and observation.get('username') == pinned['username'])
