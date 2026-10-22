#!/usr/bin/env python3
"""Static source/test presence map. This does NOT close TST-001/SUP017."""
import csv,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((repo/'docs/testing/phase9-b4-scoped-trace.csv').open(newline='',encoding='utf-8')))
assert len(rows)==5 and len({r['requirement'] for r in rows})==5
for r in rows:
 assert r['status']=='FORMAL_OPEN'
 assert r['source'].startswith(('firmware/','backend/','scripts/'))
 assert r['test'].startswith('scripts/test_phase9_b4_')
 assert (repo/r['source']).is_file() and (repo/r['test']).is_file()
print('B4_SCOPED_TRACE_INVENTORY=PASS_5_FORMAL_OPEN')
