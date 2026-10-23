#!/usr/bin/env python3
"""Strict host-only Laravel JSON receipt -> B16 C99 ACK reconciliation. No TLS/DB claims."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ORDER = [
 ('telemetry_created','/api/v1/telemetry',201,'result','created',1,True),
 ('telemetry_identical','/api/v1/telemetry',200,'result','identical_duplicate',2,True),
 ('telemetry_conflict','/api/v1/telemetry',409,'error','conflicting_duplicate',5,False),
 ('event_created','/api/v1/events',201,'result','event_persisted',3,True),
 ('event_identical','/api/v1/events',200,'result','identical_event_duplicate',4,True),
 ('event_conflict','/api/v1/events',409,'error','conflicting_event_duplicate',5,False),
 ('unauthorized','/api/v1/telemetry',401,'error','invalid_device_authentication',7,False),
 ('dependency_unavailable','/api/v1/events',503,'error','backend_temporarily_unavailable',6,False),
]

def strict_json(raw):
    def pairs(seq):
        result = {}
        for key, value in seq:
            if key in result: raise ValueError('duplicate_json_key')
            result[key] = value
        return result
    def bad_constant(value): raise ValueError('json_constant_'+value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)

def verify_records(data):
    if len(data)>8192: raise ValueError('evidence_oversized')
    if not data.endswith(b'\n') or b'\r' in data: raise ValueError('jsonl_newline_invalid')
    lines=data.splitlines()
    if len(lines)!=8: raise ValueError('case_count_invalid')
    rows=[]
    for idx,(line,expected) in enumerate(zip(lines,ORDER),1):
        if len(line)>1024: raise ValueError('row_oversized')
        row=strict_json(line.decode('utf-8','strict'))
        if not isinstance(row,dict) or set(row)!={'case','route','status','body_json','origin_verified'}:
            raise ValueError('outer_schema_invalid')
        name,route,status,key,value,tag,eligible=expected
        if (row['case']!=name or row['route']!=route or type(row['status']) is not int
            or row['status']!=status or row['origin_verified'] is not False):
            raise ValueError('unexpected_case_status_or_origin')
        body=row['body_json']
        if not isinstance(body,str) or len(body.encode())>512: raise ValueError('body_invalid_size')
        doc=strict_json(body)
        if not isinstance(doc,dict) or doc.get(key)!=value:raise ValueError('unrecognized_application_result')
        keys={key,'sample_id'} if name.startswith('telemetry_') else {key}
        if set(doc) != keys: raise ValueError('response_shape_invalid')
        if name.startswith('telemetry_') and (type(doc['sample_id']) is not int or doc['sample_id']!=17):
            raise ValueError('sample_identity_invalid')
        rows.append((status,tag,idx,100+idx,int(eligible)))
    return rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True)
    parser.add_argument('--evidence-dir',required=True)
    args=parser.parse_args()
    inp=Path(args.input).resolve(strict=True)
    outdir=Path(args.evidence_dir).resolve(strict=True)
    data=inp.read_bytes()
    rows=verify_records(data)
    root=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='vg-b17-') as directory:
        binary=Path(directory)/('receipt.exe' if os.name=='nt' else 'receipt')
        fixture=Path(directory)/'receipts.tsv'
        fixture.write_text(''.join('|'.join(map(str,row))+'\n' for row in rows),encoding='ascii')
        cc=os.getenv('CC') or 'gcc'
        result=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
          '-I',str(root/'firmware/src'),str(root/'scripts/phase9_b17_receipt_policy_fixture.c'),
          '-o',str(binary)],cwd=root,capture_output=True,text=True,timeout=60)
        if result.returncode:raise RuntimeError('B17_GCC_'+result.stderr[:400])
        run=subprocess.run([str(binary),str(fixture)],cwd=root,capture_output=True,timeout=25)
        if run.returncode!=0 or run.stderr or run.stdout.decode('ascii','strict').strip()!='B17_ACK=PASS_8_CASES_4_ACCEPT_4_HOLD':
            raise RuntimeError('B17_C99_FAILED_'+repr((run.returncode,run.stdout,run.stderr)))
    h=hashlib.sha256(data).hexdigest()
    (outdir/'b17-receipt-summary.json').write_text(json.dumps({
      'scope':'host_only', 'jsonl_sha256':h, 'receipts':len(rows), 'eligible_if_externally_verified':4,
      'held':4,'tls_evidence':'NOT_RUN','database_access':'NONE_INTENDED'},indent=2)+'\n')
    print('B17_LARAVEL_C99_RECEIPTS=PASS_8_CASES_4_CONDITIONALLY_ELIGIBLE_4_HELD_SHA256_'+h)

if __name__=='__main__':main()
