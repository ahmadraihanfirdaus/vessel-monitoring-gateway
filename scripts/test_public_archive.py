#!/usr/bin/env python3
from __future__ import annotations

import re
import hashlib
import os
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

PREFIX = "vessel-monitoring-gateway/"
MAX_FILES = 8192
MAX_FILE_BYTES = 8_000_000
MAX_TOTAL_BYTES = 128_000_000

# Exact historical blobs contain machine-profile paths. Preserve local evidence;
# omit only these immutable versions from a PUBLIC filtered snapshot. Changed
# versions are not exempt from scanning. No pattern/secret detector is waived.
PRIVATE_SNAPSHOT_BLOBS = {
    "docs/handoff/CHATGPT_CONTEXT.md": "b4d215c23ef6a53c890bb02ae9eae61fcffdf732",
    "docs/handoff/CODEX_RESUME.md": "2f098a6f882cb3386b6814778cc15d06444780dd",
    "evidence/test-results/alarm-metadata-early-regression-20261025.txt": "6bd1d20c98c0a6df1948e89c4400bf46a31569c0",
    "evidence/test-results/alarm-metadata-final-regression-20261025.txt": "4816c9f25034191768433712ae5b6b407d117b2a",
    "evidence/test-results/continuous-final-security-20261025.txt": "8c5a6b1f1e73845b1bc56149337f2c7e227cd77a",
    "evidence/test-results/device-read-scoped-gates-run1-20261025.txt": "8a269746096a0c7435123a35f72e795163f28a93",
    "evidence/test-results/phase9-p3-runtime-http-client-failed-attempt2-20261018.txt": "e08ea2fb9897a574f972c7d29dcab75e2596a910"
}

