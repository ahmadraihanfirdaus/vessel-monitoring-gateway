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
    print(f"F2_HOST: FAIL - {msg}")
    raise SystemExit(1)

gcc = shutil.which("gcc")
if not gcc:
    fail("gcc not found")

# Preserve the committed F1 gate, which itself runs the prior regression chain.
p = run([sys.executable, str(ROOT / "scripts" / "test_phase6_f1_host.py")])
if p.returncode != 0:
    fail("F1 regression returned nonzero", p.stdout)

m_f1 = re.search(
    r"PHASE6_F1_HOST_SELFTEST:\s+PASS\s+\((\d+)/(\d+)\)",
    p.stdout,
)
if not m_f1 or m_f1.group(1) != "62" or m_f1.group(2) != "62":
    fail("F1 host 62/62 PASS marker missing", p.stdout)

source = """
#include "phase6_f2_formal_scenarios.h"

int main(void)
{
    run_phase6_f2_formal_scenarios();
    return 0;
}
"""

with tempfile.TemporaryDirectory(prefix="vg_f2_") as td:
    td = pathlib.Path(td)
    c = td / "f2_runner.c"
    exe = td / ("f2_runner.exe" if os.name == "nt" else "f2_runner")
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
        fail("F2 compile failed", p.stdout)

    p = run([str(exe)])
    if p.returncode != 0:
        fail("F2 runner failed", p.stdout)

required = [
    "F2_SIM007_CHECK FOUR_ENGINE_PROFILE: PASS",
    "F2_SIM007_CHECK INPUT_ENGINE3_LOWER: PASS",
    "F2_SIM007_CHECK CONFIGURABLE_THRESHOLD: PASS",
    "F2_SIM007_CHECK ENGINE3_EVALUATED: PASS",
    "F2_SIM007_CHECK ENGINE3_DEVIATION_WARNING: PASS",
    "F2_SIM007_CHECK PEERS_NO_FALSE_WARNING: PASS",
    "F2_FORMAL_SCENARIO SIM-007: PASS",
    "PHASE6_F2_FORMAL_SCENARIOS: PASS (1/1)",
]
missing = [marker for marker in required if marker not in p.stdout]
if missing:
    fail("formal SIM-007 host markers missing: " + ", ".join(missing), p.stdout)

if re.search(r"(^|\s)FAIL(?:\s|:|\()", p.stdout):
    fail("F2 runner printed FAIL", p.stdout)

print(f"F2_HOST_C_COMPILER: {gcc}")
print("F2_F1_REGRESSION: PASS (62/62)")
print("PHASE6_F2_HOST_FORMAL_SCENARIOS: PASS (1/1)")
print(
    "NOTE: Host execution is preparation only. Formal SIM-007 roadmap evidence "
    "requires fresh target/Wokwi execution and persisted evidence."
)
