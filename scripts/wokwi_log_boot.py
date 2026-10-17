#!/usr/bin/env python3
from __future__ import annotations

import re

PROJECT_MARKER = "Project name:     vessel_gateway_firmware"
RETURN_MARKER = "main_task: Returned from app_main()"
APP_VERSION_RE = re.compile(r"App version:\s+([^\r\n]+)")
ELF_RE = re.compile(r"ELF file SHA256:\s+[0-9a-f]{9,}", re.I)
POST_RETURN_BOOT_RE = re.compile(
    r"(?:\bRebooting\.\.\.|(?:^|\n)\s*rst:|Project name:\s+|App version:\s+)",
    re.I,
)


class WokwiLogError(ValueError):
    pass


def normalize_uart(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def select_latest_complete_boot(
    text: str,
    *,
    expected_app_version: str,
) -> str:
    """Return only the latest boot segment and reject incomplete trailing boots."""
    text = normalize_uart(text)

    app_matches = list(APP_VERSION_RE.finditer(text))
    if not app_matches:
        raise WokwiLogError("app version marker missing")

    latest_app = app_matches[-1]
    actual_version = latest_app.group(1).strip()
    if actual_version != expected_app_version:
        raise WokwiLogError(
            f"latest app version mismatch: expected {expected_app_version}, "
            f"got {actual_version}"
        )

    project_pos = text.rfind(PROJECT_MARKER, 0, latest_app.start())
    if project_pos < 0:
        raise WokwiLogError("project marker missing before latest app version")

    # If the nearest project header belongs to an already completed earlier
    # boot, an appended partial boot must not inherit its markers.
    between = text[project_pos:latest_app.start()]
    if RETURN_MARKER in between:
        raise WokwiLogError("latest app marker is not in the same boot header")

    segment = text[project_pos:]

    segment_apps = list(APP_VERSION_RE.finditer(segment))
    if len(segment_apps) != 1:
        raise WokwiLogError("latest boot segment contains multiple app versions")

    return_pos = segment.find(RETURN_MARKER)
    if return_pos < 0:
        raise WokwiLogError("latest boot did not return from app_main")

    terminal_end = return_pos + len(RETURN_MARKER)
    tail = segment[terminal_end:]
    if POST_RETURN_BOOT_RE.search(tail):
        raise WokwiLogError("boot/reset activity found after terminal return")

    # Ignore harmless trailing whitespace only. The selected segment therefore
    # cannot borrow PASS markers from an earlier boot.
    return segment[:terminal_end]


def markers_in_order(text: str, markers: list[str]) -> tuple[bool, list[str]]:
    pos = 0
    missing_or_reordered: list[str] = []
    for marker in markers:
        idx = text.find(marker, pos)
        if idx < 0:
            missing_or_reordered.append(marker)
            continue
        pos = idx + len(marker)
    return not missing_or_reordered, missing_or_reordered


def has_elf_sha(text: str) -> bool:
    return bool(ELF_RE.search(text))
