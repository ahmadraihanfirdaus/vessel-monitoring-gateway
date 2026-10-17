# Living Traceability Register — Current Development Companion

`requirements/system-requirements.md` and `requirements/traceability-matrix.csv` are **LOCKED** (SHA-256 enforced). Their historic `NOT_IMPLEMENTED`/`NOT_RUN` snapshot remains untouched.

The editable companion [`living-requirement-status.csv`](living-requirement-status.csv) records the current evidence-qualified engineering assessment for all 38 IDs while preserving the exact baseline planned-test mappings. It is reconciled against completed roadmap work through Phase 8 and the pre-Phase-9 R1 repair gate.

Status fields are intentionally split:

- `implementation_assessment`: `NOT_STARTED` = no complete implementation exists; `PARTIAL` = relevant foundation exists but requirement scope is incomplete; `IMPLEMENTED_UNVERIFIED` = the development implementation exists but requirement-level verification/approval is incomplete; `VERIFIED` = independently reviewed complete requirement evidence. This register currently makes no `VERIFIED` claims.
- `formal_verification`: `NOT_RUN`, `PARTIAL`, `PASS`, `FAIL`, or `BLOCKED`. `PASS` means every mapped formal SIM/SUP case currently recorded for that requirement has accepted PASS evidence; `PARTIAL` means at least one mapped case has accepted PASS evidence while another mapped case remains open. A formal test PASS does **not** automatically make the whole requirement `VERIFIED`.
- `internal_evidence_path`: implementation/development or formal evidence supporting the current assessment. Evidence references do not authorize hardware, certification, production, or publication claims beyond their recorded scope.

Formal SIM execution is tracked separately in [`formal-scenario-status.csv`](formal-scenario-status.csv). Supplemental test execution remains in [`supplemental-verification-plan.csv`](supplemental-verification-plan.csv). The living checker derives each requirement's `formal_verification` from those test-level records rather than hard-coding a preliminary Batch A2 prohibition.

Run: `python scripts/check_living_traceability.py`. The checker requires all 38 IDs, exact planned test mappings, legal statuses, existing evidence paths, consistent SIM/SUP-derived formal status, and unchanged LOCKED hashes.

The register is still an engineering tracking aid, not final verification approval or SUP-017 execution. Physical/bench claims require separately authorized evidence. Phase 9 backend work, SIM-010..SIM-015 where not already executed, supplemental tests SUP-001..SUP-019, hardware bench verification, calibration, field validation, certification, and production readiness remain governed by their own gates.
