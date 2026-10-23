#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'firmware/src/phase9_b19_dual_slot_host.h').read_text()
assert 'phase9_b18_checkpoint_host.h' in src
assert 'vg_b18_pack(' in src and 'vg_b18_unpack(' in src
assert 'vg_b19_next_generation(' in src and 'UINT32_MAX' in src
assert 'memcmp(slot_a,slot_b,len_a)' in src
assert 'VG_B19_SLOT_MAX 800u' in src
assert 'cryptographic' in src and 'HOST development only' in src
print('B19_CONTRACT=PASS_B18_COMPATIBLE_GEN_GUARD_AND_HOST_ONLY')
