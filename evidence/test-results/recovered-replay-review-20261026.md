# Recovered replay final scope/security review

Baseline develop70963d4, ADR0009 six related scopes. Review PASS for the local
software slice; final exact staged-byte security scan remains required before
local commit. No external/formal/production approval is implied.

- Actual integration: recovered NVS transaction state exports an immutable
  capacity-eight event-only view via dedicated one-item queue, zero-wait take.
  Worker owns all NVS IO; allocation/start failures release the added queue.
  Successful positively-empty recovery is distinct from invalid/uncertain IO.
- Identity/compatibility: original device/boot/event/alarm/source/time retained,
  known metadata delegates existing1.1 serializer, unknown remains1.0 nine fields.
  Strict bounded strings, identity uniqueness, source/metadata/generation,
  alias/capacity validation and exact scalar serialization have native checks.
- Publication: fair shared recovered/current progress, transport queue refusal
  leaves cursor, unsupported legacy type reported and retained. Event-encoding
  failure/progress inconsistency halts publication explicitly; samples/latest
  telemetry and local alarm evaluation continue. Explicit recovery restarts
  recovered traversal but preserves current cursor. Queue admission is not ACK.
- Retention: no storage erase, delete, eviction, weakened cumulative prefix,
  transaction publish bypass, alarm clear or application receipt acceptance.
  Existing cap8 refuses additional critical retention explicitly. Delivery,
  authenticated binding and crash-safe outbox retirement remain open software.
- Test oracle: native fixture reuses prior transaction IO fixture, executes real
  merge/publish/recover/serializer, six events/three boots in one bounded store.
  Real PHP/MariaDB and TLS prove colliding per-boot IDs stay distinct, legacy
  absence, zero/null lifecycle, exact duplicates/conflicts, raw escaped-key/body
  boundaries and granted HTML. Replayed events preserve latest telemetry.
- Guarded test safety: approved isolated target/account, ephemeral process key,
  exact10tables/6migrations/zero rows; no new migration/DDL/production operation.
  Fixture generation precedes any DB mutation; runner lifecycle failures tested.
- Regression: initial220commands219PASS and one security-review stale-pin FAIL;
  exact five unchanged source lines reviewed and corrected P1/content PASS.
  Final13 replay methods, original native/core/B44-46, source/PHP-lint gates,
  scanner23 adversarial, living38 and real366PHP/142integration PASS evidenced.
- SDK: both current source0602eed... PASS, candidate975856/frame944 and retained
  1044352/frame1616 within unchanged app1048576/frame2048 caps. TLS/assertions
  unchanged; no upload. Queue/worker heap/full-stack/timing remain NOT_RUN.
- Security: five INFO exact whole-file/line repins only; no literal secret,
  wildcard detector waiver or credential/privacy/encoding exemption. Historical
  failures retained, logs sanitized, SDK whitespace normalization before/after
  hashes recorded. Cleanup inventory metadata only, all candidates retained.
- Continuity: both handoffs already tracked since70963d4, rewritten current
  checkpoint includes full38 matrix, actual Git/WIP, runtime/evidence/roadmap and
  ready resume. Updates after successful commit are mandatory and documented.
- Protected/LOCKED/formal hashes unchanged. Three pre-existing untracked remain
  excluded. Two older evidence paths sometimes show stat-cache M but are byte
  identical to committed blobs, no content diff and outside this scope.

Final inventory/hash oracle: recovered-replay-files-20261026.csv. Before commit
verify exact staged paths/bytes, clean expected index/branch state and security
rescan. No push/remote/destructive Git and no source/evidence deletion.