FORBIDDEN_PATHS = [
    re.compile(r"(^|/)\.git(/|$)", re.I),
    re.compile(r"(^|/)\.pio(/|$)", re.I),
    re.compile(r"(^|/)\.vscode(/|$)", re.I),
    re.compile(r"(^|/)__pycache__(/|$)", re.I),
    re.compile(r"(^|/)node_modules(/|$)", re.I),
    re.compile(r"(^|/)vendor(/|$)", re.I),
    re.compile(r"(^|/)\.env($|\.)", re.I),
    re.compile(r"(^|/)sdkconfig(?:$|\.(?!defaults$))", re.I),
    re.compile(r"\.py[co]$", re.I),
    re.compile(r"(^|/)(?:\.aws|\.codex|\.agents|\.cache)(/|$)", re.I),
    re.compile(r"(^|/)(?:credentials(?:\.json)?|secrets\.json|tokens\.json|id_rsa|id_ed25519|\.npmrc|\.pypirc|\.netrc|\.git-credentials)$", re.I),
    re.compile(r"\.(?:key|pem|p12|pfx|sqlite|sqlite3|db)$", re.I),
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


def git(repo: Path, *args: str, input_data: bytes | None = None) -> bytes:
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1")
    try:
        result = subprocess.run(["git", *args], cwd=repo, env=env, input=input_data,
                                capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise ValueError('Git snapshot operation exceeded its bound') from None
    if result.returncode:
        raise ValueError("Git snapshot metadata/content unavailable")
    return result.stdout


def forbidden_path(name: str) -> bool:
    return any(pattern.search(name) for pattern in FORBIDDEN_PATHS)


def canonical_path(name: str) -> bool:
    if len(name) > 512 or not re.fullmatch(r"[A-Za-z0-9_./-]+", name):
        return False
    parts = name.split('/')
    reserved = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", re.I)
    return all(len(p) <= 255 and p not in ('', '.', '..') and not p.endswith('.') and not reserved.match(p)
               for p in parts)


def archive_plan(repo: Path, commit: str = 'HEAD') -> dict:
    """Inspect committed metadata first; never open/hash excluded dotenv files."""
    head = git(repo, 'rev-parse', '--verify', commit+'^{commit}').decode().strip()
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', head):
        raise ValueError('Invalid source commit')
    files, excluded, excluded_details, seen = [], [], [], set()
    for entry in git(repo, 'ls-tree', '-rz', '--full-tree', head).split(b'\0'):
        if not entry:
            continue
        metadata, separator, raw_name = entry.partition(b'\t')
        fields = metadata.decode('ascii').split()
        name = raw_name.decode('utf-8', errors='strict')
        if not separator or len(fields) != 3 or not canonical_path(name):
            raise ValueError('Noncanonical snapshot path')
        if forbidden_path(name):
            excluded.append(name)
            excluded_details.append(dict(path=name, reason='SENSITIVE_OR_CACHE_NAME_METADATA_ONLY'))
            continue
        mode, kind, oid = fields
        if PRIVATE_SNAPSHOT_BLOBS.get(name) == oid:
            excluded.append(name)
            excluded_details.append(dict(path=name, oid=oid, reason='EXACT_HISTORICAL_PRIVATE_PROFILE_BLOB'))
            continue
        if mode not in ('100644', '100755') or kind != 'blob' or name.casefold() in seen:
            raise ValueError('Linked, special or colliding snapshot entry')
        seen.add(name.casefold())
        files.append(dict(path=name, mode=mode, oid=oid))
    if not files or len(files) > MAX_FILES:
        raise ValueError('Snapshot file count refused')
    # Query sizes of admitted blobs ONLY. No excluded blob is requested.
    sizes = git(repo, 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)',
                input_data=''.join(x['oid']+'\n' for x in files).encode()).decode().splitlines()
    if len(sizes) != len(files):
        raise ValueError('Incomplete snapshot size inventory')
    for item, line in zip(files, sizes):
        oid, kind, size = line.split()
        if oid != item['oid'] or kind != 'blob' or not size.isdecimal():
            raise ValueError('Invalid snapshot size inventory')
        item['bytes'] = int(size)
        if item['bytes'] > MAX_FILE_BYTES:
            raise ValueError('Snapshot file exceeds inspection bound')
    if sum(x['bytes'] for x in files) > MAX_TOTAL_BYTES:
        raise ValueError('Snapshot exceeds total inspection bound')
    return dict(head=head, files=files, excluded=sorted(excluded), excluded_details=excluded_details)


def inspect_content(data: bytes) -> None:
    # Binary/NUL data and large entries are never silently skipped.
    if len(data) > MAX_FILE_BYTES:
        raise ValueError('Archive content exceeds inspection bound')
    if machine_local_user_path_hits(data):
        raise ValueError('Machine-local path detected; content withheld')
    if any(pattern.search(data) for pattern in SECRET_PATTERNS):
        raise ValueError('High-confidence secret marker detected; content withheld')


def check_archive(path: Path, repo: Path = Path('.'), commit: str = 'HEAD') -> dict:
    plan = archive_plan(repo, commit)
    expected = {x['path']: x for x in plan['files']}
    with zipfile.ZipFile(path) as zf:
        if zf.comment:
            raise ValueError('Archive comment is not part of the source snapshot')
        infos = zf.infolist()
        if len(infos) > MAX_FILES * 4:
            raise ValueError('Archive entry count exceeds bound')
        files, seen = {}, set()
        for info in infos:
            if info.comment or info.extra or info.orig_filename != info.filename:
                raise ValueError('Non-source or ambiguous archive metadata')
            if not info.filename.startswith(PREFIX):
                raise ValueError('Archive entry outside fixed prefix')
            name = info.filename[len(PREFIX):].rstrip('/') if info.is_dir() else info.filename[len(PREFIX):]
            if info.is_dir() and (info.file_size != 0 or
                    (name and info.filename != PREFIX+name+'/')):
                raise ValueError('Directory payload or noncanonical directory refused')
            mode = stat.S_IFMT(info.external_attr >> 16)
            if (mode not in (0, stat.S_IFDIR if info.is_dir() else stat.S_IFREG)
                    or (info.external_attr >> 16) & 0o7000 or info.flag_bits & 1):
                raise ValueError('Linked, special or encrypted archive entry')
            if info.filename.casefold() in seen:
                raise ValueError('Duplicate archive entry')
            seen.add(info.filename.casefold())
            if not name and info.is_dir() and info.filename == PREFIX:
                continue
            if not canonical_path(name) or forbidden_path(name):
                raise ValueError('Forbidden, duplicate or noncanonical archive path')
            if info.is_dir():
                if not any(p.startswith(name+'/') for p in expected):
                    raise ValueError('Unexpected archive directory')
                continue
            if name in files or name not in expected or info.file_size != expected[name]['bytes']:
                raise ValueError('Archive set/size differs from admitted commit')
            files[name] = info
        if set(files) != set(expected):
            raise ValueError('Archive set differs from admitted commit')
        # Reject forbidden metadata for the ENTIRE ZIP before reading any body.
        for name, info in files.items():
            with zf.open(info) as handle:
                data = handle.read(MAX_FILE_BYTES + 1)
            if len(data) != info.file_size:
                raise ValueError('Archive content length mismatch')
            inspect_content(data)
            algorithm = hashlib.sha1 if len(expected[name]['oid']) == 40 else hashlib.sha256
            oid = algorithm(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if oid != expected[name]['oid']:
                raise ValueError('Archive content differs from committed blob')
    print(f"PUBLIC_ARCHIVE_TEST admitted_files={len(expected)}: PASS")
    print("PUBLIC_ARCHIVE_TEST exact_filtered_commit_set_and_blobs: PASS")
    print("PUBLIC_ARCHIVE_TEST forbidden_entries=0: PASS")
    print("PUBLIC_ARCHIVE_TEST machine_local_user_paths=0: PASS")
    print("PUBLIC_ARCHIVE_TEST high_confidence_secret_hits=0: PASS")
    print("PUBLIC_ARCHIVE_TEST git_metadata=ABSENT: PASS")
    print("PUBLIC_ARCHIVE_TEST: PASS")
    return plan


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
    except (AssertionError, ValueError, OSError, UnicodeError, zipfile.BadZipFile, RuntimeError):
        print("PUBLIC_ARCHIVE_TEST: FAIL - archive/source admission refused; content withheld", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
