# Approved MariaDB integration execution — 2026-10-25 (Asia/Jakarta)

Historical checkpoint retained. The subsequent [PHP 8.2.35/security continuation](security-php8235-summary-20261025.md) records 215 tests, explicit runtime selection and current security content clearance. Failed/blocked results below describe this earlier checkpoint.

Source baseline remains `develop` at `231cc2b2022223b47790347a5fecf71eb0ee2c44`. This record describes the current uncommitted worktree and supplements the [initial blocked checkpoint](mysql-integration-gate-20261025.md). Earlier code and evidence are preserved; no source reset, remote operation, or direct schema edit occurred.

## User-corrected authority and read-only admission

The user explicitly identified the approved isolated target as `127.0.0.1:3307`, `vessel_gateway_codex_test`, account `vgw_codex`, MariaDB `10.4.32`, with credentials in the Git-ignored local `backend/laravel/.env.testing`. The earlier `vessel_monitoring_gateway_test` / `vg_gateway_test` suggestions were not approved. The earlier MySQL 8-only restriction was an implementation assumption, not a LOCKED requirement; it was replaced with separate approved-local-MariaDB and ephemeral-CI-MySQL profiles. This does not claim direct MySQL 8 execution.

The initial read-only check found no process APP/DB overrides, confirmed the testing file exists, is ignored and untracked, and examined PHPUnit's 13 environment entries (all `force=false`) with no server overrides. The installed PHPUnit XML loader/handler is now reused by preflight, so its precedence matches the subsequent test process. Process environment, `$_ENV`, `$_SERVER`, PHPunit XML force/server settings, effective Laravel driver/target and cached app paths are checked before database access. An initial diagnostic used the wrong PHPUnit loader namespace and stopped before connecting; correcting it to the installed `PHPUnit\TextUI\XmlConfiguration\Loader` completed the probe without emitting exception contents.

Effective Laravel configuration matched the approved host, port, database and account. The password matched the testing-file source in memory. Password and APP_KEY values were never emitted or copied into evidence. `DATABASE()`, `CURRENT_USER()`, `VERSION()` and `@@port` independently confirmed the target. The catalog was initially empty.

MariaDB also exposed its default `test` catalog. A read-only grant inspection established global USAGE plus privileges only on the approved test catalog, with no GRANT OPTION or role grants. The local guard now verifies that restriction independently before accepting visibility of this one known default catalog. Unknown catalogs, explicit grants to `test` or other catalogs, global privileges, roles and GRANT OPTION are rejected. No tables/data in other catalogs were read or changed; no grants/accounts were altered.

`--testing-env` is explicit opt-in to reading the approved ignored testing file in PHP memory. The ordinary `.env` remains unused. Conflicting connection overrides are rejected rather than overwritten. Runtime cache/session/queue/log settings and the synthetic application key are test-scoped; audit output lists names, not secret values. The source `phpunit.xml` now uses the controlled test bootstrap. Effective application mode must be `testing`.

## Executed database gates

Command from repository root, with native GCC's directory prepended only to the child process PATH:

```text
python -B scripts/run_mysql_integration.py --testing-env --execute --migration-roundtrip
```

The user authorized migrations/testing after isolation PASS. Actual output is in [execution log](mariadb-integration-execution-20261025.txt):

| Gate | Actual result |
|---|---|
| Initial identity/configuration/grants/empty-catalog admission | PASS |
| Original B14 telemetry and B15 event C99 fixture generation | PASS; 2 telemetry and 4 event wires |
| Laravel migration apply | PASS; four migrations, five tables including repository |
| Laravel migration rollback | PASS; only empty migration repository remains |
| Laravel migration reapply | PASS; expected table inventory restored |
| Full Laravel/PHPUnit suite | PASS 214 tests; zero failed and zero skipped |
| New real firmware-wire integration methods | PASS 8, included in 214; real authentication/services/database, no mocks |
| PHPUnit unit suite | PASS 88 tests / 159 assertions, included in 214 |
| Laravel receipt to C99 ACK crosscheck | PASS |
| Ignored testing configuration file | Unchanged before/after execution |

