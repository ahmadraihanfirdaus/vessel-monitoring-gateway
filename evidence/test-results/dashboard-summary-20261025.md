# Connected monitoring execution, 2026-10-25

Baseline: `develop` HEAD `ccf57405634c8752b11fb3e34ac72281cee386ac`.
Tracked worktree/index were clean; AGENTS.md and the two protected firmware files
remain preexisting, untracked and excluded. No repeat of the one-time project
baseline, no remote action, no locked requirement change, no main DB access.

## Seven related implementation scopes

1. Additive users/grants/session/cache migration and exact isolated schema upgrade.
2. Real session login/logout, CSRF, rate limiting, password byte bounds and headers.
3. Default-deny per-user/device reads, fresh revocation and account-disable checks.
4. Local CLI provisioning/revocation using hidden/process credentials, hashed
   storage, atomic grant validation and sanitized failures.
5. Explicit configurable sample/transport freshness with unknown/error states.
6. Eight connected Blade views, faithful event/quality/source facts, escaped
   rendering, one shared telemetry sample, validated formal registry snapshots.
7. Real MariaDB/C99/kernel integration, negative/boundary/security regression,
   evidence/traceability, exact scope review and read-only cleanup inventory.

## Actual gate matrix

| Gate | Outcome | Evidence |
|---|---|---|
| Approved old-catalog read-only preflight | PASS: five tables/four migrations, zero application rows | `dashboard-db-legacy-preflight-20261025.txt` |
| Explicit migration upgrade | PASS: Laravel migrate only; ten tables/five migrations | `dashboard-db-upgrade-20261025.txt` |
| Initial integration | PASS: 289 tests, zero failed/skipped | `dashboard-integration-run1-20261025.txt` |
| Additional snapshot/evidence tests | PASS: 298 tests | `dashboard-integration-run2-20261025.txt` |
| First exception-path expansion | FAIL: 2 of 304 tests; diagnosed and corrected | `dashboard-integration-run3-20261025.txt`; boundary diagnostic logs |
| Corrected exception paths/password bound | PASS: 305 tests | `dashboard-integration-run4-20261025.txt` |
| Ancillary isolation and migration roundtrip | PASS: 323 tests; rollback/apply/reapply, receipt crosscheck | `dashboard-integration-run5-20261025.txt` |
| Final complete PHP/Laravel/MariaDB suite | PASS: 325 tests, zero failed/skipped; PHP 8.2.35 explicit | `dashboard-integration-final-20261025.txt` |
| Final database postcheck | PASS: ten exact tables/five migrations, zero application rows | `dashboard-db-postcheck-20261025.txt` |
| C99 telemetry/events and browser integration | PASS: original 2/4 C99 wire fixtures, actual ingestion/auth/storage, granted Blade read | integration logs and FirmwareMySqlIntegrationTest |
| Scanner initial | REVIEW REQUIRED: 12 initial occurrences; 15 benign occurrences reviewed after final changes | `dashboard-security-run1-20261025.txt`; triage CSV |
| Exact non-secret review and scanner adversarial tests | PASS: scanner zero findings/warnings; 22 adversarial methods | `dashboard-security-review-20261025.txt` |
| Full source/CI/traceability/lint regression | PASS: 53 policy/regression commands and 28 lint commands; two changed-file lint rechecks also PASS | `dashboard-scoped-gates-20261025.txt` |
| First staged whitespace review | FAIL: one diagnostic EOF blank line; exact staging restored, no commit. EOF formatting corrected with hashes and unchanged diagnostic text | `dashboard-integrity-20261025.txt` |
| Final content, protected hashes and exact index review | Required PASS before local commit; index scanned again after exact staging | final security/integrity logs and exact manifest |
| Cleanup candidate inspection | Metadata only; no files deleted | `dashboard-cleanup-inventory-20261025.csv` |
| Real TCP browser/listener, deployed TLS, hosted CI, direct MySQL 8, ESP32/NVS/physical bench | NOT_RUN in this slice | No inference from kernel/HTML/HTTPS-request fixtures |
| Formal SIM-010..015 and remaining SUP protocols | NOT_RUN here; registries unchanged | No formal promotion |

The final registry test also isolates each invalid SIM case with an otherwise complete valid SUP fixture and rejects PLANNED as a SIM execution state. The earlier 324-case success is retained in run6. A gate-orchestrator discovery typo was corrected from actual rg file inventory before any gate command ran; its record is retained.

The existing B12 source check still expected five authenticated API bindings
after the preceding event-read addition had made six. Its exact expected count
and new event-route assertion now match the actual routes; no binding check was
removed. All corresponding source/runtime regressions pass locally; hosted CI
remains NOT_RUN.

The two exception tests exposed a Vary-header representation mismatch (Cookie
was an additional header while the assertion inspected only the first value)
and an overly broad AuthManager mock that intercepted framework userResolver.
The application now normalizes Vary selections into one combined header; the
outage fixture replaces only the credential provider. The real SessionGuard and
framework pipeline execute. Retained diagnostics contain no credential values.

Schema safety was extended because browser sessions/cache introduce secondary
database paths. Six environmental and ten effective-configuration rejection
cases plus positive admissions prove these overrides fail closed. Populated
users/sessions/cache/cache_locks and already-upgraded legacy admission have real
transactional negative tests. Views and extra schema objects are prohibited.

## Security review qualification

No literal credential was identified in the new flagged occurrences. They are
runtime random test values, validation rule metadata, dynamic environment-name
concatenations and the existing DB_PASSWORD variable-name mapping. The existing
primary effective credential, server and grants methods remain byte-identical;
secondary checks and schema admission were strengthened.

Fifteen occurrences are documented in the triage CSV and covered by 13 distinct
new exact whole-file/line records (repeated identical lines share a record).
The finite RUNTIME_GENERATED_TEST_VALUE classification still requires exact
manual review; it is not an automatic function/test-directory exemption. Changed
bytes invalidate it. Credential token signatures, private keys, credential URLs,
privacy, binary/encoding and path checks remain non-waivable. New adversarial
tests prove runtime generation is blocked without review, changed literal bytes
invalidate review, and even reviewed runtime-class tokens are rejected.

No PHP global PATH/XAMPP change occurred. All PHP tests use
`C:/tools/php-8.2.35/php.exe`; approved MariaDB remains loopback port 3307,
`vessel_gateway_codex_test` / `vgw_codex`, engine 10.4.32. The runner creates a
valid ephemeral key and records only validity/source; standalone file-only
APP_KEY remains unconfigured. Ordinary `.env` and main DB are never loaded.

## Remaining work and boundaries

UI-001/UI-002 have local software/rendering evidence, not formal approval.
Deployment must supply authorized freshness policy and explicit domain-channel
assignments. Overview preserves all channels even if those assignments are empty.
The dashboard has explicit refresh; real-time push and deployed browser usability
are not claimed. Receipt order is not global device chronology, and the event
view is not an active-alarm reconstruction/control surface.

Continue toward the next independent software integration scope after commit;
the Goal remains active. ESP32 transport/storage implementation/verification,
dedicated end-to-end protocols, hosted CI, bench, TLS and final approval remain
open. Overall PARTIAL; final approval NOT_APPROVED; no production/hardware claim.
