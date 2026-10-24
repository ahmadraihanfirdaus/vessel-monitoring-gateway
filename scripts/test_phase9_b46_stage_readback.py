#!/usr/bin/env python3
"""Independent Python oracle for host-only authenticated inactive-slot admission."""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc');assert CC,'B46_GCC_REQUIRED'
DOMAIN=b'VG_PHASE9_B44_LEDGER_SNAPSHOT_HMAC_V1\x00'
HEAD=struct.Struct('<4sIQQII')
KEY=secrets.token_bytes(32)
A=bytes([0x11])*16;B=bytes([0x22])*16;C=bytes([0x33])*16
NONCES=[A,B,C]
def seal(gen,used=(),*,source=777,key=KEY,magic=b'VG44'):
    assert 0<=len(used)<=8 and all(len(x)==16 for x in used)
    body=HEAD.pack(magic,1,gen,source,len(used),0)+b''.join(used)+bytes(128-16*len(used))
    assert len(body)==160
    return body+hmac.new(key,DOMAIN+body,hashlib.sha256).digest()
def restored(image,key=KEY,*,floor=1,source=777):
    if image is None or len(image)!=192:return None
    body,mac=image[:160],image[160:]
    if not hmac.compare_digest(hmac.new(key,DOMAIN+body,hashlib.sha256).digest(),mac):return None
    magic,ver,gen,src,count,reserved=HEAD.unpack(body[:32]);used=body[32:]
    if magic!=b'VG44' or ver!=1 or gen<floor or src!=source or count>8 or reserved:return None
    present=[used[i*16:(i+1)*16] for i in range(count)]
    if len(set(present))!=len(present) or any(not any(x) for x in present) or any(used[count*16:]):return None
    return gen,present
def two_slot(a,b,*,key=KEY,floor=1,source=777):
    if a is not None and len(a)!=192:return None
    if b is not None and len(b)!=192:return None
    v=[restored(a,key,floor=floor,source=source),restored(b,key,floor=floor,source=source)]
    if not any(x is not None for x in v):return None
    if all(x is not None for x in v) and v[0][0]==v[1][0] and a!=b:return None
    i=0 if v[0] is not None and (v[1] is None or v[0][0]>=v[1][0]) else 1
    return i,v[i]
def oracle(a,b,stage,readback,*,key=KEY,floor=1,source=777):
    if not floor or not source or len(key)!=32:return None
    if stage is None or readback is None or len(stage)!=192 or len(readback)!=192:return None
    chosen=two_slot(a,b,key=key,floor=floor,source=source)
    if chosen is None:return None
    oldslot,(oldgen,oldused)=chosen
    if oldgen==2**64-1 or len(oldused)>=8:return None
    proposed=restored(stage,key,floor=floor,source=source)
    if proposed is None:return None
    newgen,newused=proposed
    if newgen!=oldgen+1 or len(newused)!=len(oldused)+1 or newused[:-1]!=oldused:return None
    if stage!=readback:return None
    newslots=(a,readback) if oldslot==0 else (readback,b)
    final=two_slot(*newslots,key=key,floor=floor,source=source)
    if final is None or final[0]!=1-oldslot or final[1]!=proposed:return None
    return bytes([1-oldslot])+struct.pack('<QI',newgen,len(newused))+b''.join(newused)+bytes(128-16*len(newused))
