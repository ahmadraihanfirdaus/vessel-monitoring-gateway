"""Plan a filtered committed snapshot; --execute writes a NEW local ZIP only.

No workspace backup, publication, deployment, dotenv read, deletion or overwrite.
"""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import sys
import zipfile

sys.dont_write_bytecode = True  # Process-only: never create source-tree import caches.

from test_public_archive import archive_plan, check_archive, forbidden_path, git, inspect_content

PROTECTED_UNTRACKED = {'AGENTS.md', 'firmware/.gitignore', 'firmware/.vscode/extensions.json'}


def clean_snapshot(repo: Path) -> None:
    if not git(repo, 'branch', '--show-current').strip():
        raise ValueError('Detached HEAD refused')
    # Return codes are meaningful; git() rejects any tracked/index difference.
    git(repo, 'diff', '--quiet')
    git(repo, 'diff', '--cached', '--quiet')
    others = set(git(repo, 'ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')) - {''}
    if others - PROTECTED_UNTRACKED:
        raise ValueError('Unexpected untracked files; preserve WIP and finish review first')


def output_target(path: Path) -> Path:
    target = path.absolute()
    if target.suffix.lower() != '.zip' or not target.parent.is_dir():
        raise ValueError('Output must be a new ZIP in an existing directory')
    for part in (target, *target.parents):
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('Linked output path refused')
    if target.exists() or any(forbidden_path(p) for p in target.parts):
        raise ValueError('Existing or protected output target refused')
    return target


def create_archive(repo: Path, path: Path) -> dict:
    plan = archive_plan(repo)
    clean_snapshot(repo)
    target = output_target(path)
    if target.is_relative_to(repo.resolve()):
        raise ValueError('Keep archive output outside the source repository')
    if git(repo, 'rev-parse', 'HEAD').decode().strip() != plan['head']:
        raise ValueError('Source commit changed')
    # Exclusive open is the final race guard: never truncate/rename/remove a
    # pre-existing output or temporary file. An interrupted own output stays.
    with target.open('xb') as output, zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for item in plan['files']:
            data = git(repo, 'cat-file', 'blob', item['oid'])
            if len(data) != item['bytes']:
                raise ValueError('Committed blob length changed')
            inspect_content(data)
            info = zipfile.ZipInfo('vessel-monitoring-gateway/'+item['path'], (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | int(item['mode'], 8)) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    check_archive(target, repo, plan['head'])
    clean_snapshot(repo)
    if git(repo, 'rev-parse', 'HEAD').decode().strip() != plan['head']:
        raise ValueError('Source commit changed during archive creation')
    return dict(head=plan['head'], files=len(plan['files']), excluded=len(plan['excluded']),
                exclusions=json.dumps(plan['excluded_details'], separators=(',', ':')),
                bytes=target.stat().st_size, sha256=hashlib.sha256(target.read_bytes()).hexdigest())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    try:
        repo = Path(git(Path.cwd(), 'rev-parse', '--show-toplevel').decode().strip())
        if not args.execute:
            plan = archive_plan(repo)
            print('PUBLIC_ARCHIVE: PLAN_ONLY_NO_BLOB_CONTENT_READ_NO_OUTPUT')
            print('source_commit='+plan['head'])
            print('admitted_files='+str(len(plan['files'])))
            print('excluded_sensitive_or_cache_paths='+str(len(plan['excluded'])))
            print('exclusions='+json.dumps(plan['excluded_details'], separators=(',', ':')))
            print('NOTE: HEAD only; WIP is excluded. Execute requires clean tracked/index and reviewed untracked state.')
            return 0
        result = create_archive(repo, args.output)
        print('PUBLIC_ARCHIVE: CREATED_FILTERED_COMMITTED_SNAPSHOT')
        for key, value in result.items():
            print(f'{key}={value}')
        print('NOTE: No publication/deployment approval. Interrupted own output is retained; no overwrite or deletion.')
        return 0
    except (OSError, ValueError, UnicodeError, RuntimeError, zipfile.BadZipFile):
        # Never echo file bodies, Git diagnostics, user paths or secret values.
        print('PUBLIC_ARCHIVE: BLOCKED; inspect source state/dependencies and use a fresh output path. Any partial own output is retained.', file=sys.stderr)
        return 4


if __name__ == '__main__':
    raise SystemExit(main())
