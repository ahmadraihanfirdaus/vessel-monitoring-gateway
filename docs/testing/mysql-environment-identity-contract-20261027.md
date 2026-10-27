# Test database identity contract

This policy is test-only. It does not authorize a production database or remote
publication. Environment variables select a candidate profile; they are not proof
that a server is authorized.

| Profile | Runtime | Host | Port | Database | Account |
| --- | --- | --- | --- | --- | --- |
| LOCAL_WINDOWS | Windows PHP 8.2.35 | 127.0.0.1 | 3307 | vessel_gateway_codex_test | vgw_codex |
| HOSTED_GITHUB_CI | GitHub-hosted Linux Phase 9 job | 127.0.0.1 | 3306 | vessel_gateway_ci | root |

The independent target allowlist is fixed in `MySqlIsolation::approvedTarget` and
`scripts/live_database_identity.py`. ACK must equal the selected approved catalog;
arbitrary database/account/host/port values and URL/socket/secondary connection
overrides remain prohibited. Local testing still requires MariaDB 10.4.32 and
target-only explicit account grants. CI requires MySQL 8 in the workflow service.

Before any connection or mutation, the hosted path checks Linux, GitHub-hosted
runner context, the exact repository, workflow, job, supported trigger and public
event repository identity. The service ID comes from `job.services.mysql.id` in
the two database-using step environments. The guard independently inspects that
actual running `mysql:8.0` container using the fixed local Docker Unix socket,
requires loopback-only 3306 publication, no host binds or privileged/host network,
and the MySQL volume mount. Remote Docker endpoint/context/TLS overrides are denied.
Docker inspection requests selected fields only, never environment or mount source
paths. A read-only UUID query inside that service must match the connected TCP
server UUID; changed service or preflight identities are rejected. This is an
operational guard for an authorized ephemeral runner, not cryptographic attestation
against a malicious administrator able to replace the runner, source or Docker.

Effective Laravel connection/default/session/cache/auth configuration is checked
before PDO use. Actual MySQL version, selected catalog, CURRENT_USER, server port,
visible catalog allowlist and local grants are verified independently. The empty
migration inventory is checked before fixture creation. Schema changes use only
Laravel migrations in the approved isolated catalog.

The private HTTP preflight now provides a verified profile/target and a hash of
selected server identity fields, bound to the random fixture lease and fixed
`runtime:demo` device. Python validates this record against its fixed target map,
process configuration and ACK, then pins a copy before building or preparing any
fixture. Retry, formal and resilience read-only audits must match that same pin,
the independent allowlist, lease, device and echoed database/account. The local
fingerprint binds selected identity fields; it is not a globally unique server ID.
CI additionally binds the actual server UUID. Missing/malformed/duplicate preflight
records, target drift and cross-device proofs fail closed with fixed diagnostics.

All audits still run effective-configuration, actual-server and token ownership
checks in PHP. Retry fact counts, original metadata, exact byte retry/idempotency,
receipt HMAC/native checks, null-versus-zero, authentication and device access
assertions remain intact. No sensor values, labels, timeout or response limit change.

Regression: `scripts/test_live_database_identity.py`,
`scripts/test_live_http_integration_gate.py`,
`backend/laravel/tests/Unit/HostedMySqlServiceTest.php` and existing isolation,
ownership, access, replay/receipt and real HTTP/TLS tests. Synthetic hosted proof
tests do not claim that Docker/MySQL 8 execution passed locally. Hosted verification
requires a separately approved publication and workflow dispatch.
