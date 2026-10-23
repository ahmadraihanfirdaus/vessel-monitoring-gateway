#!/usr/bin/env python3
"""B18 source shape and host-only contract; no runtime persistence claim."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b18_checkpoint_host.h').read_text(encoding='utf-8')
f=(r/'scripts/phase9_b18_checkpoint_fixture.c').read_text(encoding='utf-8')
for token in ('vg_b18_pack(', 'vg_b18_unpack(', 'vg_b18_crc32(',
              'expected_device','vg_b18_valid(', 'vg_b18_r32(',
              'reset_ack.last_accepted_sequence=highwater;', 'NET002_HOST_JOURNAL_CAP',
              'NOT crash-durable','*out=temp;', '*ack=reset_ack;'):
    assert token in h,token
for token in ('"save"','"restore"','"negative"','critical-','evicted_count!=2u',
              'a.pending','vg_b18_unpack'):
    assert token in f,token
assert 'esp_partition' not in h and 'nvs_' not in h
assert 'system(' not in f and 'popen(' not in f
print('B18_CONTRACT=PASS_HOST_BOUNDARY_INTEGRITY_RESTART_NOT_HARDWARE')
