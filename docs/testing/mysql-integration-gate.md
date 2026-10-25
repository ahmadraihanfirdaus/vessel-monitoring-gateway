# Guarded C99 / Laravel / MySQL integration gate

Source baseline: `develop` at `231cc2b2022223b47790347a5fecf71eb0ee2c44` (B46).
This is development integration tooling, not formal SIM/SUP execution or hardware evidence.

## Related scopes and dependency order

1. Admit explicit test-only configuration and the approved engine/catalog/account before connecting test traits or writing fixtures. Reject ordinary dotenv fallback, cached app state, URL/socket/read-write overrides, unrelated catalog grants and populated application tables. Local MariaDB and ephemeral CI MySQL have separate profiles.
2. Preserve existing backend tests with transactional fixtures. Replace `RefreshDatabase` schema resets with `DatabaseTransactions` and a guarded `MySqlTestCase`.
3. Reuse existing B14/B15 C99 serializers to exercise real Laravel authentication, HTTP middleware, validation, services, MySQL persistence, replay/conflict, state/history/health, null/zero, uint64 limits, event identities and source provenance. No service/authentication doubles in `FirmwareMySqlIntegrationTest`.
4. Apply migrations only to an initially empty admitted catalog. Optional rollback/reapply affects only the four migrations just applied to that empty catalog. Verify table inventories after each phase. No database creation, direct DDL, SQL seeding, fresh/reset command, or real-data operation.
5. Wire the ephemeral MySQL CI job through the same runner. Generate B14/B15 inputs and B17 receipt destination before the full suite, then crosscheck exported HTTP receipts with C99.
6. Reconcile README/living status with actual source and preserve formal result tables, LOCKED hashes, and hardware limitations.

## Local prerequisites and execution

PHP 8.2+ with required Laravel/PHPUnit extensions including `pdo_mysql`, installed Composer dependencies, Python 3, and native GCC on PATH are required. Provisioning is outside this runner. The ordinary `.env` is never loaded. By default, configuration comes only from the process/PHPUnit environment. The explicit `--testing-env` option loads the user-approved ignored `.env.testing` inside PHP memory; it never copies the file or emits password/APP_KEY values. `tests/bootstrap.php` enables the same controlled loader for PHPUnit when `VG_USE_TESTING_ENV=1`.

The user-corrected local profile is `APP_ENV=testing`, `DB_CONNECTION=mysql`, `DB_HOST=127.0.0.1`, `DB_PORT=3307`, `DB_DATABASE=vessel_gateway_codex_test`, `DB_USERNAME=vgw_codex`, MariaDB `10.4.32-MariaDB`, and an explicit `DB_PASSWORD` (even if empty). Process-only admission requires `VG_MYSQL_TEST_ACK=vessel_gateway_codex_test`; explicit testing-file selection supplies that acknowledgement only when absent. Earlier suggested `vessel_monitoring_gateway_test` / `vg_gateway_test` targets were not approved and are rejected. MySQL 8-only admission was a runner assumption, not a LOCKED requirement.

`DB_URL`, `DATABASE_URL` and `DB_SOCKET` must be unset or empty. Conflicting values in process environment, `$_ENV`, or `$_SERVER` are refused before connecting. Preflight uses the installed PHPUnit XML loader/handler (including force/server settings), compares effective Laravel configuration, and then checks `DATABASE()`, `CURRENT_USER()`, engine, port and grants. The local account must have only global USAGE and target-catalog grants, without GRANT OPTION or roles. MariaDB's visible default `test` catalog is accepted only alongside these independently verified grant restrictions; no data in that catalog is accessed. Other unrelated catalogs remain rejected. An acknowledgement/name is an operator assertion, not independent proof of data provenance. Never point it at a real-data instance.

In GitHub Actions only, the existing job's ephemeral `mysql:8.0` service uses the alternate `vessel_gateway_ci` catalog on port 3306 and its job-local account. Hosted execution has not been observed in this local session.

From repository root:

```text
python -B scripts/test_mysql_integration_gate.py
php backend/laravel/vendor/bin/phpunit -c backend/laravel/phpunit.xml --testsuite Unit --do-not-cache-result
python -B scripts/run_mysql_integration.py --php-binary C:/tools/php-8.2.35/php.exe --testing-env
python -B scripts/run_mysql_integration.py --php-binary C:/tools/php-8.2.35/php.exe --testing-env --execute --migration-roundtrip
```

The third command is read-only and requires an initially empty catalog. The fourth explicitly permits migration apply/rollback/reapply and transactional synthetic fixtures only after preflight. Exit 3 means BLOCKED; exit 1 means executed tests failed. Output includes nonsecret target details, override names, counts and status; it excludes SQL bindings, password and APP_KEY. Execution leaves the migrated empty schema in place; a second migration run refuses that existing schema rather than resetting it. No automatic cleanup/reset is attempted. Do not run against a shared or concurrently used test catalog; exclusive use is an operator precondition, not a concurrency guarantee.

After execution, select the explicit PHP 8.2.35 binary with `VG_USE_TESTING_ENV=1` on `scripts/mysql_test_gate.php --inspect` for read-only inventory/zero-row checks. `--execute --existing-schema` runs tests without migrations; adding `--migration-roundtrip` permits verified rollback/reapply only after exact inventory, zero-row and extra-object admission. Populated-catalog rejection has a real transactional negative test. No fresh/reset operation is used. The runner selects PHP explicitly without global PATH/XAMPP changes and generates a fresh cipher-compatible application key only in process memory; the file-only testing key remains unfilled.

DB-backed tests now require this migrated empty test schema even when invoked directly with PHPUnit. All fixture rows roll back after each test. Missing dependencies are not skipped or converted into success.

## Current evidence and remaining gaps

See the [latest device read integration](../../evidence/test-results/device-read-summary-20261025.md), [PHP 8.2.35/security record](../../evidence/test-results/security-php8235-summary-20261025.md), [earlier MariaDB execution](../../evidence/test-results/mariadb-integration-summary-20261025.md), and [initial checkpoint](../../evidence/test-results/mysql-integration-gate-20261025.md). Verified migration roundtrip, 251 Laravel/PHPUnit tests without failures/skips, and receipt crosscheck PASS on approved local MariaDB. MySQL 8/hosted CI remain NOT_RUN. Security content checks follow the [review protocol](security-scanner-review.md).

In-process Laravel HTTP dispatch is not a network listener/TLS test. The integration gate does not close SIM-014, SIM-015, SUP-014, SUP-017 or SUP-018. `DeviceReadService` still defines state/history by server receipt ordering; cross-boot device chronology is unresolved. Dashboard views remain unconnected. Real ESP32 Wi-Fi/TLS, filesystem/NVS durability, crash/power-loss recovery, external trusted generation floors, hardware key storage, concurrent storage CAS and physical bench remain unverified.
