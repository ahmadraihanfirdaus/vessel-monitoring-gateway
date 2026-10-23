#!/usr/bin/env python3
"""Compile original C99 journal header; store raw newline-preserving JSONL for Laravel tests."""
import argparse, hashlib, json, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def build_bytes():
    with tempfile.TemporaryDirectory(prefix='vg-b15-event-') as folder:
        binary=Path(folder)/('events.exe' if os.name=='nt' else 'events')
        cmd=[os.getenv('CC','gcc'),'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
            '-I',str(ROOT/'firmware/src'),str(ROOT/'scripts/phase9_b15_event_wire_fixture.c'),
            '-o',str(binary)]
        comp=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=60)
        if comp.returncode:raise RuntimeError('C99_COMPILE_ERROR: '+comp.stderr[:1000])
        run=subprocess.run([str(binary)],cwd=ROOT,capture_output=True,timeout=20)
        if run.returncode or run.stderr:raise RuntimeError('C99_RUNTIME_ERROR_'+str(run.returncode))
        return run.stdout

def validate(raw):
    assert 0<len(raw)<=8192 and raw.endswith(b'\n')
    count=raw.count(b'\n');crlfs=raw.count(b'\r\n')
    assert crlfs in (0,count) and b'\r' not in raw.replace(b'\r\n',b'')
    lines=raw.splitlines();assert len(lines)==4
    types=['alarm_raised','alarm_ack','alarm_cleared','fault']
    fields={'schema_version','device_id','boot_id','event_id','linked_alarm_id',
            'source_id','source_mode','event_type','occurred_at_ms'}
    for i,line in enumerate(lines):
        assert len(line)<=4096
        data=json.loads(line)
        assert set(data)==fields
        assert data['schema_version']=='1.0' and data['device_id']=='b15-demo-device'
        assert data['boot_id']=='b15-boot' and data['event_id']==i+1
        assert data['linked_alarm_id']==7 and data['source_id']==i+1
        assert data['source_mode']==('bench_test' if i==2 else 'simulation')
        assert data['event_type']==types[i] and data['occurred_at_ms']==100+i
    return hashlib.sha256(raw).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    path=Path(parser.parse_args().output).resolve()
    assert path.parent.is_dir() and not path.exists() and not path.is_symlink()
    raw=build_bytes();h=validate(raw)
    with path.open('xb') as stream:stream.write(raw)
    assert path.read_bytes()==raw
    print('B15_C99_EVENTS=PASS_4_CASES_SHA256_'+h)
if __name__=='__main__':main()
