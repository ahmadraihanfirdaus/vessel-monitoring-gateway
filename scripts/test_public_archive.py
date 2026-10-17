#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

PREFIX = "vessel-monitoring-gateway/"

FORBIDDEN_PATHS = [
    re.compile(r"(^|/)\.git(/|$)", re.I),
    re.compile(r"(^|/)\.pio(/|$)", re.I),
    re.compile(r"(^|/)\.vscode(/|$)", re.I),
    re.compile(r"(^|/)__pycache__(/|$)", re.I),
    re.compile(r"(^|/)node_modules(/|$)", re.I),
    re.compile(r"(^|/)vendor(/|$)", re.I),
    re.compile(r"(^|/)\.env($|\.)", re.I),
    re.compile(r"(^|/)sdkconfig(\.|$)", re.I),
    re.compile(r"\.py[co]$", re.I),
]

SECRET_PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
]


def machine_local_user_path_hits(data: bytes) -> list[bytes]:
    """Return concrete machine-local user-profile path matches.

    The path prefixes are assembled at runtime so this scanner does not match
    its own source text. The username component intentionally requires a
    concrete Windows-style account token, so documentation placeholders such
    as <user> are not treated as leaks.
    """

    username = rb"([A-Za-z0-9._-]{1,64})"
    backslash_users = re.escape(b"\\" + b"Users" + b"\\")
    slash_users = re.escape(b"/" + b"Users" + b"/")
    msys_users = re.escape(b"/" + b"c" + b"/" + b"Users" + b"/")

    patterns = [
        re.compile(rb"[A-Za-z]:" + backslash_users + username, re.I),
        re.compile(rb"[A-Za-z]:" + slash_users + username, re.I),
        re.compile(msys_users + username, re.I),
    ]

    hits: list[bytes] = []
    for pattern in patterns:
        hits.extend(match.group(0) for match in pattern.finditer(data))
    return hits


def tracked_files() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "-z"])
    return sorted(x.decode("utf-8") for x in raw.split(b"\0") if x)


def check_archive(path: Path) -> None:
    tracked = tracked_files()

    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        outside = [i.filename for i in infos if not i.filename.startswith(PREFIX)]
        if outside:
            raise AssertionError(f"entries outside prefix: {outside[:5]}")

        files = sorted(
            i.filename[len(PREFIX):]
            for i in infos
            if not i.is_dir() and i.filename.startswith(PREFIX)
        )

        if files != tracked:
            only_archive = sorted(set(files) - set(tracked))
            only_git = sorted(set(tracked) - set(files))
            raise AssertionError(
                f"archive does not match tracked files; "
                f"only_archive={only_archive[:5]}, only_git={only_git[:5]}"
            )

        forbidden = []
        machine_hits = []
        secret_hits = []

        for info in infos:
            if info.is_dir():
                continue

            name = info.filename[len(PREFIX):]

            if any(pattern.search(name) for pattern in FORBIDDEN_PATHS):
                forbidden.append(name)

            if info.file_size > 8_000_000:
                continue

            data = zf.read(info)
            if b"\x00" in data[:4096]:
                continue

            if machine_local_user_path_hits(data):
                machine_hits.append(name)

            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                secret_hits.append(name)

    assert not forbidden, f"forbidden archive entries: {forbidden[:10]}"
    assert not machine_hits, f"machine-local path leak: {machine_hits[:10]}"
    assert not secret_hits, f"high-confidence secret hit: {secret_hits[:10]}"

    print(f"PUBLIC_ARCHIVE_TEST tracked_files={len(tracked)}: PASS")
    print("PUBLIC_ARCHIVE_TEST exact_tracked_set: PASS")
    print("PUBLIC_ARCHIVE_TEST forbidden_entries=0: PASS")
    print("PUBLIC_ARCHIVE_TEST machine_local_user_paths=0: PASS")
    print("PUBLIC_ARCHIVE_TEST high_confidence_secret_hits=0: PASS")
    print("PUBLIC_ARCHIVE_TEST git_metadata=ABSENT: PASS")
    print("PUBLIC_ARCHIVE_TEST: PASS")


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "usage: python scripts/test_public_archive.py path/to/archive.zip",
            file=sys.stderr,
        )
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"archive not found: {path}", file=sys.stderr)
        return 2

    try:
        check_archive(path)
    except (AssertionError, zipfile.BadZipFile) as exc:
        print(f"PUBLIC_ARCHIVE_TEST: FAIL - {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
