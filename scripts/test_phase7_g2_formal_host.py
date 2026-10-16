#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "src"

def run(cmd):
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

def fail(msg, output=""):
    if output:
        print(output, end="" if output.endswith("\n") else "\n")
    print(f"G2_HOST: FAIL - {msg}")
    raise SystemExit(1)

gcc = shutil.which("gcc")
if not gcc:
    fail("gcc not found")

# Preserve the committed Phase 7 G1 host regression chain.
p = run([sys.executable, str(ROOT / "scripts" / "test_phase7_g1_host.py")])
if p.returncode != 0:
    fail("Phase 7 G1 regression returned nonzero", p.stdout)

if "PHASE7_G1_HOST_SELFTEST: PASS (64/64)" not in p.stdout:
    fail("Phase 7 G1 host marker missing", p.stdout)

source = """
#include "phase7_g2_formal_scenarios.h"

int main(void)
{
    run_phase7_g2_formal_scenarios();
    return 0;
}
"""

with tempfile.TemporaryDirectory(prefix="vg_g2_") as td:
    td = pathlib.Path(td)
    c = td / "g2_runner.c"
    exe = td / ("g2_runner.exe" if os.name == "nt" else "g2_runner")
    c.write_text(source, encoding="utf-8")

    p = run([
        gcc,
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-I",
        str(FW),
        str(c),
        "-lm",
        "-o",
        str(exe),
    ])
    if p.returncode != 0:
        fail("G2 compile failed", p.stdout)

    p = run([str(exe)])
    if p.returncode != 0:
        fail("G2 runner failed", p.stdout)

required = [
    "G2_FORMAL_SCENARIO SIM-008: PASS",
    "G2_FORMAL_SCENARIO SIM-009: PASS",
    "PHASE7_G2_FORMAL_SCENARIOS: PASS (2/2)",
]
missing = [m for m in required if m not in p.stdout]
if missing:
    fail("G2 formal PASS markers missing: " + ", ".join(missing), p.stdout)

if re.search(r"(^|\s)FAIL(?:\s|:|\()", p.stdout):
    fail("G2 runner printed FAIL", p.stdout)

print(f"G2_HOST_C_COMPILER: {gcc}")
print("G2_G1_REGRESSION: PASS")
print("PHASE7_G2_HOST_FORMAL_SCENARIOS: PASS (2/2)")
print(
    "NOTE: Host execution is preparation only. Formal roadmap evidence requires "
    "fresh target/Wokwi execution and persisted evidence."
)
