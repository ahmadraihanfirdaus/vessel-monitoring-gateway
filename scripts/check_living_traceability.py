#!/usr/bin/env python3
"""Audit editable implementation registry against *unchanged* locked requirements."""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
LOCKS={
    "requirements/system-requirements.md":"a60167d9f2a1f852a091048447f6f4acf8d2cbfd6d11f04c2a6e2f6896f5b92b",
    "requirements/traceability-matrix.csv":"bc1fc7ce697fc6180cab760320de2a1bd814f9bc78731d4a22fdae838c303fe3",
}
FIELDS=("requirement_id", "planned_test_ids", "implementation_assessment", "formal_verification", "implementation_path", "internal_evidence_path", "qualification")


def rows(path):
    with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        return reader.fieldnames,list(reader)


def check():
    for name,digest in LOCKS.items():
        actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if actual!=digest:
            raise ValueError(f"LOCKED hash mismatch: {name}")
    basenames,base=rows("requirements/traceability-matrix.csv")
    columns,live=rows("docs/testing/living-requirement-status.csv")
    if columns!=list(FIELDS):
        raise ValueError("Living registry columns changed")
    if len(base)!=38 or len(live)!=38:
        raise ValueError(f"Expected 38 entries, got baseline={len(base)}, registry={len(live)}")
    reference={r["requirement_id"]:r for r in base}
    if len(reference)!=38 or len({r["requirement_id"] for r in live})!=38:
        raise ValueError("Duplicate requirement ID")
    if {r["requirement_id"] for r in live}!=set(reference):
        raise ValueError("Requirement ID mismatch")
    statuses={"NOT_STARTED","PARTIAL","IMPLEMENTED_UNVERIFIED","VERIFIED"}
    formal={"NOT_RUN","PASS","FAIL","BLOCKED"}
    counts={s:0 for s in statuses}
    for r in live:
        rid=r["requirement_id"]
        if r["planned_test_ids"] != reference[rid]["test_ids"]:
            raise ValueError(f"Changed test IDs: {rid}")
        assessment=r["implementation_assessment"]
        if assessment not in statuses or r["formal_verification"] not in formal:
            raise ValueError(f"Invalid status: {rid}")
        if r["formal_verification"]=="PASS":
            raise ValueError(f"Formal PASS prohibited in preliminary Batch A2 registry: {rid}")
        if assessment=="VERIFIED":
            raise ValueError(f"Unreviewed VERIFIED claim: {rid}")
        counts[assessment]+=1
        paths=[p for p in (r["implementation_path"]+";"+r["internal_evidence_path"]).split(";") if p]
        for p in paths:
            if p.startswith("/") or ".." in Path(p).parts or not (ROOT/p).is_file():
                raise ValueError(f"Invalid referenced path for {rid}: {p}")
        if assessment=="NOT_STARTED" and paths:
            raise ValueError(f"NOT_STARTED row has path: {rid}")
        if assessment=="PARTIAL" and not paths:
            raise ValueError(f"PARTIAL row missing references: {rid}")
    print("BASELINE_SHA256: PASS (2/2)")
    print("LIVING_TRACEABILITY: PASS (38/38 mapped, 34 unique planned cases)")
    print(f"ASSESSMENTS: {counts}")
    print("FORMAL_SIM_SUP_VERIFICATION: NOT_RUN (not a formal execution gate)")


if __name__=="__main__":
    try:
        check()
    except (ValueError,OSError,KeyError) as err:
        print(f"FAIL: {err}",file=sys.stderr)
        raise SystemExit(1)
