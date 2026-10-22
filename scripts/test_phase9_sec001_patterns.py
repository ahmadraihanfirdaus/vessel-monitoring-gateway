#!/usr/bin/env python3
"""SEC-001 pattern detection regression, not a complete secret scanner."""
import unittest
from phase9_sec001_source_patterns import classify
class SecretPatterns(unittest.TestCase):
 def test_private_key(self):self.assertIn('PRIVATE_KEY_BEGIN',classify(b'-----BEGIN '+b'PRIVATE KEY-----'))
 def test_aws_key(self):self.assertIn('AWS_ACCESS_KEY',classify(b'AKIA'+b'A'*16))
 def test_github_token(self):self.assertIn('GITHUB_CLASSIC_TOKEN',classify(b'ghp_'+b'A'*28))
 def test_public_example_not_secret(self):self.assertEqual(classify(b'APP_ENV=testing\nDB_HOST=127.0.0.1'),[])
 def test_no_raw_secret_in_report(self):
  for name in classify(b'github_pat_'+b'B'*40):self.assertTrue(name.startswith('GITHUB'))
if __name__=='__main__':unittest.main(verbosity=2)
