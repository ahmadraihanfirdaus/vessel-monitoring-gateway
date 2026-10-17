# Pre-Phase 9 F05 — Clean Public Archive Procedure

**Status:** IMPLEMENTATION CHECK PASS — post-commit archive evidence pending

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
