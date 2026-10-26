# Project entry replacement and one-candidate cleanup review

Parent develop0507fc90b63aea8aec3ee32a722a38e25c5d3147, initially empty index.
Explicit related scope of seven-part data/UI batch, not an administrative batch.
Current user Verified Safe Cleanup policy governs; historical read-only policy
inventories and evidence remain intact. This record authorizes NO deletion.

Candidate: backend/laravel/resources/views/welcome.blade.php, tracked100644,
parent/index Git blob b7355d72a12820cc4663a607ebf567d4db057704,
working SHA256 e50e41602994840b788471625fec54a4db6138ec971be05cfdfba40daf906c22.
No preexisting tracked diff for this candidate. No other candidate is admitted.

Positive replacement proof: project root now redirects to named monitoring.index
within existing security/no-store middleware. Guest monitoring requires real
session, authenticated data requires enabled user and explicit device grant.
The existing ExampleTest.php was retained and expanded from default root200 to
five real entry/HEAD/query/guest/error regressions. Actual guarded PHP8.2.35 and
MariaDB suite377PASS while welcome template PRESENT:
data-ui-root-before-cleanup-mysql-run1-20261026.txt. Actual private TLS/PHP/session/
owned MariaDB before-cleanup gate PASS, including fixed root guest/HEAD/authorized
redirects and all eight data-connected sections:
data-ui-live-http-before-cleanup-run1-20261026.txt. Direct data fixture cleanup
returns exact approved catalog to zero application rows. No template removal was
necessary to establish actual project-entry behavior.

Dependency/compatibility review (read-only):

- Current web routes, controllers, providers, config, autoload, DI and templates:
  root uses redirect()->route('monitoring.index'); MonitoringController uses
  fixed monitoring.index/monitoring.devices views and session controller fixed
  monitoring.login. Index has eight literal section includes and shared literal
  monitoring.channel-table. AppServiceProvider register/boot are empty; composer
  PSR4 autoload has no view-loading hook/reflection plugin. Config/session.php
  contains unrelated English word welcome in a comment. No dynamic welcome view
  path or namespace registration found in current application.
- Positive framework chain: Illuminate Routing Redirector::route -> to ->
  createRedirect constructs RedirectResponse, Symfony RedirectResponse::setTargetUrl
  builds escaped inline redirect HTML and Location. It does not render Blade.
  Laravel ViewCacheCommand enumerates existing Blade files rather than requiring
  the welcome filename. Runtime root/required-view behavior has actual TLS proof.
- Vite inputs are resources/css/app.css and resources/js/app.js. Tailwind source
  globs scan existing Blade/JS/compiled views, not a required welcome filename.
  No package script explicitly requires it. No install/build/cache deletion run.
- Firmware CMake component sources are main.c, esp32_network_client.c and
  esp32_offline_store.c; includes/PRIV_REQUIRES/stack-usage/size settings have no
  backend-resource dependency. PlatformIO candidate/retained envs use same SDK
  source and board, no web assets/linker/partition changes. Current firmware
  source must still match committed SDK proof before batch commit.
- Migrations/seeds/schema/API/native fixtures: no welcome payload or schema
  dependency. No existing schema history/golden/reference fixture removed.
  Historical scaffold foundation test requires project directories/artisan/
  public entry/routes/tests, not welcome bytes; its old no-vendor/no-migration
  assertions are historical and not current installed-framework regression gates.
- CI/regression/evidence: actual root test is intentionally updated; no scanner
  fixture or historical audit allowlist requires welcome bytes. Runtime behavior
  change from generic scaffold200 to project302 is explicit, not a LOCKED API or
  telemetry contract change. LOCKED38/hash, old schema1.0/1.1, historical evidence,
  traceability/verification registries and old contracts are preserved.
- Security-scanner dependency is decisive for current deletion admission:
  scripts/audit_precommit_security.py::inspect_candidate treats any missing tracked
  working file as a security finding before index content scan. A prestaging
  mandatory security PASS cannot presently be obtained for an unstaged removal.
  Prematurely staging a deletion to hide that finding, weakening the scanner or
  expanding security tooling solely for optional scaffold cleanup is not admitted
  by this project-entry batch. This is source-inspected gate incompatibility,
  not a fabricated executed cleanup failure.

Decision: DEFERRED. Runtime role is positively replaced but complete required
cleanup gates cannot currently admit the deletion. Candidate remains PRESENT,
unchanged, unstaged; removal count0. Security review tooling support for an exact
reviewed deletion is a possible later substantive tooling dependency. Do not
infer future SAFE_TO_DELETE from this record; recheck actual state and all gates.
All cache/vendor/untracked/WIP/migration/history/evidence/handoff files remain
PROTECTED. No database/app-data cleanup. No recursive or broad deletion. NO PUSH.
