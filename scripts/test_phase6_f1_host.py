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
    print(f"F1_HOST: FAIL - {msg}")
    raise SystemExit(1)

gcc = shutil.which("gcc")
if not gcc:
    fail("gcc not found")

prior = [
    ("scripts/test_firmware_core_host.py",
     r"HOST_FIRMWARE_CORE_SELFTEST:\s+PASS\s+\(226/226\)"),

    ("scripts/test_phase4_d1_host.py",
     r"(?:PHASE4_D1_HOST_SELFTEST|D1_PROVIDER_SELFTEST):\s+PASS\s+\(38/38\)"),
    ("scripts/test_phase4_d2_host.py",
     r"(?:PHASE4_D2_HOST_SELFTEST|D2_PROVIDER_SELFTEST):\s+PASS\s+\(53/53\)"),
    ("scripts/test_phase4_d3_host.py",
     r"(?:PHASE4_D3_HOST_SELFTEST|D3_PROVIDER_SELFTEST):\s+PASS\s+\(47/47\)"),
    ("scripts/test_phase4_d4_host.py",
     r"(?:PHASE4_D4_HOST_SELFTEST|D4_PROVIDER_SELFTEST):\s+PASS\s+\(67/67\)"),
    ("scripts/test_phase4_d5_host.py",
     r"(?:PHASE4_D5_HOST_SELFTEST|D5_PROVIDER_SELFTEST):\s+PASS\s+\(54/54\)"),
    ("scripts/test_phase4_d6_host.py",
     r"(?:PHASE4_D6_HOST_SELFTEST|D6_PROVIDER_SELFTEST):\s+PASS\s+\(61/61\)"),
    ("scripts/test_phase4_d7_host.py",
     r"(?:PHASE4_D7_HOST_SELFTEST|D7_PROVIDER_SELFTEST):\s+PASS\s+\(61/61\)"),

    ("scripts/test_phase5_e1_host.py",
     r"PHASE5_E1_HOST_SELFTEST:\s+PASS\s+\(51/51\)"),
    ("scripts/test_phase5_e2_host.py",
     r"PHASE5_E2_HOST_SELFTEST:\s+PASS\s+\(60/60\)"),
    ("scripts/test_phase5_e3_host.py",
     r"PHASE5_E3_HOST_SELFTEST:\s+PASS\s+\(85/85\)"),
    ("scripts/test_phase5_e4_formal_host.py",
     r"PHASE5_E4_HOST_FORMAL_SCENARIOS:\s+PASS\s+\(6/6\)"),
]

for rel, pattern in prior:
    path = ROOT / rel
    if not path.is_file():
        fail(f"missing prior regression entrypoint: {rel}")

    p = run([sys.executable, str(path)])
    if p.returncode != 0:
        fail(f"prior regression returned nonzero: {rel}", p.stdout)

    if re.search(r"(^|\s)FAIL(?:\s|:|\()", p.stdout):
        fail(f"prior regression printed FAIL: {rel}", p.stdout)

    if not re.search(pattern, p.stdout):
        fail(f"prior PASS marker/total not found: {rel}", p.stdout)

source = """
#include "phase6_f1_selftest.h"

int main(void)
{
    run_phase6_f1_engine_model_selftest();
    return 0;
}
"""

with tempfile.TemporaryDirectory(prefix="vg_f1_") as td:
    td = pathlib.Path(td)
    c = td / "f1_runner.c"
    exe = td / ("f1_runner.exe" if os.name == "nt" else "f1_runner")
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
        fail("F1 compile failed", p.stdout)

    p = run([str(exe)])
    if p.returncode != 0:
        fail("F1 runner failed", p.stdout)

m = re.search(
    r"PHASE6_F1_ENGINE_MODEL_SELFTEST:\s+PASS\s+\((\d+)/(\d+)\)",
    p.stdout,
)
if not m or m.group(1) != m.group(2):
    fail("F1 PASS marker missing", p.stdout)

total = int(m.group(2))
if total != 62:
    fail(f"unexpected F1 self-test total: {total}; expected 62", p.stdout)

print(f"F1_HOST_C_COMPILER: {gcc}")
print("F1_PRIOR_REGRESSIONS: PASS")
print(f"PHASE6_F1_HOST_SELFTEST: PASS ({total}/{total})")
print(
    "NOTE: Development host evidence only; formal SIM-007, physical engine "
    "integration, bench hardware and production readiness are not implied."
)
