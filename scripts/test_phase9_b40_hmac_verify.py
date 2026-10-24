#!/usr/bin/env python3
"""Independent Python HMAC-SHA256 oracle vs C99 host verifier; ephemeral secrets."""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile,zlib
ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B40_GCC_NOT_FOUND'
WIRE=struct.Struct('<4s8I4QI');PREFIX=struct.Struct('<4sIQQ')
assert WIRE.size==72 and PREFIX.size==24
KDF=b'VG_PHASE9_B39_SCOPE_KDF_V1\x00'
AUTH=b'VG_PHASE9_B39_SCOPE_AUTH_V1\x00'
def seal(key,kid,epoch,wire,purpose,device):
    ctx=struct.pack('<IQI',purpose,kid,device)
    scoped=hmac.new(key,KDF+ctx,hashlib.sha256).digest()
    msg=PREFIX.pack(b'VG37',1,kid,epoch)+wire
    return msg+hmac.new(scoped,AUTH+ctx+msg,hashlib.sha256).digest()
def compiler(source,output):
    cmd=[CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic','-Ifirmware/src',
         'scripts/'+source,'-o',str(output)]
    run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=90)
    assert run.returncode==0,(cmd,run.stdout,run.stderr)
with tempfile.TemporaryDirectory(prefix='b40_verify_') as td:
    d=Path(td);extension='.exe' if os.name=='nt' else ''
    c35=d/('b35'+extension);c39=d/('b39'+extension);c40=d/('b40'+extension)
    compiler('phase9_b35_wire_receipt_fixture.c',c35)
    compiler('phase9_b39_domain_scope_fixture.c',c39)
    compiler('phase9_b40_hmac_verify_fixture.c',c40)
    def run(exe,*args):
        p=subprocess.run([str(exe),*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert p.returncode==0,(args,p.returncode,p.stdout,p.stderr)
        return p.stdout.strip()
    assert run(c40,'selftest')=='B40_SHA256_HMAC_RFC4231=PASS_3_VECTORS'
    snap=d/'snapshot.bin';wirepath=d/'wire.bin'
    assert 'PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run(c35,'stage',snap)
    assert 'PASS_CANONICAL_72_BYTES' in run(c35,'stage',snap,wirepath)
    wire=wirepath.read_bytes(); assert len(wire)==72 and zlib.crc32(wire[:68])==WIRE.unpack(wire)[13]
    device=WIRE.unpack(wire)[3];assert 1<=device<0xffffffff-10
    prekey=secrets.token_bytes(32);postkey=secrets.token_bytes(32)
    while prekey==postkey:postkey=secrets.token_bytes(32)
    wrongkey=secrets.token_bytes(32)
    restore=seal(postkey,202,40,wire,1,device)
    publish=seal(postkey,202,40,wire,2,device)
    old=seal(prekey,101,39,wire,1,device)
    cases=[('restore_valid',postkey,restore,wire,1,device,'post',True),
           ('publish_valid',postkey,publish,wire,2,device,'post',True),
           ('old_pre_valid',prekey,old,wire,1,device,'pre',True)]
    def deny(name,key=postkey,blob=restore,expected_wire=wire,purpose=1,tag=device,stage='post'):
        cases.append((name,key,blob,expected_wire,purpose,tag,stage,False))
    deny('wrong_master_key',wrongkey)
    deny('retired_old_receipt',prekey,old)
    deny('active_key_wrong_id',postkey,old)
    deny('missing_key',b'')
    deny('short_key',postkey[:-1])
    deny('long_key',postkey+b'0')
    deny('zero_key',bytes(32))
    deny('cross_purpose_restore_to_publish',postkey,restore,wire,2)
    deny('cross_purpose_publish_to_restore',postkey,publish)
    deny('device_mismatch',postkey,restore,wire,1,device+1)
    deny('device_zero',postkey,restore,wire,1,0)
    deny('purpose_zero',postkey,restore,wire,0)
    deny('purpose_three',postkey,restore,wire,3)
    deny('floor_equal_epoch',postkey,restore,wire,1,device,'floor')
    deny('activation_future',postkey,restore,wire,1,device,'future')
    deny('wrong_stage',postkey,restore,wire,1,device,'pre')
    deny('unsigned_zero_mac',postkey,restore[:96]+bytes(32))
    deny('unsigned_other_mac',postkey,restore[:96]+secrets.token_bytes(32))
    deny('truncated_mac',postkey,restore[:-1])
    deny('extra_trailing_byte',postkey,restore+b'x')
    deny('truncated_wire',postkey,restore,wire[:-1])
    deny('wire_crc_corrupt',postkey,restore,wire[:-1]+bytes([wire[-1]^1]))
    deny('wrong_magic',postkey,b'NOPE'+restore[4:])
    deny('wrong_version',postkey,restore[:4]+bytes(4)+restore[8:])
    deny('wrong_key_id',postkey,restore[:8]+(303).to_bytes(8,'little')+restore[16:])
    deny('wrong_epoch',postkey,restore[:16]+(41).to_bytes(8,'little')+restore[24:])
    deny('other_device_signer',postkey,seal(postkey,202,40,wire,1,device+1))
    deny('other_purpose_signer',postkey,publish)
    deny('same_mac_wrong_wire',postkey,restore[:95]+bytes([restore[95]^1])+restore[96:])
    altered=bytearray(wire);altered[52]^=1;altered[68:72]=zlib.crc32(altered[:68]).to_bytes(4,'little')
    deny('valid_crc_changed_payload',postkey,seal(postkey,202,40,bytes(altered),1,device))
    deny('changed_expected_wire',postkey,restore,bytes(altered))
    for offset in (96,97,103,111,119,126,127):
        b=bytearray(restore);b[offset]^=0x40
        deny('mac_mutation_'+str(offset),postkey,bytes(b))
    for offset in (24,25,40,70,95):
        b=bytearray(restore);b[offset]^=0x80
        deny('wire_mutation_'+str(offset),postkey,bytes(b))
    assert len(cases)==46,len(cases)
    structural_without_mac=0
    for idx,(name,key,blob,expected_wire,purpose,tag,stage,expected) in enumerate(cases):
        k=d/f'key{idx}.bin';r=d/f'receipt{idx}.bin';w=d/f'wire{idx}.bin'
        k.write_bytes(key);r.write_bytes(blob);w.write_bytes(expected_wire)
        result=run(c40,k,r,w,purpose,tag,stage)
        actual=result=='B40_HOST_HMAC=ACCEPT_TEST_ONLY'
        assert result in ('B40_HOST_HMAC=ACCEPT_TEST_ONLY','B40_HOST_HMAC=DENIED_TEST_ONLY'),(name,result)
        assert actual is expected,(name,actual,expected)
        if (not expected and len(blob)==128 and len(expected_wire)==72 and
            purpose in (1,2) and stage in ('pre','post')):
            raw=run(c39,r,w,purpose,tag,stage)
            if raw=='B39_STRUCTURAL_ONLY=PASS_NO_AUTH':structural_without_mac+=1
        # Secrets exist only in temporary test directory, never in repo/evidence.
    assert structural_without_mac>=8,structural_without_mac
print('B40_C99_HMAC_VERIFY=PASS_46_CASES_3_ACCEPT_43_DENY_RFC4231_3_VECTORS')
print('B40_B39_STRUCTURAL_BYPASS_DETECTED_BY_C99_HMAC=VERIFIED')
print('B40_PRODUCTION_CRYPTO_KEY_STORAGE_ESP32_ATOMIC_ACK=NOT_VERIFIED')
