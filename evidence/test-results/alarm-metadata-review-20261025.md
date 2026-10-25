# Alarm metadata final scoped review, 2026-10-25

Baseline develop5048525; implementation and test scope ADR0008, seven linked scopes.
Review outcome: PASS for this local software scope, subject to exact staged-byte
security rescan before commit. System PARTIAL; external/formal gates NOT_RUN.

- Firmware: immutable transition captured at occurrence; shared model validation,
  bounded8 ledger; uint64 IDs/time and alias guards; full retains old facts and
  local observations continue. No added physical/operational control.
- Compatibility: VGS1 bytes/budget unchanged; VGS2 version/presence/CRC/length and
  canonical absent times checked; no invented historical metadata, prefix mutation,
  metadata downgrade, silent eviction or retention weakening. RAM buffer+64 only;
  app partition/body cap unchanged. Current-boot queue once is explicitly limited;
  receipt/deletion/recovered replay remain open and are not claimed implemented.
- Backend: bounded body/auth/device gates retained; existing raw-object methods
  extracted once for shared use. Nested duplicates/escaped keys/lexical integers,
  exact max values and lifecycle semantics covered. Nullable metadata via migration
  only, old rows null. Canonical full-payload duplicate comparison stays exact.
- Real RR201/500 defect reproduced before correction. Rollback before duplicate
  classification and shared current read support nested outer snapshots; four
  actual kernel/database process cohorts PASS without modifying isolation.
- UI/read: escaped event-time facts, legacy unavailable, uint64 strings/null/zero;
  no assumption of global active state from receipt order; ACK never CLEAR.
- Test safety: exact approved local database/account, current six-migration shape,
  zero rows before fixtures, process ephemeral cipher key; no main dotenv boot.
  Race scripts are CLI-only, owned fresh lease/payload/temp root, bounded waits,
  no secret output; workers stopped before owned cleanup. No manual DDL.
- CI: two native tests added, runtime PHP patch pins/read-only permissions and
  both SDK targets retained. Non-Windows -lm source adjustment has no POSIX PASS
  claim. No hosted CI execution or remote operation.
- Security: content scan PASS0 findings/0 privacy warnings, exact file+line reviews
  retained, no detector wildcard waiver. Original36 triage remains historical;
  current notes distinguish source-version reviews from unique vulnerabilities.
- Evidence: historical failures preserved with corrected outcomes; newest HTTP
  source proof2be135..., both SDK source22a297..., actual362 PHPUnit/122 integration
  categories distinct. SDK raw whitespace-only changes pinned before/after SHA.
- Handoff: both requested docs include actual baseline Git snapshot, full38-ID
  matrix/evidence, current WIP, runtime, invariants, readiness limits and resume.
  Initial matrix-audit regex failure was an audit oracle assumption (DB/UI prefixes),
  corrected to exact38 IDs without changing requirement baseline or document matrix.
- Scope: expected tracked30 plus explicit new metadata/test/doc/evidence paths.
  Protected AGENTS/two firmware untracked and LOCKED/formal baselines unchanged.
  No delete/rename/ignore/collateral cleanup, production DB, secret file staging,
  remote action, push or history rewrite. Manifest is the final exact file oracle.

Mandatory local gates: see alarm-metadata-summary-20261025.md and individual logs.
External ESP32/NVS/power-loss/WiFi/clock, formal protocols, deployed TLS, hosted CI,
MySQL8/POSIX/graphical browser remain NOT_RUN; no full-system approval inferred.
