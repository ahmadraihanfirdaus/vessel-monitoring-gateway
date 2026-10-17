#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

import test_public_archive as target


class MachineLocalPathScannerTests(unittest.TestCase):
    def test_windows_backslash_path_detected(self) -> None:
        data = b'\\'.join([b'C:', b'Users', b'synthetic-fixture-user', b'Downloads', b'artifact.zip'])
        self.assertTrue(target.machine_local_user_path_hits(data))

    def test_windows_forward_slash_path_detected(self) -> None:
        data = b'/'.join([b'C:', b'Users', b'synthetic-fixture-user', b'Downloads', b'artifact.zip'])
        self.assertTrue(target.machine_local_user_path_hits(data))

    def test_git_bash_path_detected(self) -> None:
        data = b'/'.join([b'', b'c', b'Users', b'synthetic-fixture-user', b'Downloads', b'artifact.zip'])
        self.assertTrue(target.machine_local_user_path_hits(data))

    def test_placeholder_is_not_a_concrete_leak(self) -> None:
        data = b"/c/Users/<user>/Downloads/artifact.zip"
        self.assertEqual(target.machine_local_user_path_hits(data), [])

    def test_scanner_does_not_match_its_own_source(self) -> None:
        source = Path(target.__file__).read_bytes()
        self.assertEqual(target.machine_local_user_path_hits(source), [])


if __name__ == "__main__":
    unittest.main()
