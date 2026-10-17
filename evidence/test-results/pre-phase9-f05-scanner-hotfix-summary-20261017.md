# Pre-Phase 9 F05 Scanner Hotfix Summary

**Decision:** `F05_SCANNER_HOTFIX_PRECOMMIT_PASS`

The first post-commit F05 archive run was blocked by scanner false positives,
not by a confirmed secret or machine-local user path leak.

The scanner now:

- still detects concrete `C:\Users\<account>\...` paths;
- still detects concrete `C:/Users/<account>/...` paths;
- still detects concrete `/c/Users/<account>/...` Git Bash paths;
- does not classify the documentation placeholder `<user>` as a concrete leak;
- does not match the scanner's own source-pattern text.

Focused scanner regression: PASS (5/5).
Tracked-only archive probe: PASS.
F01 regression: PASS.
Automated security screen: PASS.
LOCKED SHA gate: PASS (2/2).

Post-commit archive evidence remains NOT_RUN until this hotfix is committed.
Total system status remains PARTIAL and Phase 9 has not started.
