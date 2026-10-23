#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'scripts/test_phase9_b19_dual_slot.py').read_text()
assert 'expected=22' in s and 'bytes1[:-2]' in s
assert 'bytes([bytes1[25]^1])' in s
assert 'VG_GCC' in s and '-Werror' in s and 'TemporaryDirectory' in s
print('B19_NEGATIVE_POLICY=PASS_CORRUPT_TORN_BOTH_BAD_STRICT_COMPILER')
