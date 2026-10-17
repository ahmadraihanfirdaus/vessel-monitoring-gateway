#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/testing/phase9-p2-design.md"

def check(name, cond):
    print(f"PHASE9_P2_DESIGN {name}: {'PASS' if cond else 'FAIL'}")
    if not cond:
        raise SystemExit(5)

text = DOC.read_text(encoding="utf-8")
flat = re.sub(r"\s+", " ", text)

required = [
    'POST /api/v1/telemetry',
    '(device_id, boot_id, sequence)',
    'UNIQUE(device_id, boot_id, sequence)',
    'UNIQUE(telemetry_sample_id, name)',
    '`devices`',
    '`telemetry_samples`',
    '`telemetry_channels`',
    '`schema_version == "1.0"`',
    'at most 4096 bytes',
    '`simulation`',
    '`bench_test`',
    '`physical`',
    '`valid`',
    '`invalid`',
    '`missing`',
    '`stale`',
    '`unknown`',
    '`201`',
    '`200`',
    '`409`',
    '`413`',
    '`422`',
    '`401`',
    '`403`',
    'event persistence schema',
    'complete device-health schema',
    'database unique constraint',
    'Laravel migrations only',
    'System status remains `PARTIAL`',
    'external telemetry identity',
    'foreign key to `devices.device_id`',
    'CHAR(64)',
    'SHA-256',
    'cryptographically random high-entropy bearer token',
    'raw bearer token is never stored',
    'not a LOCKED requirement',
    'unsigned 64-bit JSON integer',
    'channel order does not affect semantic equality',
]
for token in required:
    check("TOKEN_" + token.replace("`","").replace(" ","_")[:48], token in flat)

check("NO_DB_EXECUTION_CLAIM",
      "does not connect to or write any database" in flat)
check("EVENT_SCHEMA_DEFERRED",
      "does not create an event table" in flat)
check("HEALTH_SCHEMA_DEFERRED",
      "full device-health table" in flat)
check("HTTPS_NOT_CLAIMED",
      "does not claim HTTPS deployment" in flat)
check("FORMAL_VERIFICATION_NOT_CLAIMED",
      "formally verified" in flat)

print("PHASE9_P2_DESIGN_TEST: PASS")
