#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "src"
FIX = ROOT / "docs" / "testing" / "fixtures" / "phase8-h1"
SCHEMA = ROOT / "docs" / "contracts" / "telemetry-schema-v1.json"

SAFE = re.compile(r"^[A-Za-z0-9._:-]+$")
SOURCE = {"simulation", "bench_test", "physical"}
QUALITY = {"valid", "invalid", "missing", "stale", "unknown"}
REQ = {
    "schema_version", "device_id", "firmware_version", "boot_id",
    "sequence", "uptime_ms", "source_mode", "channels"
}

def fail(msg, output=""):
    if output:
        print(output, end="" if output.endswith("\n") else "\n")
    print(f"H1_HOST: FAIL - {msg}")
    raise SystemExit(1)

def run(cmd):
    return subprocess.run(
        cmd, cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

def valid_payload(p):
    if not isinstance(p, dict) or set(p) != REQ:
        return False
    if p["schema_version"] != "1.0":
        return False
    for k, limit in [("device_id", 48), ("firmware_version", 48), ("boot_id", 48)]:
        v = p.get(k)
        if not isinstance(v, str) or not v or len(v) > limit or not SAFE.fullmatch(v):
            return False
    if not isinstance(p["sequence"], int) or p["sequence"] < 0:
        return False
    if not isinstance(p["uptime_ms"], int) or p["uptime_ms"] < 0:
        return False
    if p["source_mode"] not in SOURCE:
        return False
    chs = p["channels"]
    if not isinstance(chs, dict) or not (1 <= len(chs) <= 16):
        return False
    for name, ch in chs.items():
        if not isinstance(name, str) or len(name) > 32 or not SAFE.fullmatch(name):
            return False
        if not isinstance(ch, dict) or set(ch) != {"value", "quality"}:
            return False
        q = ch["quality"]
        v = ch["value"]
        if q not in QUALITY:
            return False
        if q == "valid":
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                return False
        elif q in {"invalid", "missing", "unknown"}:
            if v is not None:
                return False
        elif q == "stale":
            if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)):
                return False
    return True

def identity(p):
    return (p["device_id"], p["boot_id"], p["sequence"])

def normalize(p):
    return {
        "schema_version": p["schema_version"],
        "device_id": p["device_id"],
        "firmware_version": p["firmware_version"],
        "boot_id": p["boot_id"],
        "sequence": p["sequence"],
        "uptime_ms": p["uptime_ms"],
        "source_mode": p["source_mode"],
        "channels": {k: p["channels"][k] for k in sorted(p["channels"])},
    }

def classify(a, b):
    if not valid_payload(a) or not valid_payload(b):
        return "invalid"
    if identity(a) != identity(b):
        return "distinct"
    return "identical" if normalize(a) == normalize(b) else "conflicting"

gcc = shutil.which("gcc")
if not gcc:
    fail("gcc not found")

# Preserve Phase 7 regression first.
p = run([sys.executable, str(ROOT / "scripts" / "test_phase7_g2_formal_host.py")])
if p.returncode != 0:
    fail("Phase 7 G2 host regression failed", p.stdout)
if "PHASE7_G2_HOST_FORMAL_SCENARIOS: PASS (2/2)" not in p.stdout:
    fail("Phase 7 G2 host marker missing", p.stdout)

source = """
#include "phase8_h1_selftest.h"
int main(void)
{
    run_phase8_h1_telemetry_contract_selftest();
    return 0;
}
"""

with tempfile.TemporaryDirectory(prefix="vg_h1_") as td:
    td = pathlib.Path(td)
    c = td / "h1_runner.c"
    exe = td / ("h1_runner.exe" if os.name == "nt" else "h1_runner")
    c.write_text(source, encoding="utf-8")
    p = run([
        gcc, "-std=c11", "-Wall", "-Wextra", "-Werror",
        "-I", str(FW), str(c), "-lm", "-o", str(exe)
    ])
    if p.returncode != 0:
        fail("H1 compile failed", p.stdout)
    p = run([str(exe)])
    if p.returncode != 0:
        fail("H1 C selftest runner failed", p.stdout)
    if "PHASE8_H1_TELEMETRY_CONTRACT_SELFTEST: PASS (62/62)" not in p.stdout:
        fail("H1 C selftest PASS marker missing", p.stdout)
    if re.search(r"(^|\s)FAIL(?:\s|:|\()", p.stdout):
        fail("H1 C selftest printed FAIL", p.stdout)

checks = []
def check(name, ok):
    checks.append((name, bool(ok)))

schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
check("SCHEMA_DRAFT_2020_12", schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema")
check("SCHEMA_ID_VERSIONED", schema.get("$id") == "urn:vessel-gateway:telemetry:1.0")
check("SCHEMA_REQUIRED_FIELDS", set(schema.get("required", [])) == REQ)
check("SCHEMA_VERSION_CONST", schema["properties"]["schema_version"].get("const") == "1.0")
check("SCHEMA_SOURCE_ENUM", set(schema["properties"]["source_mode"].get("enum", [])) == SOURCE)
check("SCHEMA_QUALITY_ENUM", set(schema["properties"]["channels"]["additionalProperties"]["properties"]["quality"].get("enum", [])) == QUALITY)

loaded = {}
for fp in sorted(FIX.glob("*.json")):
    loaded[fp.name] = json.loads(fp.read_text(encoding="utf-8"))
    check("FIXTURE_VALID_" + fp.stem.upper().replace("-", "_"), valid_payload(loaded[fp.name]))

base = loaded["telemetry-v1-valid.json"]
ident = loaded["telemetry-v1-duplicate-identical.json"]
conflict = loaded["telemetry-v1-duplicate-conflict.json"]
distinct = loaded["telemetry-v1-distinct.json"]
physical = loaded["telemetry-v1-synthetic-physical-label.json"]

check("IDENTITY_TUPLE_BASE", identity(base) == ("demo-device-001", "boot-demo-0001", 42))
check("DUPLICATE_IDENTICAL", classify(base, ident) == "identical")
check("DUPLICATE_CONFLICTING", classify(base, conflict) == "conflicting")
check("DUPLICATE_DISTINCT", classify(base, distinct) == "distinct")
check("MISSING_REMAINS_NULL", base["channels"]["bilge_level"]["value"] is None)
check("INVALID_REMAINS_NULL", base["channels"]["vibration_index"]["value"] is None)
check("VALID_ZERO_REMAINS_ZERO", base["channels"]["zero_test"] == {"value": 0, "quality": "valid"})
check("PHYSICAL_LABEL_IS_SYNTHETIC_FIXTURE", physical["source_mode"] == "physical" and physical["device_id"].startswith("synthetic-"))

passed = sum(ok for _, ok in checks)
total = len(checks)
for name, ok in checks:
    print(f"H1_FIXTURE_TEST {name}: {'PASS' if ok else 'FAIL'}")

if passed != total:
    fail(f"fixture/contract checks failed ({passed}/{total})")

print(f"H1_HOST_C_COMPILER: {gcc}")
print("H1_PHASE7_REGRESSION: PASS")
print("PHASE8_H1_HOST_C_SELFTEST: PASS (62/62)")
print(f"PHASE8_H1_FIXTURE_CONTRACT_TEST: PASS ({passed}/{total})")
print("PHASE8_H1_HOST_GATE: PASS")
print(
    "NOTE: Development telemetry-contract evidence only. "
    "SUP-011, SUP-012, TEL-003 backend deduplication and formal SIM-014 remain NOT_RUN."
)
