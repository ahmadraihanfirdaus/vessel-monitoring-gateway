#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

import test_public_archive as target


def concrete_account() -> bytes:
    # Assemble the fixture token so the test source itself does not contain
    # a concrete machine-local profile path that the archive scanner should flag.
    return b"ah" + b"mad"


def win_backslash_path() -> bytes:
    return b"C:" + b"\\" + b"Users" + b"\\" + concrete_account() + b"\\" + b"Downloads" + b"\\" + b"artifact.zip"


def win_forward_path() -> bytes:
    return b"C:" + b"/" + b"Users" + b"/" + concrete_account() + b"/" + b"Downloads" + b"/" + b"artifact.zip"


def git_bash_path() -> bytes:
    return b"/" + b"c" + b"/" + b"Users" + b"/" + concrete_account() + b"/" + b"Downloads" + b"/" + b"artifact.zip"


def placeholder_path() -> bytes:
    return b"/" + b"c" + b"/" + b"Users" + b"/" + b"<user>" + b"/" + b"Downloads" + b"/" + b"artifact.zip"


class MachineLocalPathScannerTests(unittest.TestCase):
    def test_windows_backslash_path_detected(self) -> None:
        self.assertTrue(target.machine_local_user_path_hits(win_backslash_path()))

    def test_windows_forward_slash_path_detected(self) -> None:
        self.assertTrue(target.machine_local_user_path_hits(win_forward_path()))

    def test_git_bash_path_detected(self) -> None:
        self.assertTrue(target.machine_local_user_path_hits(git_bash_path()))

    def test_placeholder_is_not_a_concrete_leak(self) -> None:
        self.assertEqual(target.machine_local_user_path_hits(placeholder_path()), [])

    def test_scanner_does_not_match_its_own_source(self) -> None:
        source = Path(target.__file__).read_bytes()
        self.assertEqual(target.machine_local_user_path_hits(source), [])

    def test_fixture_source_does_not_contain_concrete_path(self) -> None:
        source = Path(__file__).read_bytes()
        self.assertEqual(target.machine_local_user_path_hits(source), [])


if __name__ == "__main__":
    unittest.main()
