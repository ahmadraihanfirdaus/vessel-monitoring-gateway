#!/usr/bin/env python3
"""Audit the editable living registry against locked mappings and test-level execution records."""
from __future__ import annotations
import csv
import hashlib
import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
LOCKS = {
    "requirements/system-requirements.md": "a60167d9f2a1f852a091048447f6f4acf8d2cbfd6d11f04c2a6e2f6896f5b92b",
    "requirements/traceability-matrix.csv": "bc1fc7ce697fc6180cab760320de2a1bd814f9bc78731d4a22fdae838c303fe3",
}
FIELDS = (
    "requirement_id", "planned_test_ids", "implementation_assessment",
    "formal_verification", "implementation_path", "internal_evidence_path", "qualification",
)


def public_parts(relative):
    if (not isinstance(relative, str) or not relative or len(relative) > 512
            or not re.fullmatch(r'[A-Za-z0-9_./-]+', relative)
            or PurePosixPath(relative).is_absolute()):
        raise ValueError('Invalid public reference spelling')
    parts = relative.split('/')
    forbidden = {'.git', '.aws', '.codex', '.agents', 'credentials', 'credentials.json',
                 'secrets.json', 'tokens.json', 'id_rsa', 'id_ed25519'}
    if (any(p in ('', '.', '..') or p.lower() in forbidden or p.lower().startswith('.env') for p in parts)
            or PurePosixPath(relative).suffix.lower() in {'.key', '.pem', '.p12', '.pfx'}):
        raise ValueError('Sensitive or noncanonical reference refused')
    return parts


def public_reference(relative, root=None):
    root = Path(root or ROOT).resolve()
    parts = public_parts(relative)
    path = root.joinpath(*parts)
    cursor = path
    while cursor != root:
        if cursor.is_symlink() or (hasattr(cursor, 'is_junction') and cursor.is_junction()):
            raise ValueError('Linked public reference refused')
        cursor = cursor.parent
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('Foreign or nonregular reference refused')
    public_parts(resolved.relative_to(root).as_posix())
    before = resolved.stat()
    digest = hashlib.sha256()
    with resolved.open('rb') as handle:
        for block in iter(lambda: handle.read(131072), b''):
            digest.update(block)
    after = resolved.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('Reference changed during hash read')
    return {'sha256': digest.hexdigest(), 'bytes': after.st_size}


def inventory_reference(relative):
    # SEC002 legitimately references the tracked configuration TEMPLATE. Resolve
    # and stat that exact file only; never open/hash any dotenv content.
    if relative != 'backend/laravel/.env.example':
        return public_reference(relative)
    root = ROOT.resolve()
    target = root/relative
    cursor = target
    while cursor != root:
        if cursor.is_symlink() or (hasattr(cursor, 'is_junction') and cursor.is_junction()):
            raise ValueError('Linked template reference refused')
        cursor = cursor.parent
    if not target.resolve(strict=True).is_relative_to(root) or not target.is_file():
        raise ValueError('Foreign template reference refused')
    metadata = target.stat()
    return dict(sha256=None, bytes=metadata.st_size, mtime_ns=metadata.st_mtime_ns,
                qualification='PROTECTED_TEMPLATE_METADATA_ONLY_NO_CONTENT_READ_OR_HASH')