Database fixtures are synthetic and transaction-scoped; no manual SQL DDL, migrate:fresh, schema reset, production credentials, real-data seeding or production data access is used. Four existing migration source files are unchanged.

After tightening the effective-app-environment check, the full suite was rerun against the existing migrated empty schema, with fresh temporary C99 fixtures and the same guarded PHPUnit bootstrap. No repeated migration reset was needed. See [final regression](mariadb-final-regression-20261025.txt).

The [first existing-schema rerun](mariadb-final-regression-attempt1-20261025.txt) omitted the runner's test-key override and reported one error in the root-page example (`Illuminate\Encryption\MissingAppKeyException`); 214 cases executed with no skips. A one-case isolated diagnostic confirmed the missing-key error without exposing its value. The approved testing file's APP_KEY entry is unfilled; it was not edited. Repeating the suite with an ephemeral valid process-only application key yielded **214/214 PASS, zero failures/skips**, plus **8/8 receipt crosscheck PASS**. The main migration runner's initial 214-test PASS already used its valid test-scoped application key. This runtime override and the initial error are retained explicitly; no test was removed or skipped.

Read-only `php scripts/mysql_test_gate.php --inspect` with `VG_USE_TESTING_ENV=1` verifies exactly five tables, the four expected migration records, and zero rows in devices, telemetry_samples, telemetry_channels and monitoring_events. Live negative probes for the rejected old database, rejected old username, wrong port and URL override all refused admission with exit 3 before connecting/writing. See [postcheck and rejection log](mariadb-isolation-postcheck-20261025.txt).

## Regression, scope and commit gates

The focused [runner/lint log](mariadb-focused-20261025.txt) records 15 runner safety tests, PHP syntax checks and Python compilation. New policy tests cover all three override layers, missing/incorrect file fields, wrong engine/version/catalog, credential-source conflicts, excess grants and denial-message redaction. Existing firmware results from the initial checkpoint remain 83 B46 / 53 B45 / 57 B44 and 226 core native cases PASS; firmware source is unchanged and those suites were not unnecessarily repeated for the database-profile correction.

The [42 policy/traceability/source scripts](mariadb-policy-20261025.txt) PASS. The [candidate security screen](mariadb-security-20261025.txt) returns **REVIEW_REQUIRED, exit 1, 36 findings**. These include inherited framework/CI/text-format indicators and validation/fixture literals; the scanner's nonzero result is retained. No security allowlist or scanner bypass was introduced. Security review remains an unmet mandatory commit gate.

Final [database/worktree integrity](mariadb-final-integrity-20261025.txt) confirms zero application rows, the exact migration inventory, unchanged LOCKED/formal result files, empty index, unchanged protected firmware hashes and ignored/untracked testing configuration. The [scanner's own four regression cases](mariadb-security-regression-20261025.txt) PASS; that does not clear the 36 candidate findings. Final scoped review confirms only test support/runner/bootstrap, policy/documentation and evidence changes; production services, firmware and migration source files are untouched.

**Decision: NO STAGING / NO COMMIT.** Functional database gates PASS, but the mandatory security screen is not cleared. HEAD remains the B46 baseline. No hosted-CI or formal SIM/SUP result is inferred from local execution. The current [file/hash manifest](mysql-integration-files-20261025.csv) describes the accumulated scoped worktree; ignored credentials and preexisting user files are excluded.

## Remaining verification limits

The selected local engine is MariaDB 10.4.32 through Laravel's mysql/PDO driver. Direct MySQL 8, hosted GitHub Actions, actual HTTP listener/TLS deployment, cross-boot chronology, connected dashboard, ESP32 transport, NVS/filesystem/crash durability, key storage, hardware bench and remaining formal SIM/SUP protocols remain NOT_RUN or unresolved. Formal result CSVs and LOCKED requirements/mappings are unchanged. Overall system PARTIAL; final requirement approval NOT_APPROVED.
