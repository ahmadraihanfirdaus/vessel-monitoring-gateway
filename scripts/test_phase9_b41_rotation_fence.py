#!/usr/bin/env python3
"""B41 trust-boundary host-only oracle. Secrets are ephemeral test files."""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile,zlib
ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B41_GCC_NOT_FOUND'
WIRE=struct.Struct('<4s8I4QI')
KDF=b'VG_PHASE9_B39_SCOPE_KDF_V1\x00'
AUTH=b'VG_PHASE9_B39_SCOPE_AUTH_V1\x00'
def seal(key,kid,epoch,wire,purpose,device):
    ctx=struct.pack('<IQI',purpose,kid,device)
    derived=hmac.new(key,KDF+ctx,hashlib.sha256).digest()
    msg=struct.pack('<4sIQQ',b'VG37',1,kid,epoch)+wire
    return msg+hmac.new(derived,AUTH+ctx+msg,hashlib.sha256).digest()
with tempfile.TemporaryDirectory(prefix='vg_b41_') as td:
    d=Path(td); ext='.exe' if os.name=='nt' else ''
    c35=d/('c35'+ext);c41=d/('c41'+ext)
    for src,exe in [('phase9_b35_wire_receipt_fixture.c',c35),
                    ('phase9_b41_rotation_fence_fixture.c',c41)]:
        cmd=[CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic','-Ifirmware/src',
             'scripts/'+src,'-o',str(exe)]
        cp=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=90)
        assert cp.returncode==0,(cmd,cp.stdout,cp.stderr)
    def run(exe,*args):
        cp=subprocess.run([str(exe),*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert cp.returncode==0,(cp.stdout,cp.stderr,cp.returncode)
        return cp.stdout.strip()
    snap=d/'snap.bin';wpath=d/'wire.bin'
    assert 'PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run(c35,'stage',snap)
    assert 'PASS_CANONICAL_72_BYTES' in run(c35,'stage',snap,wpath)
    wire=wpath.read_bytes();assert len(wire)==72
    assert zlib.crc32(wire[:68])==WIRE.unpack(wire)[13]
    device=WIRE.unpack(wire)[3]
    newkey=secrets.token_bytes(32);oldkey=secrets.token_bytes(32)
    while oldkey==newkey:oldkey=secrets.token_bytes(32)
    old=seal(oldkey,101,39,wire,1,device)
    new=seal(newkey,202,40,wire,1,device)
    publish=seal(newkey,202,40,wire,2,device)
    cases=[]
    def add(name,expected,key=newkey,receipt=new,purpose=1,tag=device,
            before='post',after='post',rev0=12,rev1=12,floor=11,source=777,alias='none'):
        cases.append((name,expected,key,receipt,purpose,tag,before,after,rev0,rev1,floor,source,alias))
    add('post_valid',True)
    add('pre_valid',True,oldkey,old,before='pre',after='pre')
    add('publish_valid',True,receipt=publish,purpose=2)
    add('old_after_cutover',False,oldkey,old)
    add('key_mismatch',False,oldkey,new)
    add('wrong_key',False,secrets.token_bytes(32))
    add('wrong_policy_before',False,before='pre')
    add('wrong_policy_after',False,after='pre')
    add('retired_policy_before',False,before='retired')
    add('retired_policy_after',False,after='retired')
    add('future_policy',False,before='future',after='future')
    add('epoch_floor',False,before='floor',after='floor')
    add('before_wrong_purpose',False,before='badpurpose')
    add('after_wrong_purpose',False,after='badpurpose')
    add('before_wrong_device',False,before='baddevice')
    add('after_wrong_device',False,after='baddevice')
    add('wrong_before_source',False,before='badsource')
    add('wrong_after_source',False,after='badsource')
    add('wrong_source_expectation',False,source=778)
    add('zero_source',False,source=0)
    add('zero_revision',False,rev0=0,rev1=0)
    add('new_revision',False,rev1=13)
    add('old_revision',False,rev1=11)
    add('floor_equal',False,floor=12)
    add('floor_greater',False,floor=13)
    add('floor_max',False,floor=(1<<64)-1)
    add('wrong_purpose',False,purpose=2)
    add('wrong_device',False,tag=device+1)
    add('zero_device',False,tag=0)
    add('retired_signer_active',False,oldkey,old,before='post',after='post')
    add('publish_receipt_as_restore',False,receipt=publish)
    add('restore_receipt_as_publish',False,receipt=new,purpose=2)
    add('mac_zero',False,receipt=new[:96]+bytes(32))
    add('mac_random',False,receipt=new[:96]+secrets.token_bytes(32))
    add('bad_magic',False,receipt=b'NOPE'+new[4:])
    add('bad_epoch',False,receipt=new[:16]+(41).to_bytes(8,'little')+new[24:])
    add('bad_key_id',False,receipt=new[:8]+(303).to_bytes(8,'little')+new[16:])
    add('bad_version',False,receipt=new[:4]+bytes(4)+new[8:])
    add('corrupt_mac_first',False,receipt=bytes([new[0]^1])+new[1:])
    add('alias_output_before',False,alias='alias')
    add('policy_zero_key',False,before='zerokey',after='zerokey')
    for offset in (96,97,103,111,119,126,127):
        bad=bytearray(new);bad[offset]^=0x20
        add('flipped_mac_'+str(offset),False,receipt=bytes(bad))
    for offset in (24,40,63,95):
        bad=bytearray(new);bad[offset]^=0x80
        add('flipped_wire_'+str(offset),False,receipt=bytes(bad))
    assert len(cases)==52,len(cases)
    passed=0
    for i,(name,expect,key,receipt,purpose,tag,pre,post,r0,r1,floor,source,alias) in enumerate(cases):
        k=d/f'k{i}.bin';r=d/f'r{i}.bin';k.write_bytes(key);r.write_bytes(receipt)
        result=run(c41,k,r,wpath,purpose,tag,pre,post,r0,r1,floor,source,alias)
        assert result in ('B41_ROTATION_FENCE=ACCEPT_TEST_ONLY','B41_ROTATION_FENCE=DENIED_TEST_ONLY'),(name,result)
        assert (result=='B41_ROTATION_FENCE=ACCEPT_TEST_ONLY')==expect,(name,result,expect)
        passed+=1
assert passed==52
print('B41_ROTATION_FENCE=PASS_52_CASES_3_ACCEPT_49_DENY_NO_DB')
print('B41_EXTERNAL_TRUSTED_REVISION_ATOMIC_CAS_ESP32=NOT_VERIFIED')
