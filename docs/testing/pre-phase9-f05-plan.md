# Pre-Phase 9 F05 — Clean Public Archive Procedure

**Status:** BATCH COMPLETE — post-commit tracked-only archive evidence PASS

## Scope

F05 addresses the repository-audit finding that a raw workspace ZIP included
generated and machine-local material even though Git-tracked public source was
clean.

The repository must provide a repeatable tracked-only archive procedure that:

- archives exactly the files tracked by Git at the selected commit;
- excludes `.git`, `.pio`, `.vscode`, generated SDK configuration, Python
  caches, dependency trees and `.env` files;
- rejects machine-local Windows user paths in text content;
- rejects a small set of high-confidence secret token/key signatures;
- records the source commit and resulting SHA-256;
- does not imply publication approval, deployment approval, physical
  verification, certification or production readiness.

## Implementation

- `scripts/create_public_archive.sh` creates a ZIP using `git archive`.
- `scripts/test_public_archive.py` verifies exact tracked-file parity and the
  archive hygiene guards.
- `docs/public-release-archive.md` documents the operator procedure.

## Gate

The implementation check may exercise the procedure against the current HEAD
before commit. After this F05 implementation is committed, a separate
post-commit run must create and verify the final archive from the new commit and
record evidence before the pre-Phase-9 repair gate is considered closed.

No LOCKED file is modified.

## Implementation check — 2026-10-17

- F01 status/traceability regression: PASS.
- Automated security regression: PASS.
- Temporary tracked-only archive probe: PASS.
- Archive file set matched current Git tracked set exactly: 295/295.
- Forbidden archive entries: 0.
- Machine-local user path hits: 0.
- High-confidence secret hits: 0.
- Git metadata entries: 0.
- LOCKED SHA gate: PASS (2/2).
- Post-commit archive evidence: NOT_RUN.

Phase 9 remains blocked until this F05 implementation is committed and the
post-commit tracked-only archive is generated and verified from that commit.

## Scanner hotfix after first post-commit attempt — 2026-10-17

The first post-commit archive finalizer stopped because the machine-local path
scanner matched two non-secret literals inside the archive itself: the
documentation placeholder `/c/Users/<user>/...` and path-pattern text in the
scanner source.

The scanner was hardened to require a concrete account token and to assemble
its path prefixes at runtime so it does not match its own source. Focused
regression tests cover Windows backslash paths, Windows forward-slash paths,
Git Bash paths, the `<user>` placeholder, and scanner self-source behavior.

Hotfix pre-commit checks: PASS.

Post-commit archive evidence remains NOT_RUN until this hotfix is committed.

## Scanner fixture hotfix after second post-commit attempt — 2026-10-17

The second post-commit archive run stopped because the scanner regression test
source itself contained literal concrete machine-local path fixtures. The
scanner correctly flagged those literals.

The fixture tests now assemble concrete path samples at runtime, and a sixth
regression test verifies that the fixture source itself contains no
scanner-detectable machine-local path. Scanner rules were not weakened.

Fixture hotfix pre-commit checks: PASS (6/6).

Post-commit archive evidence remains NOT_RUN until this fixture hotfix is
committed.

## Final post-commit archive evidence — 2026-10-17

- F05 implementation commit: `55c8ef6`.
- Scanner hotfix commit: `e7e2b6b`.
- Scanner fixture hotfix commit: `b784a78`.
- Focused scanner/fixture regression: PASS (6/6).
- Tracked-only public archive generation from committed HEAD: PASS.
- Exact archive-to-Git tracked-file parity: PASS.
- Forbidden archive entries: 0.
- Machine-local user path hits: 0.
- High-confidence secret hits: 0.
- Git metadata entries: 0.
- F01 status/traceability regression: PASS.
- Automated security regression: PASS.
- LOCKED SHA gate: PASS (2/2).
- Total system status remains PARTIAL.
- Phase 9 remains NOT_STARTED until this closure evidence is committed.

This closes the pre-Phase-9 F05 repair scope only. It does not authorize
publication, deployment, physical integration, certification, calibration,
field operation, or production readiness.
