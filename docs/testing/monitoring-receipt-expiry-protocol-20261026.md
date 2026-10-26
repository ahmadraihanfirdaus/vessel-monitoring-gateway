# UI001 receipt display lifetime and real browser integration

Parent develop2b00013b6936083be18bda72d1d0e563d6482f25. Previous seven-scope
fault/storage/reference batch committed60exact files/all mandatory local gates
PASS; both handoffs saved/updated after commit. Current index empty. Preserve
all prior implementation, LOCKED38, historical evidence, private config and three
protected untracked files. No baseline/dependency audit repeat or cleanup scope.

Targeted source review: UI001 requires visibly distinct live/stale/offline/
simulation. Existing controller/MonitoringFreshness classify server receipt age
at authenticated GET, and Blade renders static labels/age; no client script.
The dashboard contract explicitly uses manual authenticated refresh, no fabricated
data feed. Assess an already-open page with an actual browser and configured test
policy before claiming a display-lifetime defect. Keep receipt provenance distinct
from physical measurement chronology; source/quality/zero/null/alarm semantics
and actual data refresh behavior remain unchanged.

## Six related scopes

1. Reproduce open-page receipt status/age versus an authenticated fresh GET using
   real Laravel/isolated MariaDB and browser DOM. Add explicit snapshot/provenance
   and conservative server receipt-deadline descriptors if justified by evidence.
2. First-party client display expiry only: age already-rendered receipt state;
   no polling, telemetry fetch, database mutation or physical control. Use a
   monotonic elapsed upper bound from the current navigation request, avoiding
   assumed client/server clock synchronization. Missing/invalid/rewound timing,
   malformed policy/attributes, unsupported cached navigation => safe snapshot/
   UNKNOWN. Never revive LIVE from STALE/OFFLINE without a new authenticated GET.
3. Safe Blade bindings for every receipt-status presentation, explicit no-JS/
   load-failure snapshot fallback, first-party static asset and narrowly scoped
   CSP. No unsafe inline/eval script, third-party dependency/CDN or value mutation.
4. Actual headless Chrome DOM integration using a fresh owned temporary profile,
   actual login/CSRF/session/granted backend and strict upstream TLS. No personal
   profile, global PATH change, certificate-ignore flag or insecure-certificate
   option. No dependency download. Browser binary existence is not execution PASS.
5. Positive/negative/boundary/security PHP/Node/browser tests plus necessary real
   PHP/MariaDB/TLS and existing native/integrated regressions. Explicit PHP8.2.35,
   approved127.0.0.1:3307/vessel_gateway_codex_test/vgw_codex, guarded ephemeral key,
   unchanged six-migration schema and exact owned cleanup. Hardware gates NOT_RUN.
6. Source-bound evidence, current32/2/4formal status retained unless a separately
   prescribed formal case is actually executed; living38/docs/both handoffs,
   security/manual/exact staged review and local develop commit only allmandatory
   local gates PASS. No push. Continue residual software assessment afterward.

## Browser test trust and isolation boundary

The installed Chrome can use its ordinary root store without modifying global
trust. A single-purpose test UI origin adapter may bind ONLY loopback localhost,
require the exact owned test user agent/Host and accepted same-origin requests,
and forward only fixed login/logout/monitoring/first-party asset paths to the
existing private TLS test listener. Upstream uses the generated public CA plus
normal hostname/date verification, rejectUnauthorized=true. No API endpoint is
exposed by the plaintext adapter; synthetic ingestion stays on verified HTTPS.
Translate only the exact owned origin in Location/form URLs/Origin; do not strip
Secure/HttpOnly/SameSite cookies or relax CSRF/grant guards. Verify browser secure
cookie behavior on localhost rather than assuming it; otherwise BLOCKED, no
insecure fallback. This is an isolated browser component/integration hop, NOT
proof of a deployed HTTPS browser edge. Existing strict TLS CA/hostname/downgrade
negative gates remain mandatory and deployment TLS remains NOT_RUN.

Use real owned test credentials internally in process only, never argv/public
logs/body/cookies/CSRF/password/APP_KEY/token/MAC. Record only browser version,
response/source hashes and selected DOM/status/visibility/timing facts. No whole
HTML or secret profile copied to evidence. Browser launch obeys sandbox/IDE
approval; denial is a blocker, never circumvented. Stop/clean only verified owned
processes/temporary roots, no broad process kill or repository deletion.

Dedicated short test freshness intervals are fixture policy, not a vessel SLA.
Record the observation/reproduction honestly, preserve failures, and freeze code
during source-bound gates. Actual browser DOM does not prove graphical/manual
operator acceptance, physical sensor freshness, SDK/RTOS/NVS/outage behavior,
currentWokwi, hostedCI, directMySQL8/POSIX or deployedTLS. No SIM010 promotion from
a browser timer test; systemPARTIAL/finalNOT_APPROVED, no requirement VERIFIED.

PROTOCOL_BATCH_REVIEW=PASS_SIX_RELATED_UI_RECEIPT_EXPIRY_SCOPES_WITH_BOUNDARIES
REPRODUCTION=NOT_RUN_AT_PROTOCOL_CREATION
IMPLEMENTATION=NOT_STARTED_AT_PROTOCOL_CREATION

Browser admission correction before production changes: actual Chrome155 under
the existing no-referrer policy serialized same-origin form Origin:null. The
first adapter rejected it; these failures are test-harness observations, not a
dashboard lifetime failure. Permit null ONLY with browser Sec-Fetch-Site same-origin,
Mode navigate, Dest document plus exact owned Host/UA. Preserve null upstream,
normal Laravel session/CSRF mandatory, reject foreign or missing POST origin.
Do not weaken app CSP/referrer/cookie/auth settings or use insecure certificates.

Startup admission review: intermittent pre-fixture relay TimeoutError retained;
server accepted request, no fatal/listen/permission flag. Root cause not inferred.
Only the read-only process readiness window is now60sec, per-request timeouts
and event-race15sec barrier unchanged. Must actually return healthy200 before
any fixture. Added two orchestration negatives/late-start admission tests (HTTP
lifecycle now24methods). Fixed earlier repeated-context diagnostic/budget patch
before final freeze. Private router logs only fixed stage names, never values.
Browser-only tests remain separate from normal215-check TLS suite. Current source
snapshot now includes all new Node/Python browser units and the24 lifecycle tests.
