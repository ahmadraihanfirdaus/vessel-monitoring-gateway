#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys

def die(msg):
    print(f"H1_WOKWI_LOG_CHECK: FAIL - {msg}")
    raise SystemExit(1)

if len(sys.argv) != 2:
    die("usage: verify_phase8_h1_wokwi_log.py <full-uart.txt>")

p = pathlib.Path(sys.argv[1])
if not p.is_file():
    die(f"log not found: {p}")

text = p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

required = [
    "Project name:     vessel_gateway_firmware",
    "App version:      f78e172-dirty",
    "PHASE4_D1_DOOR_PROVIDER_SELFTEST: PASS (38/38)",
    "PHASE4_D2_FUEL_VAPOR_PROVIDER_SELFTEST: PASS (53/53)",
    "PHASE4_D3_BILGE_PROVIDER_SELFTEST: PASS (47/47)",
    "PHASE4_D4_TEMPERATURE_PROVIDER_SELFTEST: PASS (67/67)",
    "PHASE4_D5_ATTITUDE_PROVIDER_SELFTEST: PASS (54/54)",
    "PHASE4_D6_VIBRATION_PROVIDER_SELFTEST: PASS (61/61)",
    "PHASE4_D7_POWER_PROVIDER_SELFTEST: PASS (61/61)",
    "PHASE5_E1_SAFETY_POLICY_SELFTEST: PASS (51/51)",
    "PHASE5_E2_FUEL_SAFETY_SELFTEST: PASS (60/60)",
    "PHASE5_E3_MONITOR_SAFETY_SELFTEST: PASS (85/85)",
    "PHASE5_E4_FORMAL_SCENARIOS: PASS (6/6)",
    "PHASE6_F1_ENGINE_MODEL_SELFTEST: PASS (62/62)",
    "PHASE6_F2_FORMAL_SCENARIOS: PASS (1/1)",
    "PHASE7_G1_NAVIGATION_SELFTEST: PASS (64/64)",
    "PHASE7_G2_FORMAL_SCENARIOS: PASS (2/2)",
    "PHASE8_H1_TELEMETRY_CONTRACT_SELFTEST: PASS (62/62)",
    "CORE_RUNTIME_TIMED_DEMO: PASS (6/6)",
    "main_task: Returned from app_main()",
]

parser_total = len(required) + 1
parser_pass = sum(marker in text for marker in required)
parser_pass += bool(re.search(r"ELF file SHA256:\s+[0-9a-f]{9,}", text))

print(
    f"H1_WOKWI_LOG_PARSER_SELFTEST: "
    f"{'PASS' if parser_pass == parser_total else 'FAIL'} "
    f"({parser_pass}/{parser_total})"
)

if parser_pass != parser_total:
    for marker in required:
        if marker not in text:
            print(f"H1_WOKWI_MISSING: {marker}")
    die("required markers missing")

before = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_BEFORE:\s*(\d+)", text)
after = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_AFTER:\s*(\d+)", text)
if not before or not after:
    die("stack watermark marker missing")
if before.group(1) != after.group(1):
    die("stack watermark changed")

if "PHASE8_H1_TELEMETRY_CONTRACT_SELFTEST: FAIL" in text:
    die("H1 telemetry selftest failed")
if re.search(r"\b(FATAL|Guru Meditation|assert failed|panic'ed)\b", text, re.I):
    die("fatal marker found")

print("H1_WOKWI_PHASE7_REGRESSION: PASS")
print("H1_WOKWI_TELEMETRY_CONTRACT_SELFTEST: PASS (62/62)")
print("H1_WOKWI_TIMED_DEMO: PASS (6/6)")
print(f"H1_WOKWI_STACK_WATERMARK_RAW_BEFORE: {before.group(1)}")
print(f"H1_WOKWI_STACK_WATERMARK_RAW_AFTER: {after.group(1)}")
print("H1_WOKWI_LOG_CHECK: PASS")
print(
    "NOTE: Target-side development contract evidence only. "
    "SUP-011/SUP-012, TEL-003 backend deduplication, SIM-014, "
    "network transport and production readiness are not implied."
)
