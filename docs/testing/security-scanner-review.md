# Scoped security scanner review

The original 36 scanner occurrences are classified in [triage CSV](../../evidence/test-results/security-36-triage-20261025.csv). These are occurrences across index/working layers, not 36 independent vulnerabilities. The scope identifies 32 informational false positives, two low-risk synthetic CI-key occurrences, and two medium-risk CI-configuration occurrences. No critical/high vulnerability or actual credential disclosure was identified in that reviewed set. This is not an assessment of every possible dependency, deployment or hardware vulnerability.

The six related work areas are classification, assignment parsing, bounded text coverage, exact non-secret/metadata review, explicit PHP/runtime isolation, and integrated regression/evidence. LOCKED requirements, formal result tables, production services and firmware interfaces are unchanged.

## Scanner behavior and reviewed records

- PHP `=>` is parsed as one assignment operator. Empty/null values and external references remain distinguishable from hardcoded literals. An `env()` call containing a nonempty literal fallback is screened; direct PHP literals are still rejected.
- Recognized framework/configuration/lock/hash text passes through the same UTF-8, binary/NUL, size and credential/privacy checks. Unsupported formats and symlinks still fail. Recognizing a text filename does not exempt its contents.
- `scripts/security-reviewed-findings.json` documents exact reviewed non-secret assignments using path, whole-file SHA-256, line SHA-256, classification and rationale. There are no directory/wildcard exemptions. Changed bytes invalidate the record. Malformed registries, sensitive paths and unknown classifications fail closed.
- Assignment review never waives credential tokens, private-key headers, URL credentials or operational privacy warnings. URL screening now includes HTTP(S)/FTP credentials as well as database/service URLs.
- Recognizing `composer.lock` exposed 141 author-email occurrences previously hidden by the unsupported-format finding. Fifty-three distinct line fingerprints cover those repeated upstream metadata values in the unchanged reviewed lockfile. The scanner verifies JSON pointers under `packages[]/authors[]/email` or `packages-dev[]/authors[]/email`, a recorded public GitHub package source, whole-file/line hashes and an isolated email field. Root/contact fields, non-array author structures, unknown files and changed metadata are not approved. No author address is copied into the triage/report.
- Reviewed assignments and metadata counts remain visible in output. Zero unresolved findings is content-screening success, not publication authorization or a confidentiality guarantee.

The P1 framework review still checks exact framework bytes and semantic lines. Its database configuration hash/line were stale relative to the authoritative B46 HEAD after P2 removed the MySQL credential fallback. Those two pins were reconciled after checking byte equality with HEAD and the required environment lookup. No database configuration or credential fallback was changed. The old rule requiring exactly twelve unresolved findings was replaced with the current zero-unresolved scanner result. Failed historical-pin attempts remain in evidence.

## Runtime and database boundaries

Local PHP tests use `C:/tools/php-8.2.35/php.exe` explicitly. `run_mysql_integration.py --php-binary` and `VG_PHP_CLI` select the child executable without altering global PATH or XAMPP. A missing selected binary is BLOCKED; it does not fall back.

The approved database remains `127.0.0.1:3307/vessel_gateway_codex_test`, account `vgw_codex`, MariaDB 10.4.32 through PDO/mysql. The ignored backend testing file is explicitly selected and never copied. Preflight checks effective Laravel/PHPUnit overrides, testing mode, actual server account/catalog/port/version, grants and empty application tables. The ordinary `.env` is not read by the test harness.

The file-based testing APP_KEY is empty. The controlled test runner generates a fresh cipher-compatible key in process memory, records only its source/validity, and leaves the file unchanged. Direct interactive startup using only that unfilled file still requires a separately configured valid test key. No key/password value is printed. The CI DB-free job similarly generates a per-job key; its generator was exercised locally, but hosted execution is NOT_RUN. The ephemeral database service port is bound to loopback.

An explicit `--existing-schema --migration-roundtrip` mode admits only the exact known migration inventory with zero application rows and no extra routines/events/triggers before rollback/reapply through Laravel migrations. Populated-catalog admission has a real transactional negative test. There is no migrate:fresh/reset operation or manual SQL DDL. Exclusive use of the isolated test database remains a precondition.

## Commands and limitations

```text
python -B scripts/test_audit_precommit_security.py
python -B scripts/audit_precommit_security.py
python -B scripts/audit_phase9_p1_security_review.py
python -B scripts/run_mysql_integration.py --php-binary C:/tools/php-8.2.35/php.exe --testing-env --execute --existing-schema --migration-roundtrip
```

For Python scripts that invoke PHP, set the child-process `VG_PHP_CLI` to the same explicit executable. See [current execution evidence](../../evidence/test-results/security-php8235-summary-20261025.md) for actual outcomes and retained failures. Firmware hardware, ESP32/NVS durability, hosted CI, direct MySQL 8, deployed TLS, online dependency-advisory checks and dedicated remaining SIM/SUP protocols are not established by these gates.
