# Guarded integration execution record — 2026-10-25 (Asia/Jakarta)

Historical initial checkpoint. The user subsequently supplied the approved MariaDB target and explicitly authorized reading its ignored testing configuration. See the [current execution record](mariadb-integration-summary-20261025.md): the database/migration blockers below have been resolved for that MariaDB profile. Original failed/blocked results are retained as history; they are not the current local database outcome.

**Decision: INCOMPLETE / NO COMMIT.** Mandatory real MySQL 8 persistence and migration roundtrip gates are BLOCKED. No push or remote action. Evidence describes the B46 baseline plus the scoped uncommitted worktree; it is not evidence for a new committed HEAD.

## One-time read-only baseline

- Branch `develop`, HEAD `231cc2b2022223b47790347a5fecf71eb0ee2c44`; matches supplied B46 reference. Initially no tracked changes and empty index diff.
- Preexisting untracked files: `AGENTS.md`, `firmware/.gitignore`, `firmware/.vscode/extensions.json`. Preserved, excluded from batch/staging.
- Firmware file SHA-256 before work: `.gitignore` = `d952abf002d5e1ec80c8ab1bfc9f38eb5b62fc310667d501cb2ce9f21c3effb2`; `.vscode/extensions.json` = `31cc8f05084d96b65be8f147533017c7a1b89b055d85886a2e4ab3ce532f34fb`.
- Read requirements/matrix, architecture/ICD, roadmap, ADR runtime boundary, formal protocol records, living traceability, firmware host/main sources, backend auth/ingest/read services, dashboard placeholders, tests, CI and relevant historical evidence. Internal LOCKED Blueprint is not distributed in this public repository; no requirements or hardware assumptions were invented.
- Verified 38 mappings and LOCKED hashes with `scripts/check_living_traceability.py`. CSV records SIM-001..009 PASS, SIM-010..015 NOT_RUN; five SUP PASS and fourteen PLANNED. Reference suggestion that all SUP remain open was stale.
- README/living implementation statuses incorrectly retained Phase 9 / network / UI / CI NOT_STARTED despite existing source. Historical evidence and source presence are not newly executed backend integration.
- PHP 8.2.12 has `pdo_mysql`, mbstring, DOM/XML and other PHPUnit dependencies. Composer 2.8.9 vendor autoload exists; Laravel v12.70.0; PHPUnit 11.5.57; Python 3.12.10; GCC 16.2.0 via `C:/msys64/ucrt64/bin`; Git 2.51.0.windows.2. Installed SQL client identifies MariaDB 10.4.32, not MySQL 8. No Docker command or MySQL listeners on 3306/3307 detected. No dotenv, credentials or environment dump read/recorded. An initial PHP metadata probe had a shell-quoting parse error; the corrected stdin probe returned the Laravel version above.

## Batch objective and files

Six related scopes: test isolation guard; transactional backend tests; real C99-wire/MySQL integration assertions; migration-only empty-catalog gate; CI fixture/receipt wiring; status/evidence reconciliation. See [gate protocol](../../docs/testing/mysql-integration-gate.md). The [SHA-256 file manifest](mysql-integration-files-20261025.csv) enumerates exact scoped files, excluding itself and preexisting user files.

Changed production behavior: none. Test support and CI preparation change; mandatory MySQL regression is still required before commit. Existing DB tests now require a pre-migrated empty isolated schema and rollback synthetic fixture rows instead of resetting tables. No migrations or production services were modified.

## Executed checks

Commands run from repository root unless stated. For native runs only, prepend `C:/msys64/ucrt64/bin` to process PATH. Only synthetic C99 fixture payloads are used.

| Command / gate | Actual outcome | Boundary |
|---|---|---|
| `python -B scripts/test_phase9_b46_stage_readback.py` | PASS 83 cross-process cases | Host-only; no durable storage |
| `python -B scripts/test_phase9_b45_slot_recovery.py` | PASS 53 cross-process cases | Host-only authenticated slot selection |
| `python -B scripts/test_phase9_b44_nonce_snapshot.py` | PASS 57 cross-process cases | Host-only snapshot oracle |
| `python -B scripts/test_firmware_core_host.py` | PASS 226/226; parser 5/5 | Native C; no fresh Wokwi/ESP32 run |
| NET-001 / SYS-003 host tests | PASS 6 + 4 tests | Injected host callbacks only |
| UI-001 / UI-002 source and PHP label tests | PASS 4 + 4 tests | No browser/device-data rendering |
| `test_phase9_tst002_ci_policy.py` | PASS 4 tests | Workflow source; not hosted CI |
| Real Laravel/PHPUnit DB-free regression | PASS 116 tests; 0 failed; 0 skipped | Actual in-process HTTP dispatch; persistence/auth doubles in existing tests |
| B14/B15 C99 fixture generation | PASS 2 telemetry + 4 event wires | Reused existing serializers; exact raw bytes |
| B17 Laravel receipt / C99 crosscheck | PASS 8 cases: 4 conditionally eligible, 4 held | DB-free; no TLS/durable ACK claim |
| New runner failure/ordering tests | PASS 14 tests | Real PHP rejection probe plus deterministic runner orchestration failures |
| New MySQL policy unit tests + existing unit example | PASS 33 tests / 67 assertions | Included in the 116 DB-free total; no MySQL connection |
| PHP syntax / Python compile | PASS 10 PHP files / 3 Python files | Remaining changed Python source-policy script executed directly |
| Traceability, P2/P3 source, F01, CI policy scripts | Current PASS across 42 distinct scripts | Initial P2 source FAIL retained; corrected and rechecked |
| Security scanner regression | PASS 4 tests | Scanner behavior only |
| Full candidate security screen | REVIEW_REQUIRED, exit 1; 34 findings | 24 secret-pattern indicators + 10 unsupported-format indicators; not PASS |
| Public documentation inventory | Completed, exit 0; 0 read errors | Inventory only; no confidentiality/publication approval |
| `git diff --check`, index/protected-file checks | PASS | Empty index; protected files remain unchanged and untracked |
| New real MySQL integration tests (8 methods) | NOT_RUN / BLOCKED | Requires admitted empty isolated MySQL 8 |
| Migration apply / rollback / reapply | NOT_RUN / BLOCKED | No database schema/data mutation performed |

