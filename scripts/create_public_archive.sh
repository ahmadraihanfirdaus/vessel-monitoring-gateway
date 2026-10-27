#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo 'PUBLIC_ARCHIVE: BLOCKED - run from repository' >&2
  exit 4
}
# One cross-platform policy implementation; no rm, mv, overwrite or shell backup.
exec "${VG_PYTHON_CLI:-python}" -B "$ROOT/scripts/create_public_archive.py" "$@"
