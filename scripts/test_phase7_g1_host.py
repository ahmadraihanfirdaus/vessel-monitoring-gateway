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
    print(f"G1_HOST: FAIL - {msg}")
    raise SystemExit(1)

gcc = shutil.which("gcc")
if not gcc:
    fail("gcc not found")

# Preserve the committed Phase 6 formal-host regression chain.
p = run([sys.executable, str(ROOT / "scripts" / "test_phase6_f2_formal_host.py")])
if p.returncode != 0:
    fail("Phase 6 F2 regression returned nonzero", p.stdout)

if "PHASE6_F2_HOST_FORMAL_SCENARIOS: PASS (1/1)" not in p.stdout:
    fail("Phase 6 F2 host formal marker missing", p.stdout)

source = """
#include "phase7_g1_selftest.h"

int main(void)
{
    run_phase7_g1_navigation_selftest();
    return 0;
}
"""

with tempfile.TemporaryDirectory(prefix="vg_g1_") as td:
    td = pathlib.Path(td)
    c = td / "g1_runner.c"
    exe = td / ("g1_runner.exe" if os.name == "nt" else "g1_runner")
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
        fail("G1 compile failed", p.stdout)

    p = run([str(exe)])
    if p.returncode != 0:
        fail("G1 runner failed", p.stdout)

m = re.search(
    r"PHASE7_G1_NAVIGATION_SELFTEST:\s+PASS\s+\((\d+)/(\d+)\)",
    p.stdout,
)
if not m or m.group(1) != "64" or m.group(2) != "64":
    fail("G1 navigation 64/64 PASS marker missing", p.stdout)

if re.search(r"(^|\s)FAIL(?:\s|:|\()", p.stdout):
    fail("G1 runner printed FAIL", p.stdout)

print(f"G1_HOST_C_COMPILER: {gcc}")
print("G1_PHASE6_REGRESSION: PASS")
print("PHASE7_G1_HOST_SELFTEST: PASS (64/64)")
print(
    "NOTE: Development host evidence only. Formal SIM-008/SIM-009, SUP-007, "
    "physical GNSS/NMEA bench verification and production readiness are not implied."
)
