# Connected monitoring development slice

This slice implements the browser data path for UI-001/UI-002. It does not
modify LOCKED requirements. This original slice and its five-migration test
figures below are historical; the dated20261026 continuation records current
six-migration admission, actual Chrome and strict local TLS evidence. SIM-010,
hosted CI, deployed TLS and physical transport remain unperformed. The dedicated
SUP-015 host HTML case is recorded separately in the current case registry.

## Authorization and account lifecycle

Browser routes use the explicit `web` session guard, not device bearer tokens:

- `GET /login`, `POST /login`: login form and credential verification.
- `POST /logout`: invalidate session and regenerate CSRF token.
- `GET /monitoring`: only enabled, explicitly granted devices.
- `GET /monitoring/{device}`: same grant predicate, 404 for ungranted, disabled,
  or nonexistent devices. Disabled users receive 403 after session authentication.

There is no public registration, password reset route, universal operator role,
or automatic access to every device. User disablement and device grants are
queried on every read; revocation applies to subsequent requests without a new
login. Device credential columns are not selected by the browser access query.
In-flight responses are not revocation acknowledgements or atomic control actions.

Provisioning uses the local `monitoring:operator` command with an email, optional
name, explicit `--device` grants / `--revoke` targets, and `--disable` / `--enable`.
New credentials are supplied through hidden interactive input or the dedicated
process-only `VG_MONITORING_PASSWORD` when `--password-env` is explicit. Passwords
are never command arguments, output, evidence or configuration defaults. The
existing User hashed cast stores them; new passwords must be 16..72 **bytes** to
avoid bcrypt truncation. Login rejects inputs over 72 bytes even if their Unicode
character count is smaller. Query failures have generic output without bindings.

The command validates every grant before writes and commits account/grants in
one transaction. Existing enabled devices only; no device provisioning or
physical-control capability. It must only be used against a separately verified,
authorized development target. This batch runs it inside guarded transactional
tests; it creates no lasting account in the approved test catalog and never
executes it against the ordinary `.env` or main database.

Login rotates the session ID, uses generic credential errors and flashes only
email, never password. CSRF covers login/logout. Login is throttled to five
requests per minute per framework request identity (normally client IP).
Responses, including CSRF/throttle/auth/storage errors, are no-store/private,
vary on Cookie, and carry no-referrer, nosniff and a CSP disallowing scripts,
framing, external form actions, objects and base tags. Inline styles are allowed
for this self-contained dashboard. Cookies use framework HttpOnly/SameSite=lax;
the secure flag is exercised with an HTTPS request fixture, not deployed TLS.

## Data display

All eight views render one granted device. Overview always includes every
returned channel, exact quality, null-versus-zero, schema, boot, sequence and
source metadata. Invalid/missing/unknown values render a dash rather than a
numeric safe default. Channel names and all other values are Blade-escaped.

Safety, Propulsion, Navigation and Power use explicit lists in
`config/monitoring.php` (`channel_sections`). These are presentation assignments,
not guessed OEM channel meanings, units, or safety limits. Empty/unavailable
assignments remain explicit; no data disappear from Overview. Configure them
for the approved synthetic/bench channel contract before a domain demonstration.
No implicit channel-name heuristic or invented sensor mapping is introduced.

Alarms/events show the latest 50 receipt-ordered facts, retaining event identity,
source, alarm link and occurrence counter. ACK never implies CLEAR. Neither a
filtered event list nor receipt order reconstructs current active alarm state.
Health displays last-seen/high-water facts; the same telemetry sample lookup
supplies both state and matching latest-sample health metadata.

Test Evidence reads only scenario IDs and execution statuses from the two
fixed repository SIM/SUP CSV registries. It checks exact identities, completeness,
duplicate IDs, size and status vocabulary. Missing/malformed evidence displays
UNKNOWN. Evidence bodies, arbitrary paths and free-text qualifications are never
served, and no PASS is inferred from displayed sensor values.

