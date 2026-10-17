#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys

from wokwi_log_boot import WokwiLogError, has_elf_sha, markers_in_order, select_latest_complete_boot

def die(msg):
    print(f"G2_WOKWI_LOG_CHECK: FAIL - {msg}")
    raise SystemExit(1)

if len(sys.argv) != 2:
    die("usage: verify_phase7_g2_wokwi_log.py <full-uart.txt>")

p = pathlib.Path(sys.argv[1])
if not p.is_file():
    die(f"log not found: {p}")

raw = p.read_text(encoding="utf-8", errors="replace")
try:
    text = select_latest_complete_boot(raw, expected_app_version="a7ffc9d-dirty")
except WokwiLogError as exc:
    die(str(exc))

required = [
    "Project name:     vessel_gateway_firmware",
    "App version:      a7ffc9d-dirty",
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
    "G2_FORMAL_SCENARIO SIM-008: PASS",
    "G2_FORMAL_SCENARIO SIM-009: PASS",
    "PHASE7_G2_FORMAL_SCENARIOS: PASS (2/2)",
    "CORE_RUNTIME_TIMED_DEMO: PASS (6/6)",
    "main_task: Returned from app_main()",
]
ok, missing = markers_in_order(text, required)
parser_total = len(required) + 1
parser_pass = len(required) - len(missing) + has_elf_sha(text)

print(f"G2_WOKWI_LOG_PARSER_SELFTEST: {'PASS' if parser_pass == parser_total else 'FAIL'} ({parser_pass}/{parser_total})")
if not ok or not has_elf_sha(text):
    for marker in missing:
        print(f"G2_WOKWI_MISSING_OR_REORDERED: {marker}")
    die("required markers missing or reordered")

before = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_BEFORE:\s*(\d+)", text)
after = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_AFTER:\s*(\d+)", text)
if not before or not after:
    die("stack watermark markers missing")
if before.group(1) != after.group(1):
    die("stack watermark changed during timed demo")

if "G2_FORMAL_SCENARIO SIM-008: FAIL" in text:
    die("SIM-008 formal scenario failed")
if "G2_FORMAL_SCENARIO SIM-009: FAIL" in text:
    die("SIM-009 formal scenario failed")
if re.search(r"\b(FATAL|Guru Meditation|assert failed|panic'ed)\b", text, re.I):
    die("fatal marker found")

print("G2_WOKWI_G1_REGRESSION: PASS")
print("G2_WOKWI_FORMAL_SIM008: PASS (1/1)")
print("G2_WOKWI_FORMAL_SIM009: PASS (1/1)")
print("G2_WOKWI_FORMAL_PHASE7_SCENARIOS: PASS (2/2)")
print("G2_WOKWI_TIMED_DEMO: PASS (6/6)")
print(f"G2_WOKWI_STACK_WATERMARK_RAW_BEFORE: {before.group(1)}")
print(f"G2_WOKWI_STACK_WATERMARK_RAW_AFTER: {after.group(1)}")
print("G2_WOKWI_LOG_CHECK: PASS")
print(
    "NOTE: Formal software-simulation evidence for SIM-008/SIM-009 only. "
    "SUP-007 and physical GNSS/NMEA bench verification remain NOT_RUN."
)
