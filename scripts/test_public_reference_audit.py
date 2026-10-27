"""Public reference admission and canonical records; no database or network."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import check_living_traceability as gate


class PublicReferenceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='vg-reference-audit-')
        self.root = Path(self.temp.name).resolve()
        self.assertEqual(self.root.parent, Path(tempfile.gettempdir()).resolve())
        self.assertFalse(self.root.is_symlink())
        self.addCleanup(self.temp.cleanup)
        self.file = self.root/'public.txt'
        self.file.write_bytes(b'public synthetic audit marker')

    def test_regular_public_file_hash_is_stable_without_copying_content(self):
        first=gate.public_reference('public.txt',self.root)
        self.assertEqual(first,gate.public_reference('public.txt',self.root))
        self.assertEqual(len(first['sha256']),64)
        self.assertEqual(first['bytes'],29)

    def test_sensitive_noncanonical_and_foreign_paths_fail_before_any_open(self):
        for path in ('../public.txt','/public.txt','C:/public.txt','a\\b','a//b','a/./b',
                     '.env','.ENV.testing','backend/laravel/.env.example','.git/config',
                     '.aws/credentials','tokens.json','private.key','x.pem','a\nb'):
            with self.subTest(path=path),patch.object(Path,'open') as opened,self.assertRaises(ValueError):
                gate.public_reference(path,self.root)
            opened.assert_not_called()

    def test_link_admission_fails_before_content_read(self):
        with patch.object(Path,'is_symlink',return_value=True),patch.object(Path,'open') as opened:
            with self.assertRaises(ValueError):gate.public_reference('public.txt',self.root)
        opened.assert_not_called()

    def test_a_directory_or_missing_file_is_never_a_valid_implementation(self):
        (self.root/'directory').mkdir()
        with self.assertRaises(ValueError):gate.public_reference('directory',self.root)
        with self.assertRaises(OSError):gate.public_reference('missing.txt',self.root)

    def test_unstable_content_metadata_cannot_pass_hash_audit(self):
        real=Path.stat;phase={'read':False};original_hash=gate.hashlib.sha256
        class HashRead:
            def __init__(self):self.inner=original_hash()
            def update(self,data):self.inner.update(data);phase['read']=True
            def hexdigest(self):return self.inner.hexdigest()
        def stat(path,*args,**kwargs):
            value=real(path,*args,**kwargs)
            if path==self.file:
                return SimpleNamespace(st_size=value.st_size,st_mode=value.st_mode,
                                       st_mtime_ns=value.st_mtime_ns+(1 if phase['read'] else 0))
            return value
        with patch.object(Path,'stat',stat),patch.object(gate.hashlib,'sha256',side_effect=HashRead),self.assertRaises(ValueError):
            gate.public_reference('public.txt',self.root)

    def test_existing_template_reference_uses_metadata_only_and_never_opens_dotenv(self):
        real=Path.open
        def opened(path,*args,**kwargs):
            if path.name.startswith('.env'):
                raise AssertionError('dotenv content must never be opened')
            return real(path,*args,**kwargs)
        with patch.object(Path,'open',opened):
            result=gate.inventory_reference('backend/laravel/.env.example')
        self.assertIsNone(result['sha256'])
        self.assertIn('METADATA_ONLY',result['qualification'])

    def test_duplicate_or_malformed_csv_header_and_cardinality_are_refused(self):
        path=self.root/'public.csv'
        for text in ('a,a\n1,2\n','a,b\n1\n','a,b\n1,2,3\n','\n'):
            path.write_text(text,encoding='utf-8')
            with patch.object(gate,'ROOT',self.root),self.subTest(text=text),self.assertRaises(ValueError):
                gate.rows('public.csv')

    def test_duplicate_case_rows_cannot_silently_shadow_existing_results(self):
        real=gate.rows
        for target in ('docs/testing/formal-scenario-status.csv','docs/testing/supplemental-verification-plan.csv'):
            def records(path):
                fields,rows=real(path)
                return fields,rows+[rows[0].copy()] if path==target else rows
            with self.subTest(target=target),patch.object(gate,'rows',side_effect=records), \
                 redirect_stdout(io.StringIO()),self.assertRaises(ValueError):gate.check()

    def test_fabricated_requirement_verified_assessment_remains_refused(self):
        real=gate.rows
        def records(path):
            fields,rows=real(path)
            if path=='docs/testing/living-requirement-status.csv':rows[0]['implementation_assessment']='VERIFIED'
            return fields,rows
        with patch.object(gate,'rows',side_effect=records),redirect_stdout(io.StringIO()),self.assertRaises(ValueError):
            gate.check()

    def test_missing_definition_unknown_class_or_wrong_lead_requirement_fail(self):
        real=gate.rows
        for field,value in (('expected_result',''),('verification_type','unreviewed'),('requirement_id','SYS-002')):
            def records(path):
                fields,rows=real(path)
                if path=='docs/testing/supplemental-verification-plan.csv':rows[0][field]=value
                return fields,rows
            with self.subTest(field=field),patch.object(gate,'rows',side_effect=records), \
                 redirect_stdout(io.StringIO()),self.assertRaises(ValueError):gate.check()
        original=Path.read_text
        def text(path,*args,**kwargs):
            if path==gate.ROOT/'docs/testing/verification-simulation-plan.md':return 'No scenario definitions'
            return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',text),redirect_stdout(io.StringIO()),self.assertRaises(ValueError):
            gate.check()

    def test_actual38_inventory_preserves_unperformed_case_statuses(self):
        with redirect_stdout(io.StringIO()):result=gate.check()
        self.assertEqual(len(result['requirements']),38)
        self.assertEqual(len({test['test_id'] for row in result['requirements'] for test in row['tests']}),34)
        self.assertEqual(result['requirement_approval'],'NOT_APPROVED')
        self.assertFalse(result['database_access'])
        self.assertFalse(result['hardware_verification'])
        # Current references must all be public source, including the actual
        # external-key loader. The dedicated template test still proves that
        # an explicitly inventoried dotenv template is metadata-only.
        self.assertTrue(all(x['sha256'] is not None for x in result['public_files'].values()))
        security=next(x for x in result['requirements'] if x['requirement_id']=='SEC-002')
        self.assertIn('backend/laravel/config/app.php',security['implementation_paths'])
        self.assertNotIn('backend/laravel/.env.example',security['implementation_paths'])

    def test_report_creation_refuses_existing_and_foreign_targets(self):
        folder=self.root/'evidence/test-results';folder.mkdir(parents=True)
        output=folder/'audit-test.json'
        with patch.object(gate,'ROOT',self.root):
            gate.save_report(output,{'synthetic':True})
            original=output.read_bytes()
            with self.assertRaises(ValueError):gate.save_report(output,{'synthetic':False})
            with self.assertRaises(ValueError):gate.save_report(self.root/'outside.json',{})
            with self.assertRaises(ValueError):gate.save_report(folder/'secrets.json',{})
        self.assertEqual(output.read_bytes(),original)
        self.assertEqual(set(folder.iterdir()),{output})


if __name__=='__main__':
    unittest.main()
