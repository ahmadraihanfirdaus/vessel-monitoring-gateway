# Living Traceability Register — Batch A2

`requirements/system-requirements.md` and `requirements/traceability-matrix.csv` are **LOCKED** (SHA-256 enforced). Their historic `NOT_IMPLEMENTED`/`NOT_RUN` values intentionally remain untouched.

The editable companion file [`living-requirement-status.csv`](living-requirement-status.csv) records an evidence-qualified engineering assessment for **all 38 IDs**, with the identical baseline planned-test mappings. Status fields are intentionally split:

- `implementation_assessment`: `NOT_STARTED` = no code found for complete requirement, `PARTIAL` = supporting foundation exists but acceptance behavior not implemented, `IMPLEMENTED_UNVERIFIED` = code exists without formal accepted verification, `VERIFIED` = independently reviewed complete requirement evidence.
- `formal_verification`: `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED` for actual SIM/SUP execution, **not** for adjacent self-tests.
- `internal_evidence_path`: sources of prior *development-only* checks. An existing file is **not** evidence of completion of its mapped SIM/SUP case.

Run: `python scripts/check_living_traceability.py`. The checker requires all 38 IDs, their exact planned test IDs, legal statuses, actual referenced files and locked hashes. It explicitly prohibits `VERIFIED` or formal `PASS` claims in the initial Batch A2 register.

The check is an integrity gate, not a formal execution of SUP-017. Subsequent versions must require actual execution logs, commit hashes, test environment, expected/actual outcomes and approval before any `VERIFIED` row. All physical/bench claims require separately authorized evidence.
