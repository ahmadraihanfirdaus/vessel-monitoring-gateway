"""Owned synthetic repositories only; never publication/contribution activity."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import audit_public_history as audit
import prepare_public_history as prepare


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.owned = tempfile.TemporaryDirectory(prefix='vg-history-unit-')
        self.repo = Path(self.owned.name)/'source'
        self.repo.mkdir()
        audit.git(self.repo, 'init', '--quiet')
        audit.git(self.repo, 'config', 'user.name', 'Synthetic unit fixture')
        audit.git(self.repo, 'config', 'user.email', 'fixture@users.noreply.github.com')

    def tearDown(self):
        self.owned.cleanup()

    def commit(self, name, data, message='Synthetic unit test, never published'):
        target=self.repo/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        audit.git(self.repo, 'add', '--force', '--', name)
        audit.git(self.repo, 'commit', '--quiet', '-m', message)
        return audit.git(self.repo, 'rev-parse', 'HEAD').decode().strip()

    def test_profile_rendered_escaped_and_posix(self):
        for slashes in range(1, 5):
            value=b'C:'+b'\\'*slashes+b'Users'+b'\\'*slashes+b'unit-person'
            self.assertTrue(audit.profile_hits(value))
        self.assertTrue(audit.profile_hits(b'/'+b'home/unit-person/artifact'))
        self.assertFalse(audit.profile_hits(b'C:/'+b'Users/<user>/artifact'))
        self.assertFalse(audit.profile_hits(Path(audit.__file__).read_bytes()))

    def test_deleted_secret_is_still_a_history_blocker(self):
        token=b'gh'+b'p_'+b'Q'*24
        first=self.commit('historical.txt',token)
        audit.git(self.repo,'rm','--','historical.txt')
        audit.git(self.repo,'commit','--quiet','-m','Remove synthetic fixture')
        report=audit.audit(self.repo)
        self.assertEqual(report['commit_count'],2)
        self.assertEqual(report['result'],'BLOCKED')
        self.assertTrue(any(b['issues'] for b in report['blobs']))
        self.assertNotIn(token.decode(),json.dumps(report))
        self.assertEqual(report['commits'][0]['commit'],first)

    def test_dotenv_and_shared_oid_never_read(self):
        self.commit('.env.example',b'synthetic forbidden file content')
        self.commit('copied.txt',b'synthetic forbidden file content')
        original=audit.git
        requested=[]
        def observe(repo,*args,data=None):
            if args and args[0]=='cat-file' and any(x.startswith('--batch') for x in args):
                requested.append(data)
            return original(repo,*args,data=data)
        oid=prepare.blob_oid(b'synthetic forbidden file content').encode()
        with mock.patch.object(audit,'git',side_effect=observe):
            report=audit.audit(self.repo)
        self.assertEqual(report['unique_blobs_read'],0)
        self.assertTrue(all(oid not in (x or b'') for x in requested))
        self.assertTrue(any(x['reason']=='SHARED_WITH_PROHIBITED_NAME_NOT_READ' for x in report['excluded_metadata_only']))

    def test_exact_review_does_not_waive_change_or_private_key(self):
        path='.github/workflows/unit.yml'
        data=b'_'.join([b'TEST', b'PASS'+b'WORD'])+b': '+b'synthetic-unit-fixture\n'
        oid=prepare.blob_oid(data)
        issues,_,_=audit.content_review(path,data)
        self.assertEqual(len(issues),1)
        record=dict(path=path,oid=oid,file_sha256=hashlib.sha256(data).hexdigest(),
                    line=1,line_sha256=hashlib.sha256(data.strip()).hexdigest(),
                    classification='CI_TEST_CONFIGURATION',rationale='Synthetic unit only')
        self.assertFalse(audit.apply_reviews(path,oid,data,issues,[record])[0])
        self.assertTrue(audit.apply_reviews(path,oid+'0',data,issues,[record])[0])
        self.assertTrue(audit.apply_reviews(path,oid,data+b'#changed\n',issues,[record])[0])
        key=b'-----BEGIN '+b'PRIVATE KEY-----\n'
        flagged,_,_=audit.content_review(path,key)
        self.assertTrue(audit.apply_reviews(path,oid,key,flagged,[record])[0])

    def test_actual_sanitized_history_preserves_all_commits_and_metadata(self):
        prefix=b'C:/'+b'Users/unit-person'
        self.commit('README.md',b'Owned synthetic test\n'+prefix+b'/file\n')
        self.commit('.env.example',b'synthetic fixture, never read')
        audit.git(self.repo,'commit','--allow-empty','--quiet','-m','Genuine synthetic empty test commit')
        destination=self.repo/'private/portfolio-history-unit'
        result=prepare.build(self.repo,'HEAD',[],destination,execute=True)
        self.assertEqual(result['commits_preserved'],3)
        self.assertEqual(result['identity_dates_messages_topology'],'PASS_EXACT_PRESERVATION')
        self.assertEqual(result['full_candidate_history_audit']['result'],'PASS_AUTOMATED_REVIEW_ONLY')
        self.assertEqual(audit.git(destination,'remote'),b'')
        paths=audit.git(destination,'ls-tree','-r','--name-only','portfolio').decode()
        self.assertNotIn('.env',paths)
        self.assertFalse(audit.profile_hits(audit.git(destination,'show','portfolio:README.md')))
        self.assertTrue(audit.profile_hits(audit.git(self.repo,'show','HEAD:README.md')))
        with self.assertRaises(ValueError):
            prepare.build(self.repo,'HEAD',[],destination,execute=True)

    def test_unresolved_credentials_never_create_candidate(self):
        self.commit('file.txt',b'gh'+b'p_'+b'Q'*24)
        destination=self.repo/'private/portfolio-history-blocked'
        with self.assertRaises(ValueError):
            prepare.build(self.repo,'HEAD',[],destination,execute=True)
        self.assertFalse(destination.exists())

    def test_unknown_code_privacy_and_destination_refused(self):
        raw=b'# '+b'C:/'+b'Users/unit-person/file\n'
        with self.assertRaises(ValueError):
            prepare.sanitize('runtime.py',raw)
        self.commit('README.md',b'No private content\n')
        with self.assertRaises(ValueError):
            prepare.build(self.repo,'HEAD',[],self.repo,execute=True)

    def test_binary_and_shallow_fail_closed(self):
        self.commit('file.txt',b'\x00\xff')
        report=audit.audit(self.repo)
        self.assertEqual(report['result'],'BLOCKED')
        (self.repo/'.git/shallow').write_text(report['source_commit']+'\n')
        with self.assertRaises(ValueError):
            audit.audit(self.repo)

    def test_commit_message_disclosure_blocks_before_build(self):
        marker=b'gh'+b'p_'+b'Z'*24
        self.commit('file.txt',b'Safe file\n',message=marker.decode())
        report=audit.audit(self.repo)
        self.assertTrue(report['commit_metadata_issues'])
        self.assertNotIn(marker.decode(),json.dumps(report))
        destination=self.repo/'private/portfolio-history-message'
        with self.assertRaises(ValueError):
            prepare.build(self.repo,'HEAD',[],destination,execute=True)
        self.assertFalse(destination.exists())

    def test_scanner_fixture_redaction_preserves_runtime_negative_oracle(self):
        for value in (b'C:'+b'\\Users\\unit-person\\file',b'C:/'+b'Users/unit-person/file',b'/c/'+b'Users/unit-person/file'):
            original=('data = '+repr(value)+'\n').encode()
            self.assertTrue(audit.profile_hits(original))
            new=prepare.sanitize('scripts/test_public_archive_scanner.py',original)
            self.assertFalse(audit.profile_hits(new))
            namespace={}
            exec(compile(new,'<owned-synthetic-test>','exec'),namespace)
            self.assertTrue(audit.profile_hits(namespace['data']))

    def test_git_environment_cannot_redirect_repository_writes(self):
        with mock.patch.dict(os.environ, {'GIT_DIR':str(self.repo/'wrong-repository'),
                                         'GIT_WORK_TREE':str(self.repo/'wrong-worktree')}):
            self.commit('file.txt',b'Owned safe fixture\n')
            self.assertEqual(audit.audit(self.repo)['result'],'PASS_AUTOMATED_REVIEW_ONLY')
        self.assertFalse((self.repo/'wrong-repository').exists())

    def test_history_blob_and_aggregate_bounds_fail_closed(self):
        self.commit('file.txt',b'Owned bounded fixture\n')
        with mock.patch.object(audit,'MAX_HISTORY',0),self.assertRaises(ValueError):
            audit.audit(self.repo)
        with mock.patch.object(audit,'MAX_BLOB',1):
            report=audit.audit(self.repo)
            self.assertEqual(report['result'],'BLOCKED')
            self.assertEqual(report['unique_blobs_read'],0)
        with mock.patch.object(audit,'MAX_SCAN_BYTES',1),self.assertRaises(ValueError):
            audit.audit(self.repo)


if __name__=='__main__':
    unittest.main()
