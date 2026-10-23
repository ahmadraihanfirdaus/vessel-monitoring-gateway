#!/usr/bin/env python3
"""Narrow structural contract for B20; independent of vendor or database."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'firmware/src/phase9_b20_slot_prepare_host.h').read_text()
f=(R/'scripts/phase9_b20_slot_fixture.c').read_text()
for phrase in ('vg_b20_prepare','vg_b19_select','vg_b19_next_generation',
               'last_accepted_sequence<selected.ack.last_accepted_sequence',
               'vg_b20_verify_readback','memcmp(expected,actual,expected_n)',
               'chosen=1u; /* byte-identical equal-generation slots only */'):
    assert phrase in h, phrase
for phrase in ('"bootstrap"','"update"','"recover"','"negative"',
               '"torn"','"bitflip"','"good"','B20_RESTART=PASS_GEN_'):
    assert phrase in f,phrase
assert 'NOT crash' not in h or 'No filesystem/ESP NVS' in h
print('B20_CONTRACT=PASS_PREPARE_GUARDS_AND_READBACK')
