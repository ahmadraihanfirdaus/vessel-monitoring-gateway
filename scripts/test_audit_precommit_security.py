"""Isolated regression tests; never stage or mutate the actual project index."""

from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
