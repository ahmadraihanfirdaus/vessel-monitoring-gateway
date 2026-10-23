#!/usr/bin/env python3
"""Negative invariants ensure deliberate failure is never reported as persisted ACK."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
header=(root/'firmware/src/phase9_b18_checkpoint_host.h').read_text()
fixture=(root/'scripts/phase9_b18_checkpoint_fixture.c').read_text()
assert header.index('if (stored_crc!=vg_b18_crc32') < header.index('*out=temp;')
assert header.index('if (stored_crc!=vg_b18_crc32') < header.index('*ack=reset_ack;')
assert 'reset_ack.last_accepted_sequence=highwater' in header
assert 'phase9_b8_ack_init(&reset_ack);' in header
assert 'phase9_b8_ack_commit(&a,8u,81u,true,true,true)' in fixture
assert 'memcmp(&destination,&oldstore,sizeof(oldstore))' in fixture
assert 'CRC is not authenticity' not in fixture # articulated by tests/docs, not fabricated in C
print('B18_NEGATIVE_CONTRACT=PASS_NO_RESTORE_PARTIAL_ADVANCE')
