"""Build a sanitized, parent-mapped candidate in a NEW ignored private directory.

Never clones/copies the source object database, touches source refs, or publishes.
Default is a read-only plan. Execute requires complete reviewed history and an
exclusive new destination; failures retain the owned partial candidate for review.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

import audit_public_history as history


def blob_oid(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def sanitize(path, data):
    hits = history.profile_hits(data)
    if not hits:
        return data
    if path == 'scripts/test_public_archive_scanner.py':
        # Preserve the negative oracle using synthetic runtime-joined prefixes.
        lines = data.decode('utf-8').splitlines(keepends=True)
        for i, line in enumerate(lines):
            if not history.profile_hits(line.encode()):
                continue
            statement = ast.parse(line.strip()).body[0]
            if not (isinstance(statement, ast.Assign) and len(statement.targets)==1
                    and isinstance(statement.targets[0], ast.Name) and statement.targets[0].id=='data'
                    and isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, bytes)):
                raise ValueError('Unknown historical scanner fixture; manual review required')
            value = statement.value.value
            if b'\\' in value:
                parts = [b'C:', b'Users', b'synthetic-fixture-user', b'Downloads', b'artifact.zip']
                separator = b'\\'
            else:
                parts = ([b'C:'] if value.startswith(b'C:') else [b'', b'c']) + [b'Users', b'synthetic-fixture-user', b'Downloads', b'artifact.zip']
                separator = b'/'
            indent = line[:len(line)-len(line.lstrip())]
            lines[i] = indent+'data = '+repr(separator)+'.join('+repr(parts)+')\n'
        result = ''.join(lines).encode()
        ast.parse(result)
    elif path.endswith(('.md', '.txt')):
        result = data
        for hit in hits:
            result = result.replace(hit, b'<LOCAL_HOME>')
    else:
        raise ValueError('Private path in unsupported content; manual review required')
    if history.profile_hits(result):
        raise ValueError('Sanitization incomplete')
    return result


def make_tree(destination, entries, cache):
    directories = {}
    for entry in entries:
        node = directories
        parts = entry['path'].split('/')
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        if parts[-1] in node:
            raise ValueError('Tree name collision')
        node[parts[-1]] = entry

    def write(node):
        rows = []
        for name, item in node.items():
            if 'oid' in item and 'path' in item:
                rows.append((name, item['mode'], 'blob', item['oid']))
            else:
                rows.append((name, '040000', 'tree', write(item)))
        key = tuple(sorted(rows))
        if key not in cache:
            raw = b''.join((mode+' '+kind+' '+oid+'\t'+name).encode()+b'\0'
                           for name, mode, kind, oid in key)
            cache[key] = history.git(destination, 'mktree', '-z', data=raw).decode().strip()
        return cache[key]
    return write(directories)


def build(source, revision, reviews, destination, execute=False):
    report = history.audit(source, revision, reviews)
    if report['commit_metadata_issues']:
        raise ValueError('Commit metadata requires unresolved privacy/security review')
    if any(x['reason'] != 'PROHIBITED_NAME_METADATA_ONLY_NOT_READ' for x in report['excluded_metadata_only']):
        raise ValueError('Uninspected/shared/special content prevents candidate construction')
    if any(i['reason'] != 'Machine-local profile path' for b in report['blobs'] for i in b['issues']):
        raise ValueError('Unresolved non-profile content findings')
    if not execute:
        return dict(mode='PLAN_ONLY', source_commit=report['source_commit'],
                    commits=report['commit_count'], private_blob_versions=report['flagged_blob_path_versions'],
                    excluded_paths=sorted({x['path'] for x in report['excluded_metadata_only']}),
                    publication_authorized=False)
    destination = destination.absolute()
    if (destination.parent.parent.resolve() != source.resolve() or destination.parent.name != 'private'
            or not re.fullmatch(r'portfolio-history-[A-Za-z0-9_-]+', destination.name)
            or destination.exists() or destination.is_symlink()):
        raise ValueError('Exclusive new source/private/portfolio-history-* destination required')
    for parent in destination.parents:
        if parent.is_symlink() or (hasattr(parent, 'is_junction') and parent.is_junction()):
            raise ValueError('Linked destination parent refused')
    # Only a new isolated bare repository is initialized. Original refs untouched.
    destination.mkdir(parents=True, exist_ok=False)
    history.git(destination, '-c', 'init.defaultBranch=portfolio', 'init', '--bare', '--quiet', '--template=')
    changed, mappings, payload = [], {}, bytearray()
    oids = sorted({b['oid'] for b in report['blobs']})
    batch = history.git(source, 'cat-file', '--batch', data=''.join(x+'\n' for x in oids).encode())
    originals, offset = {}, 0
    for expected in oids:
        end = batch.index(b'\n', offset)
        oid, kind, size = batch[offset:end].decode().split()
        if oid != expected or kind != 'blob':
            raise ValueError('Source batch identity mismatch')
        end_data = end+1+int(size)
        if batch[end_data:end_data+1] != b'\n':
            raise ValueError('Source batch framing mismatch')
        originals[oid] = batch[end+1:end_data]
        offset = end_data+1
    if offset != len(batch):
        raise ValueError('Source batch trailing data')
    for b in report['blobs']:
        data = originals[b['oid']]
        if hashlib.sha256(data).hexdigest() != b['sha256']:
            raise ValueError('Immutable source blob binding failed')
        new = sanitize(b['path'], data)
        issues, _, _ = history.content_review(b['path'], new)
        issues, _ = history.apply_reviews(b['path'], blob_oid(new), new, issues, reviews)
        if issues:
            raise ValueError('Candidate blob has unresolved findings')
        oid = blob_oid(new)
        mappings[(b['path'], b['oid'])] = oid
        if new != data:
            changed.append(dict(path=b['path'], original_blob=b['oid'], candidate_blob=oid,
                                action='SYNTHETIC_RUNTIME_JOINED_FIXTURE' if b['path'].endswith('.py') else 'PROFILE_PREFIX_REDACTION_ONLY'))
        payload.extend(b'blob\ndata '+str(len(new)).encode()+b'\n'+new+b'\n')
    payload.extend(b'done\n')
    history.git(destination, 'fast-import', '--quiet', '--done', data=bytes(payload))
    commit_map, tree_cache = {}, {}
    omissions = {(x['commit'], x['path']) for x in report['excluded_metadata_only']}
    for row in report['commits']:
        source_commit = row['commit']
        entries = []
        for raw in history.git(source, 'ls-tree', '-rz', '--full-tree', source_commit).split(b'\0'):
            if not raw:
                continue
            meta, path = raw.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            path = path.decode()
            if (source_commit, path) in omissions:
                continue
            if kind != 'blob' or (path, oid) not in mappings:
                raise ValueError('Unreviewed tree object')
            entries.append(dict(path=path, mode=mode, oid=mappings[(path, oid)]))
        tree = make_tree(destination, entries, tree_cache)
        original = history.git(source, 'cat-file', 'commit', source_commit)
        header, sep, message = original.partition(b'\n\n')
        fields = []
        for field in header.splitlines():
            if field.startswith(b'tree '):
                field = b'tree '+tree.encode()
            elif field.startswith(b'parent '):
                field = b'parent '+commit_map[field[7:].decode()].encode()
            elif not field.startswith((b'author ', b'committer ')):
                raise ValueError('Unsupported signed/extended commit metadata')
            fields.append(field)
        candidate = history.git(destination, 'hash-object', '-t', 'commit', '-w', '--stdin',
                                data=b'\n'.join(fields)+sep+message).decode().strip()
        commit_map[source_commit] = candidate
    tip = commit_map[report['source_commit']]
    history.git(destination, 'update-ref', 'refs/heads/portfolio', tip)
    if history.git(source, 'rev-parse', '--verify', revision+'^{commit}').decode().strip() != report['source_commit']:
        raise ValueError('Source revision drift')
    if history.git(destination, 'remote').strip():
        raise ValueError('Unexpected candidate remote')
    # Independent full-history check of the actual candidate, not just the plan.
    verified = history.audit(destination, 'refs/heads/portfolio', reviews)
    if verified['result'] != 'PASS_AUTOMATED_REVIEW_ONLY' or verified['commit_count'] != report['commit_count']:
        raise ValueError('Actual candidate history audit failed')
    for old, new in zip(report['commits'], verified['commits']):
        for key in ('author_identity_sha256', 'committer_identity_sha256', 'author_timestamp',
                    'committer_timestamp', 'author_timezone', 'committer_timezone', 'message_sha256'):
            if old[key] != new[key]:
                raise ValueError('Historical identity/date/message changed')
        if new['parents'] != [commit_map[p] for p in old['parents']]:
            raise ValueError('Commit parent topology changed')
    integrity = history.git(destination, 'fsck', '--full', '--strict', '--no-reflogs', '--unreachable')
    if integrity.strip():
        raise ValueError('Unexpected unreachable/dangling objects in isolated candidate')
    return dict(schema=1, source_commit=report['source_commit'], candidate_tip=tip,
                candidate_branch='portfolio', commits_preserved=len(commit_map),
                original_to_candidate_commits=commit_map, changed_blob_versions=changed,
                removed_paths=sorted({x['path'] for x in report['excluded_metadata_only']}),
                identity_dates_messages_topology='PASS_EXACT_PRESERVATION',
                full_candidate_history_audit=verified, candidate_integrity='PASS_FSCK_FULL_STRICT',
                source_refs_or_history_modified=False, remotes=[], publication_authorized=False,
                result='SANITIZED_HISTORY_CANDIDATE_REQUIRES_INDEPENDENT_REVIEW')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.cwd())
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--history-reviews', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('Existing output refused')
        reviews = json.loads(args.history_reviews.read_text(encoding='utf-8'))['records']
        result = build(args.source.resolve(), args.revision, reviews, args.candidate, args.execute)
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write('\n')
        print(json.dumps({k: result[k] for k in ('result', 'source_commit', 'candidate_tip', 'commits_preserved') if k in result}))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        print('PUBLIC_HISTORY_CANDIDATE=BLOCKED; original untouched; diagnostics withheld; no publication')
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