## Freshness policy

`MONITORING_STALE_AFTER_SECONDS` and `MONITORING_OFFLINE_AFTER_SECONDS` have no
assumed defaults. They must be positive integers with offline > stale. Unset or
invalid policy gives UNKNOWN. With valid policy, a missing receipt is OFFLINE;
invalid/future timestamps are UNKNOWN. Exact boundary behavior is:

- age < stale: LIVE;
- stale <= age < offline: STALE;
- age >= offline: OFFLINE.

The test intervals 10/30 seconds are deterministic test oracles only, not vessel
acceptance thresholds. Receipt age is measured in UTC. Telemetry receipt age and
transport last-seen age have separate badges so a new heartbeat/replay does not
silently re-label an older sample. These facts do not establish cross-boot
measurement chronology. Refresh is an explicit authenticated GET; no fabricated
live feed, autonomous physical action or sample mutation occurs.

Continuation20261026: an open real Chrome page reproduced frozen LIVE even after
the configured stale/offline boundaries, while a new authenticated GET returned
OFFLINE. Server HTML now defaults to a neutral, explicit SNAPSHOT label at the
displayed server capture time. A first-party external script expires all four
receipt labels against conservative server millisecond budgets and monotonic
current-navigation elapsed time. It never fetches telemetry or changes data,
source, quality, alarms, or the server receipt chronology. Rounded-up server
fractional age avoids extending a receipt budget across a fractional boundary.
No browser/server wall-clock synchronization or engineering TTL is assumed.

Missing/malformed/unsafe policy or timing gives UNKNOWN; missing script/blocked
asset leaves the explicit SNAPSHOT fallback. Cached restore, rewind, pagehide,
hidden visibility or freeze invalidate the client status until a new GET.
These are browser display checks, not hard real-time guarantees: event-loop
suspension, timer scheduling and privacy-rounded browser clocks are not physical
sensor freshness or timing certification. Values and snapshot-age text remain
as of the server capture. Server receipt can reflect replay; OFFLINE here is a
receipt-policy classification, not a determination of physical engine state.

Only successful granted device HTML allows script-src self; connect-src none,
no inline/eval script. Login/list/denials/errors retain script-src none. Other
no-store/referrer/frame/form/CSRF/grant/cookie protections remain. The static JS
URL includes its public content hash; it contains no runtime identity or secret.
Actual headless Chrome uses a fresh owned profile and a fixed UI-only loopback
origin adapter to verified HTTPS upstream, with unchanged Secure/HttpOnly/Lax
cookies and real Laravel session/CSRF. Its HTTP localhost browser edge is not
deployed browser HTTPS proof. See receipt-expiry protocol and evidence summary.

## Schema and isolated test admission

One additive Laravel migration creates users, monitoring_device_access, sessions,
cache and cache_locks. Four original migrations remain unchanged. Local test
inventory is now exactly ten tables and five migration records, with zero rows
outside migration metadata at admission and after the suite.

`mysql_test_gate.php --inspect-legacy` is read-only and admits only the exact
previous five-table/four-migration empty catalog. Explicit `--upgrade-existing`
admits that same source inventory before Laravel migrate applies the addition;
it refuses populated, foreign, malformed, or already-upgraded inventories.
`--inspect` and `--roundtrip-existing` require the current exact inventory.
Roundtrip rolls back exactly the five known migrations and reapplies them via
Laravel only. There is no manual DDL, migrate:fresh, reset or catalog provisioning.

Every gate checks the approved primary connection/server/account/grants and
effective session/cache/auth configuration before PDO migration/fixture use.
Secondary connections may only be unset or the same mysql connection; table
names are canonical. Test bootstrap audits relevant override names, never secret
values, and never loads the ordinary `.env`. The runner supplies its own temporary
cipher-compatible APP_KEY; the file-only testing key remains empty.

See the [actual test matrix and retained failures](../../evidence/test-results/dashboard-summary-20261025.md).
