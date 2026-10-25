# Real loopback HTTP/TLS continuation, 2026-10-25

Baseline: local `develop` HEAD `895e031ed205b6888c46a423cd1c9ee39c8f6e61`.
This follows the committed transport/NVS implementation. No full baseline
re-audit, remote interaction, LOCKED requirement change, migration change,
primary database access or firmware upload occurred in this slice.

## Seven related scopes

1. Exact schema/empty admission and proof of ownership for cross-request fixtures.
2. Actual PHP 8.2.35 CLI-server dispatch using the isolated test bootstrap.
3. Ephemeral local CA/leaf TLS, trusted-chain positive and hostile transport cases.
4. Actual core/snapshot C99 bytes through TLS/TCP/Laravel/MariaDB and read APIs.
5. Persistent browser-style cookie/form authentication, CSRF, session rotation,
   grant/account changes, logout and database-backed rate limiting.
6. Bounded proxy, prerequisite/failure/source-stability guards, owned process/temp
   lifecycle and guarded exact fixture cleanup.
7. CI wiring, security triage, regression, status/traceability and cleanup evidence.

## Executed gate matrix

| Gate | Actual outcome | Evidence in this directory |
|---|---|---|
| First new ownership unit integration | FAIL: one of 334 methods; grant ownership used internal device ID instead of existing string device_id | `live-http-isolation-run1-20261025.txt` |
| Corrected existing grant schema use | PASS: 334 methods, zero failed/skipped | isolation-run2 log |
| Stronger immutable token/lease ownership | PASS: final PHP/Laravel/MariaDB 335 methods, zero failed/skipped | `live-http-isolation-run3-20261025.txt` |
| Original strict empty-catalog policy | PASS: populated owned fixtures still rejected by normal empty gate; separate shape-only method does not waive ownership | LiveHttpSafetyTest and same isolation log |
| Initial live-profile preflight | BLOCKED before fixtures: unquoted null logging value did not equal literal null-channel configuration | `live-http-preflight-run1-20261025.txt` |
| Corrected explicit live profile | PASS: PHP 8.2.35; approved MariaDB/catalog/account; DB sessions/cache; Secure cookie; debug false; valid process-only APP_KEY; default mode NOT_RUN/read-only | preflight-run2 log |
| Initial real loopback request pipeline | PASS: 62 labeled assertions, exact owned cleanup | network-run1 and network-run2 logs |
| Runner failure/lifecycle regression | PASS: ten adversarial methods, including blocked preflight, compiler/TLS prerequisites, failed case cleanup, failed cleanup not PASS, source mutation, unsafe temp target and response-secret redaction | `live-http-network-final-20261025.txt` |
| Final real connection and boundary pipeline | PASS: 65 labeled assertions, no failed case, no skip; actual source stable | `live-http-boundary-final-20261025.txt` |
| Native runtime packet identity | PASS: six actual core/snapshot-recovered JSON packets; SHA-256 unchanged | same final network log |
| Actual TLS certificate/hostname/plaintext negatives | PASS on local Python TLS edge and real PHP upstream; no OS trust-store installation | same final network log |
| Actual API contracts and persistence | PASS: 4,096/4,097 bytes, MIME/JSON/auth/device identity, replay/conflict, cursor, null/quality, event ACK/CLEAR facts | same final network log |
| Zero and uint64 boundary | PASS: explicit synthetic HTTP packet stores zero and exact UINT64_MAX sequence/uptime; read JSON and Blade zero cell checked | same final network log |
| Actual persistent browser-style session flow | PASS: CSRF 419, cookie flags, database ID rotation, HTTPS redirects, grant revocation, disable/enable, logout destruction and next-request denial | same final network log |
| Actual cross-request rate limit | PASS: fresh owned cache namespace, five incorrect logins then 429 with Retry-After/no-store | same final network log |
| Existing source/CI/security plus changed PHP lint | PASS: 54 policy/regression commands and six PHP syntax checks | `live-http-scoped-regression-20261025.txt` |
| Initial scanner triage | REVIEW: seven informational non-secret occurrences, zero privacy warnings; exact records only | security-run1 log and security-triage CSV |
| Final security/shape/protected/scope/index | Required PASS before local commit; index rescanned after exact staging | final-security/integrity logs and exact manifest |
| Final real DB postcheck | Required PASS: exact ten tables/five migrations, zero application rows | final-security log; each actual network run also verified cleanup |
| Cleanup candidates | Read-only metadata; dependencies/evidence retained | cleanup-inventory CSV |
| Graphical browser, deployed/public TLS, ESP32 TLS/clock/NVS/power loss, direct MySQL 8, hosted CI, new formal SIM/SUP execution | NOT_RUN | No promotion from host sockets/HTML or prior SDK compilation |

