#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b35_wire_receipt_host.h').read_text()
f=(r/'scripts/phase9_b35_wire_receipt_fixture.c').read_text()
s=(r/'scripts/test_phase9_b35_wire_receipt.py').read_text()
for name in ('wrong_magic','wrong_device','wrong_ack','wrong_revision',
 'wrong_footer','truncated','trailing','null_raw','snapshot_mutation',
 'envelope_witness','alias_dest_snapshot','alias_raw_envelope',
 'encode_alias_output_snapshot','encode_wrong_snapshot'):
 assert name in f and repr(name) in s,name
assert 'memcmp(&verified,&before,sizeof(verified))!=0' in f
assert 'memcmp(output,output_before,sizeof(output))!=0' in f
assert 'memcmp(snapshot,snapshot_before,sizeof(snapshot))!=0' in f
assert 'memcmp(raw,raw_before,sizeof(raw))!=0' in f
assert 'CRC32 is not authentication' in h
print('B35_NEGATIVE=PASS_CORRUPTION_REPLAY_ALIAS_NO_OUTPUT_WRITE')
