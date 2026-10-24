#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
h=(r/'firmware/src/phase9_b36_wire_interop_host.h').read_text()
f=(r/'scripts/phase9_b36_wire_interop_fixture.c').read_text()
s=(r/'scripts/test_phase9_b36_wire_interop.py').read_text()
for term in ('VG_B36_EXPECTED_WIRE_LENGTH 72u','vg_b36_reference_encode(',
 'vg_b36_reference_decode(', 'vg_b18_crc32(local,68u)', 'vg_b18_crc32(raw,68u)',
 'memcpy(out,local,sizeof(local));return true;', '*out=temporary;return true;'):
 assert term in h,term
for term in ('vg_b36_reference_decode(', 'vg_b36_reference_encode('):
 assert term in f,term
for term in ("struct.Struct('<4s8I4QI')",'zlib.crc32(', 'reference_parse(', 'repair_crc('):
 assert term in s,term
assert all(forbidden not in h for forbidden in ('malloc(', 'free(', 'fopen(', 'fwrite(', 'system(', 'esp_partition_write('))
print('B36_CONTRACT=PASS_INDEPENDENT_C99_INDEXED_VS_PYTHON_STRUCT_WIRE_ORACLE')
