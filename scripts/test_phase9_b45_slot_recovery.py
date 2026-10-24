#!/usr/bin/env python3
"""Independent HMAC/struct oracle for B45 C99 two-slot selection, host-only."""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B45_GCC_REQUIRED'
DOMAIN=b'VG_PHASE9_B44_LEDGER_SNAPSHOT_HMAC_V1\x00'
HEADER=struct.Struct('<4sIQQII')
KEY=secrets.token_bytes(32)
N0=bytes.fromhex('11'*16)
N1=bytes.fromhex('22'*16)
N2=bytes.fromhex('33'*16)
assert HEADER.size==32

def seal(generation,nonces,count,*,source=777,key=KEY,magic=b'VG44'):
    assert len(nonces)==128
    body=HEADER.pack(magic,1,generation,source,count,0)+nonces
    return body+hmac.new(key,DOMAIN+body,hashlib.sha256).digest()

def validate(snapshot,key=KEY,*,floor=1,source=777):
    if snapshot is None or len(snapshot)!=192:return None
    body,tag=snapshot[:160],snapshot[160:]
    if not hmac.compare_digest(hmac.new(key,DOMAIN+body,hashlib.sha256).digest(),tag):return None
    magic,version,gen,src,count,reserved=HEADER.unpack(body[:32])
    nonces=body[32:160]
    if (magic!=b'VG44' or version!=1 or gen<floor or src!=source or not count<=8 or reserved!=0):return None
    active=[nonces[i*16:(i+1)*16] for i in range(count)]
    if any(not any(n) for n in active) or len(set(active))!=len(active):return None
    if any(nonces[count*16:]):return None
    return gen,count,nonces

def oracle(a,b,*,floor=1,source=777,key=KEY):
    # Malformed present slot length is an API error, not a valid empty slot.
    if floor==0 or source==0 or len(key)!=32:return None
    if (a is not None and len(a)!=192) or (b is not None and len(b)!=192):return None
    x=validate(a,key,floor=floor,source=source)
    y=validate(b,key,floor=floor,source=source)
    if x is None and y is None:return None
    if x is not None and y is not None and x[0]==y[0] and a!=b:return None
    idx=0 if x is not None and (y is None or x[0]>=y[0]) else 1
    gen,count,nonces=x if idx==0 else y
    return bytes([idx])+struct.pack('<QI',gen,count)+nonces

with tempfile.TemporaryDirectory(prefix='vg_b45_') as td:
    d=Path(td);exe=d/('b45.exe' if os.name=='nt' else 'b45')
    cp=subprocess.run([CC,'-std=c99','-pedantic','-Wall','-Wextra','-Werror',
        '-Ifirmware/src','scripts/phase9_b45_slot_recovery_fixture.c','-o',str(exe)],
        cwd=ROOT,capture_output=True,text=True,timeout=90)
    assert cp.returncode==0,cp.stderr
    cp=subprocess.run([str(exe),'selftest'],cwd=ROOT,capture_output=True,text=True,timeout=60)
    assert cp.returncode==0,(cp.stdout,cp.stderr)
    assert 'B45_ALIAS_LENGTH_IMMUTABLE=PASS' in cp.stdout
    cases=[]
    def check(name,a,b,*,floor=1,source=777,key=KEY):
        index=len(cases);keyfile=d/f'key_{index}.bin';keyfile.write_bytes(key)
        pa=d/f'slot0_{index}.bin';pb=d/f'slot1_{index}.bin'
        if a is not None:pa.write_bytes(a)
        if b is not None:pb.write_bytes(b)
        outfile=d/f'result_{index}.bin'
        sentinel=(b'UNCHANGED_OUTPUT_WHEN_DENIED_'+bytes([index%255]))
        outfile.write_bytes(sentinel)
        r=subprocess.run([str(exe),str(pa) if a is not None else '-',
            str(pb) if b is not None else '-',str(keyfile),str(outfile),
            str(floor),str(source)],cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert r.returncode==0,(name,r.returncode,r.stdout,r.stderr)
        expected=oracle(a,b,floor=floor,source=source,key=key)
        if expected is None:
            assert r.stdout.strip()=='B45_SELECT_DENIED_UNCHANGED_TEST_ONLY',(name,r.stdout)
            assert outfile.read_bytes()==sentinel,name
        else:
            assert outfile.read_bytes()==expected,(name,'oracle mismatch')
            idx=expected[0];gen=struct.unpack('<Q',expected[1:9])[0]
            assert r.stdout.strip()==f'B45_SELECT_ACCEPT_SLOT_{idx}_GEN_{gen}_TEST_ONLY',name
        cases.append(name)
    empty=bytes(128);one=N0+bytes(112);two=N0+N1+bytes(96);three=N0+N1+N2+bytes(80)
    old=seal(11,empty,0);mid=seal(12,one,1);new=seal(14,two,2);latest=seal(17,three,3)
    check('newer_slot1',old,mid)
    check('newer_slot0',new,old)
    check('only_slot0',mid,None)
    check('only_slot1',None,latest)
    check('duplicate_exact',mid,mid)
    check('one_corrupt_slot0',bytes([mid[0]^1])+mid[1:],new)
    check('one_corrupt_slot1',old,new[:-1]+bytes([new[-1]^1]))
    check('equal_generation_conflicting_authenticated',mid,seal(12,two,2))
    check('same_generation_source_rewritten',mid,seal(12,one,1,source=778))
    check('both_missing',None,None)
    check('both_corrupt',b'!'*192,b'?'*192)
    check('floor_reject_both',mid,new,floor=15)
    check('floor_accept_only_new',mid,new,floor=14)
    check('wrong_source',mid,new,source=778)
    check('wrong_key',mid,new,key=secrets.token_bytes(32))
    check('bad_len0',mid[:191],new)
    check('bad_len1',mid,new[:150])
    check('too_long',mid,new+b'!')
    check('empty_bytes_slot0',b'',new)
    check('bad_b44_magic_authenticated',seal(11,empty,0,magic=b'NOPE'),None)
    check('source_mismatch_one',seal(11,empty,0,source=999),mid)
    check('samegen_conflict_count_zero',old,seal(11,one,1))
    check('floor_zero',new,mid,floor=0)
    check('source_zero',mid,new,source=0)
    for j in range(24):
        altered=bytearray(latest);pos=(j*7+3)%192;altered[pos]^=1<<(j%8)
        check(f'single_bit_{j}',old,bytes(altered),floor=13)
    for i in range(5):
        # A high generation without the test key cannot displace valid state.
        invalid=seal(400+i,three,3,key=secrets.token_bytes(32))
        check(f'unauthenticated_high_{i}',mid,invalid)
    assert len(set(cases))==len(cases)
print(f'B45_TWO_SLOT_ORACLE=PASS_{len(cases)}_CROSS_PROCESS_CASES_NO_DB')
print('B45_CRASH_ATOMIC_DISK_NVS_TRUSTED_FLOOR_CONCURRENT_CAS=NOT_VERIFIED')
