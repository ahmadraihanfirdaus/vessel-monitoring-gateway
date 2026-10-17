#!/usr/bin/env python3
from __future__ import annotations
import csv
import hashlib
from collections import Counter
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCKS = {
    "requirements/system-requirements.md": "a60167d9f2a1f852a091048447f6f4acf8d2cbfd6d11f04c2a6e2f6896f5b92b",
    "requirements/traceability-matrix.csv": "bc1fc7ce697fc6180cab760320de2a1bd814f9bc78731d4a22fdae838c303fe3",
}


def read_csv(path):
    with (ROOT/path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def require(cond, name):
    print(f"F01_STATUS_TEST {name}: {'PASS' if cond else 'FAIL'}")
    if not cond:
        raise SystemExit(1)


def main():
    for p,d in LOCKS.items():
        require(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d, f"LOCKED_{Path(p).name}")

    sim=read_csv("docs/testing/formal-scenario-status.csv")
    require(len(sim)==15, "SIM_ROW_COUNT")
    sm={r['test_id']:r['execution_status'] for r in sim}
    require(all(sm[f"SIM-{i:03d}"]=="PASS" for i in range(1,10)), "SIM001_009_PASS")
    require(all(sm[f"SIM-{i:03d}"]=="NOT_RUN" for i in range(10,16)), "SIM010_015_NOT_RUN")

    live=read_csv("docs/testing/living-requirement-status.csv")
    require(len(live)==38, "LIVING_38_ROWS")
    ac=Counter(r['implementation_assessment'] for r in live)
    fc=Counter(r['formal_verification'] for r in live)
    require(ac==Counter({'IMPLEMENTED_UNVERIFIED':18,'PARTIAL':12,'NOT_STARTED':8}), "IMPLEMENTATION_COUNTS")
    require(fc==Counter({'NOT_RUN':25,'PASS':10,'PARTIAL':3}), "FORMAL_COUNTS")
    require(not any(r['implementation_assessment']=='VERIFIED' for r in live), "NO_VERIFIED_CLAIM")

    target_files=[
        'README.md','docs/github-repository-plan.md','docs/testing/traceability-status.md',
        'docs/testing/living-traceability-guide.md','docs/testing/firmware-evidence-index.md'
    ]
    joined='\n'.join((ROOT/p).read_text(encoding='utf-8') for p in target_files)
    stale=[
        'Phase 4 NOT_STARTED',
        'Formal SIM/SUP NOT_RUN',
        'next work is to complete Firmware Core Phase 3',
        'partial Phase 3 firmware implementation',
        'prohibits `VERIFIED` or formal `PASS` claims in the initial Batch A2 register',
    ]
    require(not any(x in joined for x in stale), "STALE_PHASE3_A2_TEXT_REMOVED")
    require('SIM-001..SIM-009 PASS' in joined or 'SIM-001 through SIM-009' in joined, "CURRENT_SIM_STATUS_PRESENT")
    require('Phase 9 NOT_STARTED' in joined or 'Phase 9 Laravel/MySQL has not started' in joined, "PHASE9_NOT_STARTED_PRESENT")
    require('SUP-001..SUP-019' in joined or 'SUP-001 through SUP-019' in joined, "SUP_OPEN_STATUS_PRESENT")

    p=subprocess.run([sys.executable, str(ROOT/'scripts/check_living_traceability.py')], cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end='')
    if p.stderr: print(p.stderr, end='', file=sys.stderr)
    require(p.returncode==0, "LIVING_CHECKER_RUN")
    require('FORMAL_SIM_SCENARIOS: PASS=9, NOT_RUN=6' in p.stdout, "CHECKER_SIM_COUNTS")
    require('TOTAL_SYSTEM_STATUS: PARTIAL' in p.stdout, "SYSTEM_PARTIAL")

    print('PRE_PHASE9_F01_STATUS_TEST: PASS')

if __name__=='__main__':
    main()