def rows(path: str):
    public_reference(path)
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        if not fields or len(fields) != len(set(fields)) or any(not name for name in fields):
            raise ValueError('Duplicate or empty registry header')
        data = list(reader)
        if any(set(row) != set(fields) or any(value is None for value in row.values()) for row in data):
            raise ValueError('Registry row cardinality mismatch')
        return fields, data


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
    registry_names = list(LOCKS) + ['docs/testing/living-requirement-status.csv',
        'docs/testing/formal-scenario-status.csv', 'docs/testing/supplemental-verification-plan.csv']
    registry_before = {name: public_reference(name) for name in registry_names}
    for name, digest in LOCKS.items():
        actual = registry_before[name]['sha256']
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
    if sup_columns != ['test_id', 'requirement_id', 'verification_type', 'planned_verification',
                       'expected_result', 'execution_status', 'evidence_path']:
        raise ValueError("Supplemental plan columns invalid")
    if len(sim_rows) != 15 or len(sup_rows) != 19:
        raise ValueError('Duplicate or missing canonical case rows')
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
    definition_path = 'docs/testing/verification-simulation-plan.md'
    public_reference(definition_path)
    defined_sim = re.findall(r'^\| (SIM-\d{3}) \|', (ROOT/definition_path).read_text(encoding='utf-8'), re.M)
    if Counter(defined_sim) != Counter(expected_sim):
        raise ValueError('Simulation plan definitions missing or duplicated')
    verification_types = {'documentation', 'contract', 'static_review', 'unit', 'simulation',
                          'security_review', 'integration', 'functional', 'traceability_audit', 'ci'}
    for row in sup_rows:
        if (row['requirement_id'] not in reference
                or row['test_id'] not in reference[row['requirement_id']]['test_ids'].split(';')
                or row['verification_type'] not in verification_types
                or not row['planned_verification'].strip() or not row['expected_result'].strip()):
            raise ValueError('Supplemental definition/type/requirement mapping invalid')

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
    # Separate public-link inventory; this does not approve implementation or
    # infer execution for planned/hardware cases from mere file presence.
    files = dict(registry_before)
    def reference(name):
        if name not in files:
            files[name] = inventory_reference(name)
        return name
    definitions = {'SIM': 'docs/testing/verification-simulation-plan.md',
                   'SUP': 'docs/testing/supplemental-verification-plan.csv'}
    cases = {r['test_id']:r for r in sim_rows + sup_rows}
    inventory = []
    for row in live:
        sources = list(dict.fromkeys(p for p in row['implementation_path'].split(';') if p))
        evidence = list(dict.fromkeys(p for p in row['internal_evidence_path'].split(';') if p))
        for path in sources + evidence:
            reference(path)
        tests = []
        for case in row['planned_test_ids'].split(';'):
            definition = reference(definitions[case[:3]])
            recorded = cases[case]
            artifact = recorded.get('evidence_path', '')
            if artifact:
                reference(artifact)
            tests.append(dict(test_id=case, definition_path=definition,
                              execution_status=recorded['execution_status'], evidence_path=artifact))
        inventory.append(dict(requirement_id=row['requirement_id'],
            implementation_assessment=row['implementation_assessment'], formal_verification=row['formal_verification'],
            implementation_paths=sources, internal_evidence_paths=evidence, tests=tests))
    for name, expected in files.items():
        if inventory_reference(name) != expected:
            raise ValueError('Reference inventory changed during audit')
    print(f'PUBLIC_REFERENCE_AUDIT: PASS (38 requirements, {len(files)} file references; protected template metadata only; no DB/network)')
    return dict(requirements=inventory, public_files=files, registry_hashes=registry_before,
                requirement_count=38, planned_case_count=34, database_access=False,
                hardware_verification=False, requirement_approval='NOT_APPROVED')


def save_report(path, report):
    root = ROOT.resolve()
    target = path.resolve()
    if (not target.is_relative_to(root) or target.parent != root/'evidence/test-results'
            or not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,100}\.json', target.name)):
        raise ValueError('Report must be a new named public evidence JSON')
    public_parts(target.relative_to(root).as_posix())
    if path.is_symlink() or target.parent.is_symlink() or target.exists():
        raise ValueError('Existing or linked report output refused')
    with target.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--report', type=Path)
        args = parser.parse_args()
        if args.report:
            protocol = 'docs/testing/formal-public-reference-audit-20261026.md'
            public_reference(protocol)
            if 'PROTOCOL_CASE_REVIEW=PASS_SUP017_READ_ONLY_PUBLIC_REFERENCE_AUDIT' not in (ROOT/protocol).read_text(encoding='utf-8'):
                raise ValueError('Dedicated reference protocol review required')
            reviewed_inputs = {name:public_reference(name) for name in ('scripts/check_living_traceability.py', protocol)}
        result = check()
        if args.report:
            if any(public_reference(name) != expected for name, expected in reviewed_inputs.items()):
                raise ValueError('Audit tool/protocol changed during execution')
            result.update(parent_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                tool_sha256=public_reference('scripts/check_living_traceability.py')['sha256'],
                protocol_path=protocol, protocol_sha256=public_reference(protocol)['sha256'])
            save_report(args.report, result)
            print('PUBLIC_REFERENCE_REPORT: PASS_NEW_ARTIFACT_NO_EXISTING_FILE_OVERWRITE')
    except (ValueError, OSError, KeyError) as err:
        print(f"FAIL: {err}", file=__import__('sys').stderr)
        raise SystemExit(1)
