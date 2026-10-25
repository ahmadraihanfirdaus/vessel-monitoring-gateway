"""Isolated regression tests; never stage or mutate the actual project index."""

from pathlib import Path
import hashlib
import json
import secrets
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().with_name("audit_precommit_security.py")


class SecurityAuditRegressionTests(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory(prefix="vg_security_test_")
        self.addCleanup(self._temporary.cleanup)
        self.repo = Path(self._temporary.name)
        self.exec_git("init", "-q")
        (self.repo / "scripts").mkdir()
        shutil.copyfile(SCRIPT, self.repo / "scripts" / SCRIPT.name)
        self.write("firmware/src/clean.c", "int safe(void) { return 0; }\n")
        self.write("firmware/src/clean.h", "#ifndef CLEAN_H\n#define CLEAN_H\n#endif\n")
        self.exec_git("add", "scripts/audit_precommit_security.py", "firmware/src/clean.c", "firmware/src/clean.h")

    def exec_git(self, *args):
        done = subprocess.run(["git", *args], cwd=self.repo, text=True, capture_output=True)
        self.assertEqual(done.returncode, 0, done.stderr)

    def write(self, relative, content):
        file = self.repo / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")

    def scan(self):
        return subprocess.run([sys.executable, "scripts/audit_precommit_security.py"], cwd=self.repo, text=True, capture_output=True)

    def test_clean_c_and_h_sources_pass(self):
        result = self.scan()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT: AUTOMATED SECURITY SCREEN PASSED", result.stdout)

    def test_sdk_defaults_are_scanned_as_text_without_a_secret_exemption(self):
        self.write('firmware/sdkconfig.defaults', 'CONFIG_MBEDTLS_HAVE_TIME_DATE=y\n')
        self.assertEqual(self.scan().returncode, 0)
        self.write('firmware/sdkconfig.defaults', self.assignment(repr(secrets.token_hex(16))))
        result = self.scan()
        self.assertEqual(result.returncode, 1)
        self.assertIn('Possible hardcoded secret', result.stdout)
        self.write('firmware/sdkconfig.defaults', 'ghp_'+'Z'*25+'\n')
        self.assertEqual(self.scan().returncode, 1)
        (self.repo/'firmware/sdkconfig.defaults').write_bytes(b'\x00\xff')
        self.assertEqual(self.scan().returncode, 1)

    def test_runtime_test_generation_requires_exact_review_and_changes_invalidate_it(self):
        self.write('runtime.php', self.assignment('bin2hex(random_bytes(20))', True))
        self.assertNotEqual(self.scan().returncode, 0)
        self.reviewed('runtime.php', classification='RUNTIME_GENERATED_TEST_VALUE')
        self.assertEqual(self.scan().returncode, 0)
        self.write('runtime.php', self.assignment(repr(secrets.token_hex(16)), True))
        self.assertNotEqual(self.scan().returncode, 0)

    def test_runtime_review_still_cannot_waive_credential_token(self):
        token = 'ghp_' + 'C' * 25
        self.write('runtime.php', self.assignment(repr(token), True))
        self.reviewed('runtime.php', classification='RUNTIME_GENERATED_TEST_VALUE')
        result = self.scan()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Possible credential token', result.stdout)

    def test_staged_token_in_c_is_rejected(self):
        fake_token = "ghp_" + "A" * 25
        self.write("firmware/src/clean.c", f'const char *sample = "{fake_token}";\n')
        self.exec_git("add", "firmware/src/clean.c")
        result = self.scan()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Possible credential token", result.stdout)

    def test_unstaged_change_in_h_is_rejected(self):
        fake_token = "ghp_" + "B" * 25
        self.write("firmware/src/clean.h", f'const char *sample = "{fake_token}";\n')
        result = self.scan()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[working]", result.stdout)

    def test_unsupported_untracked_binary_is_rejected(self):
        (self.repo / "surprise.bin").write_bytes(b"\x00\x01\x02")
        result = self.scan()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported format", result.stdout)

    def reviewed(self, path, classification='SYNTHETIC_NEGATIVE_FIXTURE'):
        data = (self.repo/path).read_bytes()
        lines = data.decode().splitlines()
        records = [{'id': 'fixture-review-'+str(i), 'path': path,
                    'file_sha256': hashlib.sha256(data).hexdigest(),
                    'line_sha256': hashlib.sha256(line.encode()).hexdigest(),
                    'classification': classification, 'rationale': 'Generated isolated test fixture only.'}
                   for i, line in enumerate(lines)]
        self.write('scripts/security-reviewed-findings.json', json.dumps({'version': 1, 'records': records}))

    def assignment(self, value, arrow=False):
        key = 'pass'+'word'
        return repr(key)+(' => ' if arrow else ' = ')+value+';\n'

    def test_php_arrow_empty_and_external_lookup_are_not_secret_values(self):
        for value in ("''", 'null', "env('DB_"+'PASSWORD'+"')", "env('DB_"+'PASSWORD'+"', '')"):
            with self.subTest(value_kind=value.split('(')[0]):
                self.write('check.php', self.assignment(value, True))
                result=self.scan()
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_php_arrow_literal_and_environment_literal_fallback_are_rejected(self):
        sensitive=secrets.token_hex(16)
        for value in (repr(sensitive), "env('DB_"+'PASSWORD'+"', "+repr(sensitive)+")"):
            self.write('check.php', self.assignment(value, True))
            result=self.scan()
            self.assertEqual(result.returncode, 1)
            self.assertIn('Possible hardcoded secret', result.stdout)
            self.assertNotIn(sensitive, result.stdout+result.stderr)

    def test_hash_pinned_review_is_narrow_and_visible(self):
        self.write('check.php', self.assignment(repr('hashed'), True))
        self.reviewed('check.php', 'FRAMEWORK_CAST')
        result=self.scan()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('REVIEWED NON-SECRET:', result.stdout)

    def test_any_file_mutation_invalidates_review(self):
        self.write('check.php', self.assignment(repr('hashed'), True))
        self.reviewed('check.php', 'FRAMEWORK_CAST')
        self.write('check.php', (self.repo/'check.php').read_text()+'// changed\n')
        self.assertEqual(self.scan().returncode, 1)

    def test_reviewed_index_cannot_hide_unstaged_secret(self):
        self.write('check.php', self.assignment(repr('hashed'), True))
        self.reviewed('check.php', 'FRAMEWORK_CAST')
        self.exec_git('add', 'check.php')
        self.write('check.php', self.assignment(repr(secrets.token_hex(16)), True))
        result=self.scan()
        self.assertEqual(result.returncode, 1)
        self.assertIn('[working]', result.stdout)

    def test_registry_cannot_waive_strong_secret_signatures(self):
        signatures=['gh'+'p_'+secrets.token_hex(15),
                    '-----BEGIN '+'PRIVATE KEY-----',
                    'mysql'+'://synthetic:'+secrets.token_hex(16)+'@example.invalid/db']
        for signature in signatures:
            self.write('check.php', self.assignment(repr(signature), True))
            self.reviewed('check.php')
            result=self.scan()
            self.assertEqual(result.returncode, 1)
            self.assertNotIn(signature, result.stdout+result.stderr)

    def test_registry_rejects_wildcards_paths_hashes_and_duplicate_ids(self):
        self.write('check.php', self.assignment(repr('hashed'), True))
        self.reviewed('check.php')
        original=json.loads((self.repo/'scripts/security-reviewed-findings.json').read_text())
        for change in ({'path':'*.php'}, {'path':'../check.php'}, {'path':'.env'},
                       {'file_sha256':'bad'}, {'classification':'IGNORE_ALL'}):
            doc=json.loads(json.dumps(original));doc['records'][0].update(change)
            self.write('scripts/security-reviewed-findings.json', json.dumps(doc))
            result=self.scan()
            self.assertEqual(result.returncode, 1)
            self.assertIn('Invalid reviewed-finding registry',result.stdout)
        original['records'].append(original['records'][0])
        self.write('scripts/security-reviewed-findings.json',json.dumps(original))
        self.assertEqual(self.scan().returncode,1)

    def test_supported_text_formats_still_screen_all_content(self):
        for name in ('backend/artisan','backend/composer.lock','backend/.editorconfig',
                     'backend/.htaccess','evidence/hash.sha256'):
            self.write(name,'{}\n')
        self.assertEqual(self.scan().returncode,0)
        self.write('backend/composer.lock',json.dumps({'api_'+'key':secrets.token_hex(16)}))
        self.assertEqual(self.scan().returncode,1)

    def test_supported_format_cannot_hide_binary_invalid_utf8_or_oversize_data(self):
        for data in (b'\0',b'\xff',b'x'*(5*1024*1024+1)):
            (self.repo/'hash.sha256').write_bytes(data)
            self.assertEqual(self.scan().returncode,1)

    def test_sensitive_path_cannot_be_reviewed(self):
        self.write('.env',self.assignment(repr(secrets.token_hex(16))))
        self.reviewed('.env')
        result=self.scan()
        self.assertEqual(result.returncode,1)
        self.assertIn('Sensitive filename',result.stdout)

    def lock_metadata(self, extra=None):
        mail=('synthetic-author'+'@'+'upstream.invalid')
        package={'name':'synthetic/package','source':{'url':'https://github.com/synthetic/package'},
                 'authors':[{'email':mail}]}
        doc={'packages':[package],'packages-dev':[]}
        if extra:doc.update(extra)
        self.write('backend/laravel/composer.lock',json.dumps(doc,indent=2)+'\n')
        self.reviewed('backend/laravel/composer.lock','UPSTREAM_AUTHOR_METADATA')

    def test_pinned_upstream_author_metadata_is_reviewed_without_printing_address(self):
        self.lock_metadata()
        result=self.scan()
        self.assertEqual(result.returncode,0,result.stdout)
        self.assertIn('Reviewed dependency author metadata: 1',result.stdout)
        self.assertNotIn(('synthetic-author'+'@'+'upstream.invalid'),result.stdout)

    def test_metadata_review_cannot_hide_other_contact_fields(self):
        self.lock_metadata({'contact':('unrelated-contact'+'@'+'private.invalid')})
        result=self.scan()
        self.assertEqual(result.returncode,1)
        self.assertIn('Email address requires privacy review',result.stdout)

    def test_root_email_field_cannot_impersonate_an_author_field(self):
        self.lock_metadata({'email':('synthetic-author'+'@'+'upstream.invalid')})
        self.assertEqual(self.scan().returncode,1)

    def test_non_array_authors_cannot_be_reviewed(self):
        self.lock_metadata()
        path=self.repo/'backend/laravel/composer.lock'
        doc=json.loads(path.read_text());doc['packages'][0]['authors']={'named':doc['packages'][0]['authors'][0]}
        path.write_text(json.dumps(doc,indent=2)+'\n')
        self.reviewed('backend/laravel/composer.lock','UPSTREAM_AUTHOR_METADATA')
        self.assertEqual(self.scan().returncode,1)

    def test_changed_metadata_invalidates_pin(self):
        self.lock_metadata()
        path=self.repo/'backend/laravel/composer.lock'
        path.write_text(path.read_text()+'\n')
        self.assertEqual(self.scan().returncode,1)

    def test_metadata_pins_cannot_waive_password_or_url_credentials(self):
        self.lock_metadata({'api_'+'key':secrets.token_hex(16)})
        self.assertEqual(self.scan().returncode,1)
        self.write('check.txt','https'+'://user:'+secrets.token_hex(16)+'@example.invalid')
        self.reviewed('check.txt')
        self.assertEqual(self.scan().returncode,1)


if __name__ == "__main__":
    unittest.main()
