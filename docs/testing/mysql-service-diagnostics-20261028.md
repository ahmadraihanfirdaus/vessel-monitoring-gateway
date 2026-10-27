# Hosted MySQL service proof diagnostics

Scope: test-only service admission. This is a diagnostic checkpoint; the internal
cause of run [40547241521](https://github.com/ahmadraihanfirdaus/vessel-monitoring-gateway/actions/runs/40547241521)
is **UNKNOWN**. The published parent is `b7a3f06d3820161f052e1bc5a3618ae59dc46c94`.

Read-only log review found one MySQL 8 container creation command, the expected
loopback publication, no explicit mount flag, and one forwarded 64-hex service ID
matching the container ID at cleanup. These facts do not prove Docker inspect,
JSON decoding, the UUID query or all inspected properties succeeded. The previous
outer catch collapsed those paths into `isolated service identity unavailable`.
Context admission preceded that catch. Laravel/PDO admission, migrations, fixtures
and HTTP/retry/formal/resilience integration did not run in that hosted job.

[GitHub's job context](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#job-context)
defines `job.services.<service_id>.id` as the service container ID. The unchanged
workflow passes it through step-level `VG_CI_MYSQL_CONTAINER_ID` in both DB-using
steps. [Docker inspect](https://docs.docker.com/reference/cli/docker/inspect/)
documents Go-template formatting for selected fields. There is no raw inspect response or
command stderr in the existing evidence, so no individual command/template or
property failure is claimed as confirmed.

| Static reason | Failure boundary |
| --- | --- |
| SERVICE_CONTAINER_ID_MISSING | Missing/empty expected service ID, before event or command access |
| DOCKER_INSPECT_FAILED | Inspect command exception, nonzero exit, timeout or output bound |
| DOCKER_INSPECT_JSON_INVALID | Decode failure or non-object root; no UUID query follows |
| SERVICE_PROPERTY_MISMATCH | Fixed image/running/binds/privileged/network/mount/port constraint |
| MYSQL_UUID_QUERY_FAILED | Read-only UUID command failure, timeout or output bound |
| MYSQL_UUID_INVALID | UUID value/type does not match the existing exact format |
| SERVICE_IDENTITY_MISMATCH | Invalid/mismatched container ID, or preflight/service/TCP UUID drift |

Messages contain only `MYSQL_TEST_BLOCKED:`, one fixed reason and optional fixed
property category: IMAGE, RUNNING, BINDS, PRIVILEGED, NETWORK, MOUNTS, PORT_BINDING
or EXTRA_PUBLICATION. They never include inspected values, stderr, environment,
credentials, private paths, command exceptions or exception chains. Existing CLI
gate catch expressions preserve these messages; both actual entrypoints are tested
in ephemeral always-deny child processes before any database/app bootstrap.

Authorization remains unchanged: fixed local/hosted targets and ACK, effective
Laravel configuration, actual MySQL identity/catalog/grants, Linux/GitHub-hosted
workflow/job/event context, actual container proof via the fixed local socket,
server UUID comparison, ownership/token/lease/device and receipt/metadata/replay
semantics. There is no environment-controlled executor or fake runtime mode. The
IO seam is private and used only via reflection in deterministic unit tests; real
`verify` always selects the actual command implementation.

Command arrays, selected-fields template, 5-second command timeout and 8192-byte
output bound are unchanged. No timeout/cap increase or guard relaxation is included.
An independently reproduced local negative case exposed a PHP warning when ports
was a scalar; an explicit array check now rejects that case without warning. This
is not evidence that the hosted response had that malformed value. A 234-case
comparison found no acceptance differences against the published policy.

Tests: new `HostedMySqlDiagnosticsTest` covers all seven reasons, all eight fixed
property categories, ordering/stop-on-error, command failure/timeout/output limits,
redaction and both CLI error boundaries. Existing `HostedMySqlServiceTest` and
`MySqlIsolationTest` remain. Actual Docker/MySQL 8 execution is NOT_RUN locally;
injected IO is not a substitute for hosted verification. Regression runs use the
approved isolated Windows MariaDB catalog, never production or SQLite.

Public gate summary: `evidence/test-results/mysql-service-diagnostics-20261028.json`.
Scope manifest: `evidence/test-results/mysql-service-diagnostics-files-20261028.csv`.
New publication and one controlled hosted run require separate approval. If a
reason appears, inspect only that proven boundary; retain fail-closed behavior.
