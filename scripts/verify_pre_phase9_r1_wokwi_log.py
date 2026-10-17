#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys

from wokwi_log_boot import WokwiLogError, has_elf_sha, markers_in_order, select_latest_complete_boot

EXPECTED_APP_VERSION = "947b9d3-dirty"

def die(msg):
    print(f"PRE_PHASE9_R1_WOKWI_LOG_CHECK: FAIL - {msg}")
    raise SystemExit(1)

if len(sys.argv) != 2:
    die("usage: verify_pre_phase9_r1_wokwi_log.py <full-uart.txt>")

p = pathlib.Path(sys.argv[1])
if not p.is_file():
    die(f"log not found: {p}")

raw = p.read_text(encoding="utf-8", errors="replace")
try:
    text = select_latest_complete_boot(raw, expected_app_version=EXPECTED_APP_VERSION)
except WokwiLogError as exc:
    die(str(exc))

required = [
    "Project name:     vessel_gateway_firmware",
    f"App version:      {EXPECTED_APP_VERSION}",
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
ok, missing = markers_in_order(text, required)
parser_total = len(required) + 1
parser_pass = len(required) - len(missing) + has_elf_sha(text)

print(
    f"PRE_PHASE9_R1_WOKWI_PARSER_SELFTEST: "
    f"{'PASS' if parser_pass == parser_total else 'FAIL'} "
    f"({parser_pass}/{parser_total})"
)
if not ok or not has_elf_sha(text):
    for marker in missing:
        print(f"PRE_PHASE9_R1_WOKWI_MISSING_OR_REORDERED: {marker}")
    die("required markers missing or reordered")

before = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_BEFORE:\s*(\d+)", text)
after = re.search(r"C4_MAIN_STACK_WATERMARK_RAW_AFTER:\s*(\d+)", text)
if not before or not after:
    die("stack watermark markers missing")
if before.group(1) != after.group(1):
    die("stack watermark changed")

if re.search(r"\b(FATAL|Guru Meditation|assert failed|panic'ed)\b", text, re.I):
    die("fatal marker found")
if re.search(r"(?:^|\n).*(?:SELFTEST|SCENARIO|TEST).*:\s*FAIL(?:\s|$)", text):
    die("target self-test FAIL marker found")

print("PRE_PHASE9_R1_WOKWI_REGRESSION_CHAIN: PASS")
print("PRE_PHASE9_R1_WOKWI_G1_NAVIGATION: PASS (64/64)")
print("PRE_PHASE9_R1_WOKWI_H1_TELEMETRY: PASS (62/62)")
print("PRE_PHASE9_R1_WOKWI_TIMED_DEMO: PASS (6/6)")
print(f"PRE_PHASE9_R1_WOKWI_STACK_WATERMARK_RAW_BEFORE: {before.group(1)}")
print(f"PRE_PHASE9_R1_WOKWI_STACK_WATERMARK_RAW_AFTER: {after.group(1)}")
print("PRE_PHASE9_R1_WOKWI_LOG_CHECK: PASS")
print(
    "NOTE: Repair/regression target evidence only. It does not change formal "
    "SIM/SUP status, physical verification, TEL-003 backend status, or "
    "production readiness."
)
