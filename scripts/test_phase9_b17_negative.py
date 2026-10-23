"""No DB: reject duplicate JSON keys, forged origin, response mutation and truncation."""
import copy
import json
from phase9_b17_receipt_crosscheck import ORDER, verify_records

def make_rows():
    rows=[]
    for name,route,status,key,value,tag,eligible in ORDER:
        body={key:value}
        if name.startswith('telemetry_'):body['sample_id']=17
        rows.append({'case':name,'route':route,'status':status,
                     'body_json':json.dumps(body,separators=(',',':')),'origin_verified':False})
    return rows

def raw(rows):return (''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rows)).encode()
valid=make_rows()
assert len(verify_records(raw(valid)))==8
bad=[]
row=copy.deepcopy(valid);row[0]['origin_verified']=True;bad.append(raw(row))
row=copy.deepcopy(valid);row[0]['status']=200;bad.append(raw(row))
row=copy.deepcopy(valid);row[0]['body_json']='{"result":"created","result":"created","sample_id":17}';bad.append(raw(row))
row=copy.deepcopy(valid);row[0]['body_json']='{"result":"created","sample_id":17,"token":"leak"}';bad.append(raw(row))
row=copy.deepcopy(valid);row[1]['body_json']='{"result":"created","sample_id":17}';bad.append(raw(row))
row=copy.deepcopy(valid);row[2]['body_json']='{"error":"conflicting_duplicate","sample_id":0}';bad.append(raw(row))
row=copy.deepcopy(valid);row[0]['status']=True;bad.append(raw(row))
bad.append(raw(valid)[:-1])
bad.append(raw(valid)+b'\n')
for ix,payload in enumerate(bad):
    try: verify_records(payload)
    except (ValueError,UnicodeDecodeError,TypeError): pass
    else:raise AssertionError(f'negative_{ix}_accepted')
print(f'B17_NEGATIVE=PASS_{len(bad)}_REJECTED')
