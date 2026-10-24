#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b35_wire_receipt_host.h').read_text()
f=(r/'scripts/phase9_b35_wire_receipt_fixture.c').read_text()
for s in ('VG_B35_WIRE_LENGTH 72u','vg_b35_encode(', 'vg_b35_verify(',
 'vg_b35_project(', 'vg_b18_crc32(', 'vg_b31_overlaps(',
 'vg_b18_w32(', 'vg_b35_w64(', 'vg_b18_r32(', 'vg_b35_r64(',
 'memcpy(out,temp,sizeof(temp));*written=sizeof(temp);', '*verified=got;return true;'):
 assert s in h,s
assert h.index('vg_b35_project(e,snapshot')<h.index('memcpy(out,temp')
assert h.index('vg_b35_project(trusted,snapshot')<h.index('*verified=got')
assert 'vg_b34_finalize_envelope(' in f
assert 'stage35(' in f and 'verify35(' in f
for bad in ('malloc(', 'free(', 'fopen(', 'fwrite(', 'system(', 'esp_partition_write'):
 assert bad not in h,bad
print('B35_CONTRACT=PASS_CANONICAL_LE72_FIELD_FORMAT_AND_OUTPUT_GUARD')