DB-free regression invocation: generate fresh temporary B14/B15 JSONL with their bridge `--output` commands; set `VG_B14_WIRE_JSONL`, `VG_B15_EVENT_JSONL` and a fresh `VG_B17_RECEIPTS_JSONL` destination. Run `php vendor/bin/phpunit --colors=never --do-not-cache-result --log-junit <temporary-report> --filter '^(?!.*(?:TelemetryIngestTest|EventIngestTest|DeviceReadApiTest|FirmwareMySqlIntegrationTest)).*$'` from `backend/laravel`, with explicit `APP_ENV=testing`, synthetic APP_KEY, array cache/session, sync queue, null log channel and deliberately unavailable DB port 1. `TestApplication` disables dotenv loading. Then run `phase9_b17_receipt_crosscheck.py --input <temporary-receipts> --evidence-dir <temporary-folder>`.

Observed raw fixture hashes on this Windows C runtime (CRLF retained): B14 `9d0edbcc1e050155797b2c8cbe3de5226ffb7bbf01c9a01c252650fbe846525f`; B15 `e495ab61324bd0b29f764b33e0187a2892d4a92c054bf9dbc943dca96de3f308`; B17 receipt export `d8771f43ebf40e762f20e723ea10548f9b1b0c377cb6567c1584e0f06e2464b3`. Temporary files were removed by their owning temporary-directory context; no credentials or private coordinates were captured.

Detailed local logs: [focused tests](mysql-integration-focused-20261025.txt), [initial policy run](mysql-integration-policy-20261025.txt), [policy correction/recheck](mysql-integration-policy-recheck-20261025.txt), [blocked MySQL execution](mysql-integration-blocked-20261025.txt), [security scan](mysql-integration-security-20261025.txt), [document inventory](mysql-integration-document-review-20261025.txt), and [final branch/index/hash checks](mysql-integration-final-state-20261025.txt). No formal execution CSV is promoted by this batch.

Initial policy failure: P2 source test required local dotenv/vendor absence and exactly three migrations, contradicting installed local dependencies and the existing P3 fourth migration. It now checks prohibited dotenv/SQLite/vendor paths in the Git index without opening local secrets; P2 migrations must remain present and P3 retains the complete four-migration inventory check. The initial failing log remains available. F01 status assertions were also updated from its historical pre-Phase-9 snapshot to the existing formal records and current qualified implementation status. No functional assertion was removed from the backend tests.

Scope/security review: new device bearers are generated at runtime and stored only as SHA-256 digests. Guards perform read-only SELECT/SHOW queries; schema changes are delegated to Laravel migration commands only after empty-catalog admission. No firmware source, migration, LOCKED requirement/matrix, or formal result-table edits occur. New scanner indicators include password-field validation maps and synthetic policy-test values; baseline indicators include framework/env expressions, the ephemeral CI test key, and unsupported text formats. This scoped review does not clear the full candidate screen; **security gate remains REVIEW_REQUIRED**. Do not stage or commit until required review and real MySQL gates are satisfied.

## Remaining blockers

Provide an approved disposable empty MySQL 8 test catalog/account through process environment and execute the documented guarded command. Tests/CI are prepared but database correctness and migration reversal remain unproven in this session. No local commit is permitted while this mandatory gate is incomplete.

Cross-boot distinct telemetry ordering remains unresolved; state/history remain ordered by server receipt. Connected dashboard, actual ESP32 Wi-Fi/TLS, NVS/filesystem durability, trusted generation-floor persistence, concurrent storage publication, fresh Wokwi/hardware bench, remaining formal SIM/SUP, HTTPS and production readiness remain unverified. Overall system PARTIAL; final approval NOT_APPROVED.
