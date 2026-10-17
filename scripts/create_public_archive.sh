#!/usr/bin/env bash
set -euo pipefail

fail(){ echo "PUBLIC_ARCHIVE: BLOCKED - $*" >&2; exit 4; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || fail "run from repository"
cd "$ROOT"

[[ -n "$(git branch --show-current)" ]] || fail "detached HEAD is not allowed"
git diff --quiet || fail "tracked worktree must be clean"
git diff --cached --quiet || fail "index must be clean"

unexpected="$(
  git ls-files --others --exclude-standard \
  | grep -v -E '^firmware/(\.gitignore|\.vscode/.*)$' || true
)"
[[ -z "$unexpected" ]] || {
  echo "$unexpected" >&2
  fail "unexpected untracked files"
}

OUT="${1:-}"
if [[ -z "$OUT" ]]; then
  fail "usage: bash scripts/create_public_archive.sh /absolute/or/relative/output.zip"
fi

case "$OUT" in
  *.zip) ;;
  *) fail "output path must end in .zip" ;;
esac

OUT_DIR="$(dirname "$OUT")"
mkdir -p "$OUT_DIR"

PREFIX="vessel-monitoring-gateway/"
TMP="${OUT}.tmp"
rm -f "$TMP"

git archive --format=zip --prefix="$PREFIX" HEAD > "$TMP"
[[ -s "$TMP" ]] || fail "git archive produced an empty file"

python scripts/test_public_archive.py "$TMP"

mv -f "$TMP" "$OUT"

echo "PUBLIC_ARCHIVE: CREATED"
echo "source_commit=$(git rev-parse HEAD)"
echo "tracked_files=$(git ls-files | wc -l | tr -d '[:space:]')"
echo "archive_bytes=$(wc -c < "$OUT" | tr -d '[:space:]')"
echo "archive_sha256=$(sha256sum "$OUT" | awk '{print $1}')"
echo "output=$OUT"
echo "NOTE: This archive contains tracked Git content only; it is not deployment or production approval."
