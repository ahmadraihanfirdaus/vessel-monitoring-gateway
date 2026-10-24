#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/test_phase9_b36_wire_interop.py').read_text()
f=(r/'scripts/phase9_b36_wire_interop_fixture.c').read_text()
for term in ("cases['footer']", "cases['truncated']", "cases['trailing']",
 "cases['duplicate_domain']", "cases['zero_revision']", "cases['zero_epoch']",
 "cases['stale_ack_valid_crc']", "cases['future_generation_valid_crc']"):
 assert term in s,term
for term in ('memcmp(&candidate_fields,&before,sizeof(before))',
 'memcmp(reference,bytes,72u)', 'memcmp(reference,recoded,sizeof(recoded))'):
 assert term in f,term
print('B36_NEGATIVE=PASS_REPAIRED_CRC_MISMATCH_NOREWRITE_REFERENCE')
