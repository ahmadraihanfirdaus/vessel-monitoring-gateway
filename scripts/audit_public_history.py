"""Read-only, value-redacted audit of every tree/blob reachable from one commit.

No checkout, clone, remote access, identity rewrite or dotenv read is performed.
An excluded/unreadable object is a publication blocker, never a clean result.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import audit_precommit_security as security
import test_public_archive as archive

MAX_BLOB = 8_000_000
MAX_HISTORY = 4096
MAX_SCAN_BYTES = 128_000_000


def profile_hits(data):
    # Include raw source/JSON escapes, rather than only rendered Windows paths.
    account = rb'[A-Za-z0-9._-]{1,64}'
    separators = re.escape(b'\\') + rb'{1,8}'
    patterns = [rb'[A-Za-z]:' + separators + b'Users' + separators + account,
                rb'[A-Za-z]:/' + b'Users/' + account,
                b'/c/' + b'Users/' + account,
                b'/' + b'Users/' + account,
                b'/' + b'home/' + account]
    return sorted(set(m.group() for p in patterns for m in re.finditer(p, data, re.I)), key=len, reverse=True)


def git(repo, *args, data=None):
    environment = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
    environment.update(GIT_OPTIONAL_LOCKS='0', GIT_NO_REPLACE_OBJECTS='1',
                       GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    result = subprocess.run(
        ['git', '--no-replace-objects', '-c', 'core.hooksPath='+os.devnull,
         '-c', 'safe.directory='+str(Path(repo).resolve()), *args], cwd=repo, input=data,
        capture_output=True, timeout=120,
        env=environment,
    )
    if result.returncode:
        raise ValueError('Git operation refused; diagnostics withheld')
    return result.stdout


def content_review(path, data):
    """Reuse the existing exact-pin reviews; never return matching values."""
    security.findings.clear()
    security.warnings.clear()
    security.reviewed_findings.clear()
    security.reviewed_metadata.clear()
    security.scan_text(path, 'history', data)
    issues = [{'line': x[2], 'reason': x[3], 'kind': kind}
              for kind, values in [('FINDING', security.findings),
                                   ('PRIVACY', security.warnings)] for x in values]
    if profile_hits(data):
        issues.append(dict(line=0, reason='Machine-local profile path', kind='PRIVACY'))
    return issues, len(security.reviewed_findings), len(security.reviewed_metadata)


def apply_reviews(path, oid, data, issues, records):
    remaining, accepted = [], []
    if not any(x['reason'] == 'Possible hardcoded secret' for x in issues):
        return issues, accepted
    lines = data.decode('utf-8-sig').splitlines()
    digest = hashlib.sha256(data).hexdigest()
    for issue in issues:
        matched = None
        if (issue['reason'] == 'Possible hardcoded secret' and issue['kind'] == 'FINDING'
                and path.startswith('.github/workflows/') and 0 < issue['line'] <= len(lines)):
            line_sha = hashlib.sha256(lines[issue['line']-1].encode()).hexdigest()
            matched = next((r for r in records if r.get('path') == path and r.get('oid') == oid
                            and r.get('file_sha256') == digest and r.get('line_sha256') == line_sha
                            and r.get('line') == issue['line'] and r.get('classification') == 'CI_TEST_CONFIGURATION'
                            and isinstance(r.get('rationale'), str) and r['rationale']), None)
        if matched:
            accepted.append(dict(line=issue['line'], classification=matched['classification'],
                                 line_sha256=matched['line_sha256']))
        else:
            remaining.append(issue)
    return remaining, accepted


def audit(repo: Path, revision='HEAD', historical_reviews=()):
    if git(repo, 'rev-parse', '--is-shallow-repository').strip() != b'false':
        raise ValueError('Complete history required, shallow repository refused')
    if git(repo, 'for-each-ref', '--format=%(refname)', 'refs/replace').strip():
        raise ValueError('Replacement refs refused')
    if git(repo, 'rev-parse', '--show-object-format').strip() != b'sha1':
        raise ValueError('Unsupported object format')
    graft = git(repo, 'rev-parse', '--git-path', 'info/grafts').decode().strip()
    if (repo / graft).exists():
        raise ValueError('Grafted history refused')
    head = git(repo, 'rev-parse', '--verify', revision+'^{commit}').decode().strip()
    commits = git(repo, 'rev-list', '--max-count='+str(MAX_HISTORY+1), '--reverse', '--topo-order', head).decode().splitlines()
    if not 0 < len(commits) <= MAX_HISTORY:
        raise ValueError('History bound refused')
    security.findings.clear()
    security.review_records = security.load_review_records()
    if security.findings:
        raise ValueError('Existing security review registry invalid')
    objects = collections.defaultdict(set)
    trees = {}
    commit_rows = []
    metadata_issues = []
    excluded = []
    excluded_oids = set()
    for oid in commits:
        raw = git(repo, 'cat-file', 'commit', oid)
        header, _, message = raw.partition(b'\n\n')
        fields = header.splitlines()
        row = {'commit': oid, 'parents': [x[7:].decode() for x in fields if x.startswith(b'parent ')]}
        for key in ('author', 'committer'):
            values = [x[len(key)+1:] for x in fields if x.startswith(key.encode()+b' ')]
            if len(values) != 1:
                raise ValueError('Malformed commit identity')
            identity, timestamp, zone = values[0].rsplit(b' ', 2)
            name, sep, email = identity.rpartition(b' <')
            if not sep or not email.endswith(b'>'):
                raise ValueError('Malformed commit identity')
            email = email[:-1]
            row[key+'_identity_sha256'] = hashlib.sha256(identity).hexdigest()
            row[key+'_email_sha256'] = hashlib.sha256(email).hexdigest()
            row[key+'_email_class'] = ('GITHUB_NOREPLY' if email.endswith(b'@users.noreply.github.com')
                                       else 'UNVERIFIED_EMAIL')
            row[key+'_timestamp'] = int(timestamp)
            row[key+'_timezone'] = zone.decode('ascii')
            if row[key+'_email_class'] != 'GITHUB_NOREPLY':
                metadata_issues.append(dict(commit=oid, field=key, reason='Email publication/association unverified'))
        issues, _, _ = content_review('COMMIT_METADATA.txt', raw)
        metadata_issues.extend(dict(commit=oid, **x) for x in issues)
        row['message_sha256'] = hashlib.sha256(message).hexdigest()
        tree = git(repo, 'ls-tree', '-rz', '--full-tree', oid)
        row['tree_manifest_sha256'] = hashlib.sha256(tree).hexdigest()
        trees[oid] = []
        for item in tree.split(b'\0'):
            if not item:
                continue
            meta, sep, path = item.partition(b'\t')
            mode, kind, blob = meta.decode('ascii').split()
            path = path.decode('utf-8')
            if not sep or not archive.canonical_path(path):
                raise ValueError('Unsafe historical path; name withheld')
            entry = dict(path=path, mode=mode, oid=blob)
            trees[oid].append(entry)
            if len(trees[oid]) > archive.MAX_FILES:
                raise ValueError('Historical tree entry bound refused')
            if (archive.forbidden_path(path) or path.lower() in security.BLOCKED_PATHS
                    or any(path.lower().startswith(p) for p in security.BLOCKED_DIRECTORIES)):
                excluded.append(dict(commit=oid, **entry, reason='PROHIBITED_NAME_METADATA_ONLY_NOT_READ'))
                excluded_oids.add(blob)
            elif mode not in ('100644', '100755') or kind != 'blob':
                excluded.append(dict(commit=oid, **entry, reason='SPECIAL_ENTRY_NOT_READ'))
            else:
                objects[blob].add(path)
        row['files'] = len(trees[oid])
        commit_rows.append(row)
    for oid in excluded_oids:
        for path in objects.pop(oid, ()):
            excluded.append(dict(oid=oid, path=path, reason='SHARED_WITH_PROHIBITED_NAME_NOT_READ'))
    # One bounded batch process. Excluded objects are never requested.
    sizes = git(repo, 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)',
                data=''.join(x+'\n' for x in objects).encode()).decode().splitlines()
    admitted = []
    total = 0
    for line in sizes:
        oid, kind, size = line.split()
        if kind != 'blob' or int(size) > MAX_BLOB:
            excluded.extend(dict(oid=oid, path=p, reason='BLOB_SIZE_OR_TYPE_NOT_READ') for p in objects[oid])
        else:
            admitted.append(oid)
            total += int(size)
    if total > MAX_SCAN_BYTES:
        raise ValueError('Aggregate history inspection bound refused')
    batch = git(repo, 'cat-file', '--batch', data=''.join(x+'\n' for x in admitted).encode())
    offset = 0
    blobs = []
    for expected in admitted:
        end = batch.index(b'\n', offset)
        oid, kind, size = batch[offset:end].decode().split()
        size = int(size)
        if oid != expected or kind != 'blob':
            raise ValueError('Batch identity mismatch')
        data = batch[end+1:end+1+size]
        offset = end+size+2
        if len(data) != size or batch[offset-1:offset] != b'\n':
            raise ValueError('Batch size mismatch')
        digest = hashlib.sha256(data).hexdigest()
        for path in sorted(objects[oid]):
            issues, review_count, metadata = content_review(path, data)
            issues, historic = apply_reviews(path, oid, data, issues, historical_reviews)
            blobs.append(dict(oid=oid, path=path, bytes=size, sha256=digest,
                              issues=issues, exact_nonsecret_reviews=review_count,
                              dependency_author_reviews=metadata, historical_nonsecret_reviews=historic))
    if offset != len(batch):
        raise ValueError('Trailing batch data')
    findings = sum(bool(x['issues']) for x in blobs)
    return dict(schema=1, source_commit=head, scope='ALL_COMMITS_REACHABLE_FROM_SINGLE_APPROVED_TIP',
                commit_count=len(commits), commits=commit_rows, unique_blobs_read=len(admitted),
                blob_path_versions=len(blobs), historical_paths=len({p for v in trees.values() for p in [x['path'] for x in v]}),
                blobs=blobs, excluded_metadata_only=excluded, commit_metadata_issues=metadata_issues,
                flagged_blob_path_versions=findings,
                result='BLOCKED' if findings or excluded or metadata_issues else 'PASS_AUTOMATED_REVIEW_ONLY',
                publication_authorized=False, secrets_or_matching_values_recorded=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--history-reviews', type=Path)
    args = parser.parse_args()
    try:
        reviews = json.loads(args.history_reviews.read_text(encoding='utf-8'))['records'] if args.history_reviews else []
        report = audit(args.repo.resolve(), args.revision, reviews)
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write('\n')
        print(json.dumps({k: report[k] for k in ['source_commit', 'commit_count', 'unique_blobs_read',
                         'blob_path_versions', 'flagged_blob_path_versions', 'result']}))
        return 0 if report['result']=='PASS_AUTOMATED_REVIEW_ONLY' else 3
    except (ValueError, OSError, subprocess.SubprocessError, UnicodeError):
        print('HISTORY_AUDIT=BLOCKED; details withheld; no publication authorized')
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