Final network source-stability digest:
`e5d938e4f5ea71e8a6553ba04efde7b998e1e0bfb67c3aaa7204724c5c7bd3c0`.
The six original C99 wire packets remain SHA-256
`21930ab910d66844d7903d2e726c3c5a8db9809018deacb0e26d93d61f88ee4a`.
Additional zero/uint64 and event-fact inputs are explicitly synthetic HTTP test
data, not additional native firmware output. Counts are separate assertion/
method categories; no combined count of unique system requirements is inferred.

## Isolation and review details

The ordinary `.env` and main database are not bootstrapped. Dedicated test inputs
and APP_KEY are generated in process, never printed or passed as command-line
arguments. The ignored testing file retains its empty APP_KEY. The read-only
postcheck therefore does not claim a configured file key; actual HTTP/PHP tests
use a valid ephemeral one. No key, cookie, session ID, password, bearer or response
body is copied to evidence. Session-ID fingerprints remain internal to the
runner; cookie ciphertext changes alone are not treated as rotation proof.

Cross-request fixtures intentionally persist only in the initially empty approved
catalog. Cleanup proves the random lease, token digests and exact row ownership,
then deletes only those owned records and checks all application rows are zero.
An identically named device with another token is a negative admission case.
Foreign data is never reclaimed by a broad delete. Fixture lifecycle is CLI-only;
the private loopback router enforces its test-client marker before app dispatch.

The proxy has a fixed upstream, bounded body/reply, exact Host policy, no redirect
following and known forwarded scheme. Trusting that loopback hop is explicit test
deployment configuration. CSRF is genuinely enforced while APP_ENV remains
testing. The literal null log channel is explicitly configured; the original
testing LogManager fallback is not labeled a production vulnerability.

The first new ownership guard made an incorrect assumption about the grant FK;
the existing migration uses string device_id and no grant timestamps. It was
fixed before any live fixture preparation. Other existing implementation was
preserved. Source-stability guards were then added so final evidence cannot
certify a run spanning source edits; earlier successful runs remain historical.

Seven scanner occurrences were manually classified: two unchanged CI labels,
two historical validity/source labels and three runtime form inputs. None is a
literal secret. Whole-file and line hashes are pinned, and strong credential/
private-key/URL/path/encoding/privacy findings remain non-waivable. Current key
audit output uses separate validity booleans. The original 36-item review remains
in its existing security report; it was not replaced or reinterpreted.

## Remaining work

This closes a local TCP/TLS/session integration gap, not graphical browser
rendering, installed/deployed TLS, ESP32 transport execution, trusted device time,
NVS confidentiality/wear/power-loss or full resource-watermark proof. Continuous
all-domain acquisition, complete alarm metadata composition, and durable
replay/ACK integration remain substantive software work. Formal registries are
unchanged: SIM-001..009 PASS, SIM-010..015 NOT_RUN, five SUP PASS and fourteen
PLANNED. Overall remains PARTIAL and final approval NOT_APPROVED.

See `docs/testing/live-loopback-integration.md` for invocation and design, and the
exact manifest for the changed source/evidence files and byte hashes.
