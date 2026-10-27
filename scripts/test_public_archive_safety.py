"""Real isolated Git/ZIP integration and hostile metadata, with no real secrets."""
from contextlib import redirect_stdout
import hashlib
import io
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

import create_public_archive as exporter
import test_public_archive as verifier


class PublicArchiveSafetyTest(unittest.TestCase):
    def setUp(self):
        isolated_git = patch.dict(os.environ, {'GIT_CONFIG_NOSYSTEM': '1',
                                              'GIT_CONFIG_GLOBAL': os.devnull,
                                              'GIT_CONFIG_SYSTEM': os.devnull})
        isolated_git.start()
        self.addCleanup(isolated_git.stop)
        self.temp = tempfile.TemporaryDirectory(prefix='vg-public-audit-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.assertEqual(self.root.parent, Path(tempfile.gettempdir()).resolve())
        self.assertFalse(self.root.is_symlink())
        self.repo = self.root/'source'
        self.repo.mkdir()
        subprocess.run(['git', 'init', '-q', '-b', 'develop', str(self.repo)], check=True, capture_output=True)
        self.public = {'README.md': b'public synthetic source\n',
                       'firmware/sdkconfig.defaults': b'CONFIG_EXAMPLE=y\n'}
        self.excluded = {'backend/.env.example': b'excluded synthetic template fixture\n',
                         'backend/.env.testing': b'excluded synthetic local fixture\n',
                         'backend/vendor/cache.txt': b'excluded dependency fixture\n',
                         'firmware/.pio/build.txt': b'excluded build fixture\n',
                         'firmware/sdkconfig': b'excluded generated fixture\n'}
        for name, data in {**self.public, **self.excluded}.items():
            path = self.repo/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        subprocess.run(['git', 'add', '--all'], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'user.name=Synthetic Archive Test', '-c',
                        'user.email=synthetic-archive.invalid', 'commit', '-qm', 'synthetic fixture'],
                       cwd=self.repo, check=True, capture_output=True)
        self.output = self.root/'new.zip'

    def check(self, path):
        with redirect_stdout(io.StringIO()):
            return verifier.check_archive(path, self.repo)

    def synthetic_zip(self, changes=(), omit=(), modes=None):
        with warnings.catch_warnings(), zipfile.ZipFile(self.output, 'w') as archive:
            warnings.simplefilter('ignore', UserWarning)  # Expected duplicate hostile entry only.
            for name, data in [*[(p, b) for p, b in self.public.items() if p not in omit], *changes]:
                info = zipfile.ZipInfo(verifier.PREFIX+name)
                if modes and name in modes:
                    info.external_attr = modes[name] << 16
                archive.writestr(info, data)
        return self.output

    def test_metadata_excludes_dotenv_caches_before_any_excluded_blob_request(self):
        excluded_oids = {verifier.git(self.repo, 'rev-parse', 'HEAD:'+p).strip() for p in self.excluded}
        original = verifier.git
        calls = []
        def guarded(repo, *args, input_data=None):
            calls.append(args)
            if args[0] == 'cat-file':
                for oid in excluded_oids:
                    self.assertNotIn(oid, input_data or b'')
                    self.assertNotIn(oid.decode(), args)
            return original(repo, *args, input_data=input_data)
        with patch.object(verifier, 'git', side_effect=guarded):
            plan = verifier.archive_plan(self.repo)
        self.assertEqual({x['path'] for x in plan['files']}, set(self.public))
        self.assertEqual(set(plan['excluded']), set(self.excluded))
        self.assertFalse(any(c[:2] == ('cat-file', 'blob') for c in calls))

    def test_real_filtered_archive_keeps_sdk_defaults_and_original_commit_bytes(self):
        before = {p: hashlib.sha256((self.repo/p).read_bytes()).hexdigest() for p in self.public}
        with redirect_stdout(io.StringIO()):
            result = exporter.create_archive(self.repo, self.output)
        self.assertEqual(result['files'], 2)
        self.assertEqual(result['excluded'], len(self.excluded))
        self.assertEqual(result['sha256'], hashlib.sha256(self.output.read_bytes()).hexdigest())
        self.check(self.output)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(set(archive.namelist()), {verifier.PREFIX+p for p in self.public})
            for p, data in self.public.items():
                self.assertEqual(archive.read(verifier.PREFIX+p), data)
        self.assertEqual(before, {p: hashlib.sha256((self.repo/p).read_bytes()).hexdigest() for p in self.public})
        self.assertFalse(verifier.git(self.repo, 'status', '--porcelain').strip())

    def test_default_plan_never_creates_output_or_reads_blob_content_despite_wip(self):
        (self.repo/'README.md').write_bytes(b'owned uncommitted fixture\n')
        output = io.StringIO()
        with patch.object(Path, 'cwd', return_value=self.repo), \
             patch.object(sys, 'argv', ['create_public_archive.py', str(self.output)]), \
             patch.object(exporter, 'create_archive') as create, redirect_stdout(output):
            self.assertEqual(exporter.main(), 0)
        create.assert_not_called()
        self.assertIn('PLAN_ONLY_NO_BLOB_CONTENT_READ_NO_OUTPUT', output.getvalue())
        self.assertFalse(self.output.exists())

    def test_dirty_tracked_or_staged_or_foreign_untracked_blocks_before_output(self):
        (self.repo/'README.md').write_bytes(b'owned changed source\n')
        with self.assertRaises(ValueError): exporter.create_archive(self.repo, self.output)
        self.assertFalse(self.output.exists())
        verifier.git(self.repo, 'add', 'README.md')
        with self.assertRaises(ValueError): exporter.create_archive(self.repo, self.output)
        self.assertFalse(self.output.exists())
        # Keep dirty test state; each condition is independently checked in a fresh test.

    def test_foreign_untracked_blocks_but_three_protected_files_are_not_exported(self):
        for p in exporter.PROTECTED_UNTRACKED:
            target = self.repo/p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'protected synthetic untracked fixture\n')
        exporter.clean_snapshot(self.repo)
        foreign = self.repo/'unexpected.txt'
        foreign.write_bytes(b'unrelated owned fixture\n')
        with self.assertRaises(ValueError): exporter.create_archive(self.repo, self.output)
        self.assertFalse(self.output.exists())
        for p in exporter.PROTECTED_UNTRACKED:
            self.assertEqual((self.repo/p).read_bytes(), b'protected synthetic untracked fixture\n')

    def test_existing_output_and_existing_temporary_neighbor_are_never_overwritten(self):
        self.output.write_bytes(b'existing user-owned fixture\n')
        neighbor = Path(str(self.output)+'.tmp')
        neighbor.write_bytes(b'existing neighbor fixture\n')
        with self.assertRaises(ValueError): exporter.create_archive(self.repo, self.output)
        self.assertEqual(self.output.read_bytes(), b'existing user-owned fixture\n')
        self.assertEqual(neighbor.read_bytes(), b'existing neighbor fixture\n')

    def test_exclusive_open_refuses_a_raced_existing_output(self):
        original = Path.open
        def raced(path, mode='r', *args, **kwargs):
            if path == self.output and mode == 'xb':
                with original(path, 'wb') as handle: handle.write(b'raced user-owned fixture\n')
            return original(path, mode, *args, **kwargs)
        with patch.object(Path, 'open', raced), self.assertRaises(FileExistsError):
            exporter.create_archive(self.repo, self.output)
        self.assertEqual(self.output.read_bytes(), b'raced user-owned fixture\n')

    def test_forbidden_zip_metadata_is_rejected_before_any_payload_is_opened(self):
        names = ['.env.testing', '.git/config', 'vendor/file.txt', '.pio/file.bin',
                 '../outside.txt', 'C:/outside.txt', 'nested//file.txt', 'NUL.txt',
                 'back\\slash.txt', 'extra/', 'README.md', 'readme.md']
        for name in names:
            with self.subTest(name=name):
                self.synthetic_zip([(name, b'forbidden synthetic fixture')])
                with patch.object(zipfile.ZipFile, 'open', side_effect=AssertionError('payload read')), \
                     self.assertRaises(ValueError): self.check(self.output)

    def test_linked_zip_entry_is_refused_before_payload_read(self):
        self.synthetic_zip(modes={'README.md': stat.S_IFLNK | 0o777})
        with patch.object(zipfile.ZipFile, 'open', side_effect=AssertionError('payload read')), \
             self.assertRaises(ValueError): self.check(self.output)

    def test_root_directory_link_special_mode_and_encryption_are_refused(self):
        for name, mode in [('', stat.S_IFLNK | 0o777), ('README.md', stat.S_IFCHR | 0o644),
                           ('README.md', stat.S_IFREG | 0o4644)]:
            self.synthetic_zip([(name, b'')], modes={name: mode}) if name else self.synthetic_zip([('', b'')])
            with zipfile.ZipFile(self.output) as archive:
                infos = archive.infolist()
            if name == '':
                infos[-1].filename = verifier.PREFIX
                infos[-1].external_attr = mode << 16
            with patch.object(zipfile.ZipFile, 'infolist', return_value=infos), \
                 patch.object(zipfile.ZipFile, 'open', side_effect=AssertionError('payload read')), \
                 self.assertRaises(ValueError): self.check(self.output)
        self.synthetic_zip()
        with zipfile.ZipFile(self.output) as archive: infos = archive.infolist()
        infos[0].flag_bits |= 1
        with patch.object(zipfile.ZipFile, 'infolist', return_value=infos), \
             patch.object(zipfile.ZipFile, 'open', side_effect=AssertionError('payload read')), \
             self.assertRaises(ValueError): self.check(self.output)

    def test_git_timeout_never_echoes_unredacted_diagnostics(self):
        with patch.object(verifier.subprocess, 'run', side_effect=subprocess.TimeoutExpired('synthetic private diagnostic', 60)):
            with self.assertRaisesRegex(ValueError, '^Git snapshot operation exceeded its bound$'):
                verifier.git(self.repo, 'rev-parse', 'HEAD')

    def test_exact_private_blob_omission_is_metadata_pinned_not_a_scan_waiver(self):
        path = 'README.md'
        oid = verifier.git(self.repo, 'rev-parse', 'HEAD:'+path).decode().strip()
        original = verifier.git
        def guarded(repo, *args, input_data=None):
            if args[0] == 'cat-file':
                self.assertNotIn(oid.encode(), input_data or b'')
                self.assertNotIn(oid, args)
            return original(repo, *args, input_data=input_data)
        with patch.object(verifier, 'PRIVATE_SNAPSHOT_BLOBS', {path: oid}), \
             patch.object(verifier, 'git', side_effect=guarded):
            plan = verifier.archive_plan(self.repo)
        self.assertNotIn(path, {x['path'] for x in plan['files']})
        self.assertIn(dict(path=path, oid=oid, reason='EXACT_HISTORICAL_PRIVATE_PROFILE_BLOB'),
                      plan['excluded_details'])
        with patch.object(verifier, 'PRIVATE_SNAPSHOT_BLOBS', {path: '0'*40}):
            plan = verifier.archive_plan(self.repo)
        self.assertIn(path, {x['path'] for x in plan['files']})
        # A non-matching/changed blob still undergoes the normal content scan.
        with self.assertRaises(ValueError):
            verifier.inspect_content(b'\0'+b'-----BEGIN '+b'PRIVATE KEY-----')

    def test_directory_payload_comments_extra_and_ambiguous_names_cannot_hide_content(self):
        self.synthetic_zip([('', b'non-source directory payload')])
        with patch.object(zipfile.ZipFile, 'open', side_effect=AssertionError('payload read')), \
             self.assertRaises(ValueError): self.check(self.output)
        self.synthetic_zip()
        with zipfile.ZipFile(self.output, 'a') as archive: archive.comment = b'non-source comment'
        with self.assertRaises(ValueError): self.check(self.output)
        for field, value in [('comment', b'non-source entry comment'),
                             ('extra', b'non-source extra metadata'),
                             ('orig_filename', verifier.PREFIX+'README.md\0hidden')]:
            self.synthetic_zip()
            with zipfile.ZipFile(self.output) as archive: infos = archive.infolist()
            setattr(infos[0], field, value)
            with patch.object(zipfile.ZipFile, 'infolist', return_value=infos), \
                 patch.object(zipfile.ZipFile, 'open', side_effect=AssertionError('payload read')), \
                 self.assertRaises(ValueError): self.check(self.output)

    def test_missing_extra_and_same_length_mutated_blobs_are_refused(self):
        for changes, omit in [([], ['README.md']), ([('extra.txt', b'x')], []),
                              ([('README.md', b'X'+self.public['README.md'][1:])], ['README.md'])]:
            self.synthetic_zip(changes, omit)
            with self.assertRaises(ValueError): self.check(self.output)

    def test_oversize_limits_block_before_content_retrieval_or_output(self):
        with patch.object(verifier, 'MAX_FILE_BYTES', 4), self.assertRaises(ValueError):
            exporter.create_archive(self.repo, self.output)
        self.assertFalse(self.output.exists())
        with patch.object(verifier, 'MAX_TOTAL_BYTES', 4), self.assertRaises(ValueError):
            exporter.create_archive(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_binary_nul_does_not_bypass_high_confidence_secret_scan(self):
        marker = b'-----BEGIN '+b'PRIVATE KEY-----'
        with self.assertRaises(ValueError): verifier.inspect_content(b'\0synthetic '+marker)
        verifier.inspect_content(b'\0ordinary synthetic binary fixture')

    def test_output_links_private_targets_missing_parents_and_repo_output_are_refused(self):
        for target in [self.root/'missing'/'out.zip', self.repo/'out.zip',
                       self.root/'.git'/'out.zip', self.root/'out.txt']:
            with self.assertRaises(ValueError): exporter.create_archive(self.repo, target)
            self.assertFalse(target.exists())
        with patch.object(Path, 'is_symlink', return_value=True), self.assertRaises(ValueError):
            exporter.output_target(self.output)

    def test_source_commit_change_cannot_be_reported_as_success(self):
        original = exporter.git
        calls = 0
        def moved(repo, *args, input_data=None):
            nonlocal calls
            if args == ('rev-parse', 'HEAD'):
                calls += 1
                if calls == 2: return b'0'*40+b'\n'
            return original(repo, *args, input_data=input_data)
        with patch.object(exporter, 'git', side_effect=moved), redirect_stdout(io.StringIO()), \
             self.assertRaises(ValueError): exporter.create_archive(self.repo, self.output)
        self.assertTrue(self.output.exists())  # Own incomplete/result artifact is retained, not deleted.


if __name__ == '__main__':
    unittest.main(verbosity=2)
