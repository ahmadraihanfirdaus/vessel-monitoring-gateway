#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "backend" / "laravel"

def check(name: str, ok: bool) -> None:
    print(f"PHASE9_P1_FOUNDATION {name}: {'PASS' if ok else 'FAIL'}")
    if not ok:
        raise SystemExit(5)

check("ROOT_PRESENT", APP.is_dir())

required = [
    "artisan",
    "composer.json",
    "composer.lock",
    "app",
    "bootstrap",
    "config",
    "public/index.php",
    "routes/web.php",
    "storage",
    "tests",
]
for rel in required:
    check(f"REQUIRED_{rel.replace('/', '_').upper()}", (APP / rel).exists())

forbidden = [
    APP / ".env",
    APP / "vendor",
    APP / "database" / "database.sqlite",
]
for path in forbidden:
    check(f"FORBIDDEN_{path.name.upper()}_ABSENT", not path.exists())

migration_files = []
mig_dir = APP / "database" / "migrations"
if mig_dir.exists():
    migration_files = [p for p in mig_dir.rglob("*") if p.is_file()]
check("APPLICATION_MIGRATIONS_ABSENT", not migration_files)

composer = json.loads((APP / "composer.json").read_text(encoding="utf-8"))
requires = composer.get("require", {})
framework = str(requires.get("laravel/framework", ""))
check("LARAVEL_FRAMEWORK_REQUIRED", bool(framework))
check("LARAVEL_12_CONSTRAINT", bool(re.search(r"(^|[^0-9])12(?:\.|[^0-9]|$)", framework)))

lock = json.loads((APP / "composer.lock").read_text(encoding="utf-8"))
packages = {p.get("name"): p for p in lock.get("packages", [])}
check("LOCK_CONTAINS_LARAVEL_FRAMEWORK", "laravel/framework" in packages)
framework_version = packages.get("laravel/framework", {}).get("version", "UNKNOWN")
print(f"PHASE9_P1_FOUNDATION LARAVEL_FRAMEWORK_LOCKED_VERSION: {framework_version}")

tracked_risk = []
for path in APP.rglob("*"):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    low = rel.lower()
    if "/vendor/" in f"/{low}/":
        tracked_risk.append(rel)
    if low.endswith("/.env") or low == ".env":
        tracked_risk.append(rel)
check("NO_VENDOR_OR_ENV_FILES", not tracked_risk)

print("PHASE9_P1_FOUNDATION DATABASE_CONNECTION: NOT_ATTEMPTED")
print("PHASE9_P1_FOUNDATION DATABASE_WRITE: NOT_ATTEMPTED")
print("PHASE9_P1_FOUNDATION TEST: PASS")