with tempfile.TemporaryDirectory(prefix='vg_b46_') as tmp:
    d=Path(tmp);exe=d/('b46.exe' if os.name=='nt' else 'b46')
    cp=subprocess.run([CC,'-std=c99','-pedantic','-Wall','-Wextra','-Werror',
        '-Ifirmware/src','scripts/phase9_b46_stage_readback_fixture.c','-o',str(exe)],
        cwd=ROOT,capture_output=True,text=True,timeout=90)
    assert cp.returncode==0,cp.stderr
    cp=subprocess.run([str(exe),'selftest'],cwd=ROOT,capture_output=True,text=True,timeout=40)
    assert cp.returncode==0,(cp.stdout,cp.stderr)
    assert 'B46_ALIAS_FAIL_CLOSED_NO_OUTPUT_ON_DENY=PASS' in cp.stdout
    cases=[]
    def check(name,a,b,stage,readback,*,floor=1,source=777,key=KEY):
        i=len(cases);files=[]
        for j,data in enumerate((a,b,stage,readback)):
            f=d/f'{i}_{j}.bin'
            if data is None:files.append('-')
            else:f.write_bytes(data);files.append(str(f))
        keyfile=d/f'k_{i}.bin';keyfile.write_bytes(key)
        result=d/f'res_{i}.bin';sentinel=b'NO_WRITE_ON_DENIAL_'+bytes([i%255]);result.write_bytes(sentinel)
        cp=subprocess.run([str(exe),*files,str(keyfile),str(result),str(floor),str(source)],
            cwd=ROOT,capture_output=True,text=True,timeout=40)
        assert cp.returncode==0,(name,cp.stdout,cp.stderr)
        ref=oracle(a,b,stage,readback,key=key,floor=floor,source=source)
        if ref is None:
            assert cp.stdout.strip()=='B46_DENY_OUTPUT_UNCHANGED_HOST_ONLY',(name,cp.stdout)
            assert result.read_bytes()==sentinel,name
        else:
            assert result.read_bytes()==ref,(name,cp.stdout,'independent oracle mismatch')
            gen=struct.unpack('<Q',ref[1:9])[0]
            assert cp.stdout.strip()==f'B46_ACCEPT_INACTIVE_SLOT_{ref[0]}_GEN_{gen}_HOST_ONLY',name
        cases.append(name)
    old=seal(20);first=seal(21,[A]);second=seal(22,[A,B]);third=seal(23,[A,B,C])
    check('accept_inactive_slot1',old,None,first,first)
    check('accept_inactive_slot0',None,first,second,second)
    check('accept_overwrite_older_slot0',old,first,second,second)
    check('accept_overwrite_older_slot1',second,first,third,third)
    check('deny_stale_same_generation',old,None,old,old)
    check('deny_generational_jump',old,None,second,second)
    check('deny_old_slot_missing',None,None,first,first)
    check('deny_stage_missing',old,None,None,None)
    check('deny_readback_missing',old,None,first,None)
    check('deny_stage_short',old,None,first[:191],first)
    check('deny_readback_short',old,None,first,first[:191])
    check('deny_stage_extended',old,None,first+b'X',first)
    check('deny_stage_crc_bitflip',old,None,first[:29]+b'\x01'+first[30:],first)
    check('deny_readback_other_valid',old,None,first,seal(21,[B]))
    check('deny_wrong_nonce_sequence',first,None,seal(22,[B,C]),seal(22,[B,C]))
    check('deny_new_nonce_duplicate',first,None,seal(22,[A,A]),seal(22,[A,A]))
    check('deny_no_new_nonce',first,None,seal(22,[A]),seal(22,[A]))
    check('deny_two_new_nonce',old,None,second,second)
    check('deny_source_mismatch',old,None,seal(21,[A],source=999),seal(21,[A],source=999))
    check('deny_wrong_key',old,None,first,first,key=secrets.token_bytes(32))
    check('deny_floor_roll_back',old,None,first,first,floor=21)
    check('deny_floor_zero',old,None,first,first,floor=0)
    check('deny_source_zero',old,None,first,first,source=0)
    check('deny_split_brain_current',first,seal(21,[B]),second,second)
    check('deny_both_invalid_current',b'X'*192,b'Y'*192,first,first)
    check('deny_invalid_slot_len',old[:191],first,second,second)
    check('deny_generation_overflow',seal(2**64-1),None,first,first)
    check('deny_stage_invalid_magic_authenticated',old,None,seal(21,[A],magic=b'BOOM'),seal(21,[A],magic=b'BOOM'))
    # Fault cuts in independent readback bytes; no prior nonce published on any denial.
    for k in range(48):
        offset=(k*37+17)%192
        partial=bytearray(first);partial[offset]^=1<<(k%8)
        check(f'cut_bit_{k:02d}',old,None,first,bytes(partial))
    for k in range(7):
        check(f'cut_truncate_{k}',old,None,first,first[:k*31])
    assert len(set(cases))==len(cases)
    accepts=sum(oracle(a,b,s,r) is not None for a,b,s,r in [(old,None,first,first),(None,first,second,second),(old,first,second,second),(second,first,third,third)])
    assert accepts==4
print(f'B46_STAGE_READBACK=PASS_{len(cases)}_CROSS_PROCESS_CASES_4_ACCEPT_REST_DENY_NO_DB')
print('B46_TORN_WRITE_DISK_FSYNC_NVS_CONCURRENT_CAS_TRUSTED_FLOOR=NOT_VERIFIED')
