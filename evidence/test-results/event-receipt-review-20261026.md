# Receipt/retirement manual security and scope review 2026-10-26

Baseline developbb4f462; current batch seven related scopes perADR0010. No stage
or commit until final working and staged scans, exact manifest/blob review PASS.

## Review of trust and mutation boundaries

- Backend receipt opts in explicitly, rejects duplicate/invalid header versions
  and caller-owned transactions before writes, signs only committed201/new or200/
  identical result. Normal JSON untouched; raw authenticated bearer, no stored
  token digest as key. Existing actualRR race regression remains201/200,201/409.
- Exact complete request SHA and HTTP status/domain are MAC-bound. Native strict
  bounded length/hex/media/alias/status and standard PSA provider are used by
  actual SDK worker. Positive tests use independent Python HMAC/real C crypto;
  no positive mock authorization. Wrong key/body/status/forgery/truncation refuse.
- VGS3floor scoped tolatest_boot; legacy bytes0floor unchanged, max5150/5184.
  Ordinary publish still no deletion/no invented floor. Authenticated path builds
  exact one-target candidate, preserves all other facts/latest/counters and only
  then runs shared unselected write/commit/readback. Unknown metadata remains
  unknown; known metadata cannot downgrade. Every partial-write/uncertain IO
  fault has native evidence; no physical durability inference.
- Worker receipt jobs are bounded, copy no key, mutex is released before crypto/
  IO, floor/admission normalization and typed completion follow durable result.
  First current snapshot prerequisite and fair normal/receipt jobs prevent
  startup starvation. Fresh boot refuses latest/retained namespace collision.
  Older recovered prefix can re-authenticate without rewinding running IDs.
- Actual owner handles only one request, shared monotonic kind-independent tag,
  exact immutable target and recovery epoch. HTTP alone never frees RAM.
  Matching durable generation/floor/exact prefix is required. New recovered
  prerequisites reschedule; unexplained rejection halts events/retains facts.
  Storage unavailable/uncertain retains RAM and permits bounded publication;
  exhaustion needs explicit reset/recovery. Alarm condition/ACK/allocator/time
  are not mutated by delivery. No physical engine/mission-system outputs.
- Actual private hostfile bridge compiles before DB writes; root/phase/identity/
  bounds/existing binary/initial slot checks fail closed. Token only process
  environment, receipts bounded binary stdin, no public response/key output.
  Real TLS integration uses server committed receipt with Python/native checks,
  file readback/reopen/owner and next facts. Host files are not physical NVS.
- Full adapter is continuous-only; retained selftest receipt API false, reader
  VGS3 preserved. Both SDK source hashes match; candidate985920/frame1056,
  retained1045408/frame1616 within unchanged app/stack/TLS/assertion gates.
  Retained3168byte margin and unmeasured full heap/callstack remain risks.

## Actual gates and failure disposition

373realPHP cases0failure0skip;187actualTLS/API/read/UI checks;229/229 broad host/
source/lint commands; native retirement17/floor7/protocol8/owner8/file4 plus
existing regression/core226 perboot repeat2. Current source/protected/formal/
38matrix/approved target-key/schema0app rows audit PASS. Both handoffs saved and
tracked. No DB migration added, existing six-migration mode is intentional.

Initial fixture enum/unused/alarm-reuse/full-capacity/source-name assumptions
failed and are corrected in retained development logs; no production guard or
compiler limit was weakened. First actual HTTP run failed race suffix oracle
including new receipt IDs; exact four-cohort selection corrected and full187
rerun PASS. Every failure remains evidence, no deletion or fabricated success.
Initial scanner5INFO occurrences are byte-identical CI/runtime lines frombb4f462,
0privacy warnings. Renew only exact line+whole-file pins, historical reviews
retained. No strong-secret/private-key/URL/path/privacy detector weakened.

## Scope and protected data

All changes are receipt/backend/firmware/runner/CI/tests/documentation/evidence
for this vertical slice. Final CSV manifest records exact files/hashes plusSELF.
RequirementsLOCKED, AGENTS.md, two protected firmware files and formal registries
have unchanged exact SHA/blob checks. Main .env/DB never booted/read; approved
127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex only, ephemeral cipher-compatible
process test key. No plaintext key/password/MAC/APP_KEY copied to public evidence.
Two preexisting metadata logs with stat-cache M are byte-identical and excluded.
Cleanup7categories read-only; no file/evidence/dependency deletion. No remote
operation, push, merge/reset/clean/history rewrite or hardware upload/erase.

System remains PARTIAL, finalNOT_APPROVED. Current Wokwi, ESP32/NVS/PSA/RTOS,
physical flash/power-loss/wear/rollback/clock/WiFi/TLS, full heap/stack/timing,
hostedCI, directMySQL8/POSIX, graphical/deployedTLS/formal newSIM/SUP NOT_RUN.
CRC is not at-rest authentication. Unsupported RECOVERY/cap8/refusal and explicit
reset policy remain. None of these external gaps is silently countedPASS.

MANUAL_SECURITY_LOGIC_SCOPE_REVIEW=PASS_SCOPED_WITH_RECORDED_LIMITS
FINAL_WORKING_SECURITY=PASS_ZERO_UNRESOLVED_ZERO_PRIVACY
EXACT_STAGED_SECURITY=REQUIRED_BEFORE_COMMIT
