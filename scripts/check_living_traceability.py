#!/usr/bin/env python3
"""Audit the editable living registry against locked mappings and test-level execution records."""
from __future__ import annotations
import csv
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCKS = {
    "requirements/system-requirements.md": "a60167d9f2a1f852a091048447f6f4acf8d2cbfd6d11f04c2a6e2f6896f5b92b",
    "requirements/traceability-matrix.csv": "bc1fc7ce697fc6180cab760320de2a1bd814f9bc78731d4a22fdae838c303fe3",
}
FIELDS = (
    "requirement_id", "planned_test_ids", "implementation_assessment",
    "formal_verification", "implementation_path", "internal_evidence_path", "qualification",
)


def rows(path: str):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def mapped_status(test_ids: list[str], sim: dict[str, str], sup: dict[str, str]) -> str:
    states = []
    for tid in test_ids:
        if tid.startswith("SIM-"):
            states.append(sim[tid])
        elif tid.startswith("SUP-"):
            raw = sup[tid]
            states.append("NOT_RUN" if raw == "PLANNED" else raw)
        else:
            raise ValueError(f"Unknown test ID: {tid}")
    if any(s == "FAIL" for s in states):
        return "FAIL"
    if states and all(s == "PASS" for s in states):
        return "PASS"
    if any(s == "PASS" for s in states):
        return "PARTIAL"
    if any(s == "BLOCKED" for s in states):
        return "BLOCKED"
    return "NOT_RUN"


def check():
    for name, digest in LOCKS.items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"LOCKED hash mismatch: {name}")

    _, base = rows("requirements/traceability-matrix.csv")
    columns, live = rows("docs/testing/living-requirement-status.csv")
    sim_columns, sim_rows = rows("docs/testing/formal-scenario-status.csv")
    sup_columns, sup_rows = rows("docs/testing/supplemental-verification-plan.csv")

    if columns != list(FIELDS):
        raise ValueError("Living registry columns changed")
    if sim_columns != ["test_id", "execution_status", "evidence_path", "qualification"]:
        raise ValueError("Formal scenario registry columns changed")
    if sup_columns is None or "test_id" not in sup_columns or "execution_status" not in sup_columns:
        raise ValueError("Supplemental plan columns invalid")
    if len(base) != 38 or len(live) != 38:
        raise ValueError(f"Expected 38 entries, got baseline={len(base)}, registry={len(live)}")

    reference = {r["requirement_id"]: r for r in base}
    live_ids = {r["requirement_id"] for r in live}
    if len(reference) != 38 or len(live_ids) != 38 or live_ids != set(reference):
        raise ValueError("Requirement ID mismatch/duplicate")

    sim = {r["test_id"]: r["execution_status"] for r in sim_rows}
    sup = {r["test_id"]: r["execution_status"] for r in sup_rows}
    expected_sim = {f"SIM-{i:03d}" for i in range(1, 16)}
    expected_sup = {f"SUP-{i:03d}" for i in range(1, 20)}
    if set(sim) != expected_sim:
        raise ValueError("Formal scenario registry must contain SIM-001..SIM-015 exactly once")
    if set(sup) != expected_sup:
        raise ValueError("Supplemental plan must contain SUP-001..SUP-019 exactly once")

    allowed_exec = {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}
    for r in sim_rows:
        if r["execution_status"] not in allowed_exec:
            raise ValueError(f"Invalid SIM execution status: {r['test_id']}")
        p = r["evidence_path"]
        if r["execution_status"] == "PASS" and not p:
            raise ValueError(f"PASS SIM missing evidence: {r['test_id']}")
        if p and (p.startswith("/") or ".." in Path(p).parts or not (ROOT / p).is_file()):
            raise ValueError(f"Invalid SIM evidence path: {r['test_id']} -> {p}")

    allowed_sup = {"PLANNED", "NOT_RUN", "PASS", "FAIL", "BLOCKED"}
    for r in sup_rows:
        if r["execution_status"] not in allowed_sup:
            raise ValueError(f"Invalid SUP execution status: {r['test_id']}")
        p = r.get("evidence_path", "")
        if r["execution_status"] == "PASS" and not p:
            raise ValueError(f"PASS SUP missing evidence: {r['test_id']}")
        if p and (p.startswith("/") or ".." in Path(p).parts or not (ROOT / p).is_file()):
            raise ValueError(f"Invalid SUP evidence path: {r['test_id']} -> {p}")

    assessments = {"NOT_STARTED", "PARTIAL", "IMPLEMENTED_UNVERIFIED", "VERIFIED"}
    formal = {"NOT_RUN", "PARTIAL", "PASS", "FAIL", "BLOCKED"}
    assessment_counts = Counter()
    formal_counts = Counter()

    for r in live:
        rid = r["requirement_id"]
        if r["planned_test_ids"] != reference[rid]["test_ids"]:
            raise ValueError(f"Changed test IDs: {rid}")
        assessment = r["implementation_assessment"]
        fstatus = r["formal_verification"]
        if assessment not in assessments or fstatus not in formal:
            raise ValueError(f"Invalid status: {rid}")
        if assessment == "VERIFIED":
            raise ValueError(f"VERIFIED requires a later dedicated requirement-approval gate: {rid}")

        test_ids = [x for x in r["planned_test_ids"].split(";") if x]
        derived = mapped_status(test_ids, sim, sup)
        if fstatus != derived:
            raise ValueError(f"Formal status mismatch: {rid}: registry={fstatus}, derived={derived}")

        paths = [p for p in (r["implementation_path"] + ";" + r["internal_evidence_path"]).split(";") if p]
        for p in paths:
            if p.startswith("/") or ".." in Path(p).parts or not (ROOT / p).is_file():
                raise ValueError(f"Invalid referenced path for {rid}: {p}")
        if assessment == "NOT_STARTED" and paths:
            raise ValueError(f"NOT_STARTED row has path: {rid}")
        if assessment in {"PARTIAL", "IMPLEMENTED_UNVERIFIED"} and not paths:
            raise ValueError(f"{assessment} row missing references: {rid}")

        assessment_counts[assessment] += 1
        formal_counts[fstatus] += 1

    print("BASELINE_SHA256: PASS (2/2)")
    print("LIVING_TRACEABILITY: PASS (38/38 mapped, 34 unique planned cases)")
    print(f"ASSESSMENTS: {dict(sorted(assessment_counts.items()))}")
    print(f"FORMAL_REQUIREMENT_STATUS: {dict(sorted(formal_counts.items()))}")
    print(f"FORMAL_SIM_SCENARIOS: PASS={sum(1 for s in sim.values() if s == 'PASS')}, NOT_RUN={sum(1 for s in sim.values() if s == 'NOT_RUN')}")
    print(f"SUPPLEMENTAL_TESTS: PLANNED={sum(1 for s in sup.values() if s == 'PLANNED')}, PASS={sum(1 for s in sup.values() if s == 'PASS')}")
    print("FINAL_REQUIREMENT_APPROVAL: NOT_APPROVED")
    print("TOTAL_SYSTEM_STATUS: PARTIAL")


if __name__ == "__main__":
    try:
        check()
    except (ValueError, OSError, KeyError) as err:
        print(f"FAIL: {err}", file=__import__('sys').stderr)
        raise SystemExit(1)
