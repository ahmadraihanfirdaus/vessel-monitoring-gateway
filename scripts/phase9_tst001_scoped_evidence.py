#!/usr/bin/env python3
"""TST-001 scoped mapping inventory; formal evidence remains NOT_RUN."""
import csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/'docs/testing/phase9-b2-scoped-trace-map.csv'
def entries():
 with MAPPING.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
 needed={'case_id','requirement','implementation_path','test_path','formal_status'}
 if len(rows)!=5 or not all(set(x)==needed for x in rows):raise ValueError('INVALID_MAPPING_SHAPE')
 if len({x['case_id'] for x in rows})!=5:raise ValueError('DUPLICATE_CASE')
 for x in rows:
  if x['case_id']!=x['requirement'] or x['formal_status']!='NOT_RUN':raise ValueError('FORMAL_STATUS_OVERRIDE')
  for k in ('implementation_path','test_path'):
   v=Path(x[k]);p=(ROOT/v).resolve()
   if v.is_absolute() or '..' in v.parts or not p.is_relative_to(ROOT) or not p.is_file():raise ValueError('INVALID_EVIDENCE_PATH')
   x[k+'_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 return rows
if __name__=='__main__':
 rows=entries();print('TST001_SCOPED_MAPPING=PASS_5_OF_5')
 print('TST001_FORMAL_VERIFICATION=NOT_RUN')
 print('TST001_EVIDENCE_DIGEST='+hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
