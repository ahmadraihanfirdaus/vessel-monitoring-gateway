#!/usr/bin/env python3
"""B42 independent Python nonce-bound HMAC oracle versus C99 host verifier."""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile,zlib
ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B42_GCC_NOT_FOUND'
WIRE=struct.Struct('<4s8I4QI')
KDF=b'VG_PHASE9_B39_SCOPE_KDF_V1\x00'
AUTH=b'VG_PHASE9_B39_SCOPE_AUTH_V1\x00'
CHALLENGE=b'VG_PHASE9_B42_CHALLENGE_AUTH_V1\x00'
def seal(master,kid,epoch,wire,purpose,device):
    ctx=struct.pack('<IQI',purpose,kid,device)
    scoped=hmac.new(master,KDF+ctx,hashlib.sha256).digest()
    body=struct.pack('<4sIQQ',b'VG37',1,kid,epoch)+wire
    return body+hmac.new(scoped,AUTH+ctx+body,hashlib.sha256).digest()
def proof(master,nonce,sealed,wire,purpose,device,epoch,revision=12,source=777):
    data=nonce+sealed+wire+struct.pack('<QQIIQ',revision,source,purpose,device,epoch)
    assert len(data)==248,len(data)
    return hmac.new(master,CHALLENGE+data,hashlib.sha256).digest()
with tempfile.TemporaryDirectory(prefix='vg_b42_') as temporary:
    d=Path(temporary);ext='.exe' if os.name=='nt' else ''
    c35=d/('c35'+ext);c42=d/('c42'+ext)
    for src,exe in [('phase9_b35_wire_receipt_fixture.c',c35),
                    ('phase9_b42_challenge_bound_fixture.c',c42)]:
        cp=subprocess.run([CC,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
                           '-Ifirmware/src','scripts/'+src,'-o',str(exe)],
                          cwd=ROOT,capture_output=True,text=True,timeout=90)
        assert cp.returncode==0,(src,cp.stderr)
    def run(exe,*args):
        cp=subprocess.run([str(exe),*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert cp.returncode==0,(cp.stdout,cp.stderr,cp.returncode)
        return cp.stdout.strip()
    snap=d/'snap.bin';wire_file=d/'wire.bin'
    assert 'PASS_TWO_ROUND_CHECKPOINT_FIXTURE' in run(c35,'stage',snap)
    assert 'PASS_CANONICAL_72_BYTES' in run(c35,'stage',snap,wire_file)
    wire=wire_file.read_bytes();assert len(wire)==72
    assert zlib.crc32(wire[:68])==WIRE.unpack(wire)[13]
    device=WIRE.unpack(wire)[3]
    new_master=secrets.token_bytes(32);old_master=secrets.token_bytes(32)
    while old_master==new_master:old_master=secrets.token_bytes(32)
    nonce=secrets.token_bytes(16)
    while not any(nonce):nonce=secrets.token_bytes(16)
    pre=seal(old_master,101,39,wire,1,device)
    post=seal(new_master,202,40,wire,1,device)
    publish=seal(new_master,202,40,wire,2,device)
    valid_proof=proof(new_master,nonce,post,wire,1,device,40)
    cases=[]
    def add(name,expected,*,master=new_master,sealed=post,issued=nonce,echo=nonce,
            mac=valid_proof,purpose=1,tag=device,before='post',after='post',
            rev0=12,rev1=12,floor=11,source=777,alias='none'):
        cases.append((name,expected,master,sealed,issued,echo,mac,purpose,tag,
                      before,after,rev0,rev1,floor,source,alias))
    add('valid_post',True)
    add('valid_pre',True,master=old_master,sealed=pre,before='pre',after='pre',
        mac=proof(old_master,nonce,pre,wire,1,device,39))
    add('valid_publish',True,sealed=publish,purpose=2,
        mac=proof(new_master,nonce,publish,wire,2,device,40))
    add('different_issued_nonce',False,issued=secrets.token_bytes(16))
    add('different_echo_nonce',False,echo=secrets.token_bytes(16))
    add('both_other_nonce_same_old_proof',False,issued=secrets.token_bytes(16),echo=nonce)
    add('all_zero_nonce',False,issued=bytes(16),echo=bytes(16))
    add('wrong_proof',False,mac=secrets.token_bytes(32))
    add('zero_proof',False,mac=bytes(32))
    add('old_key_after_cutover',False,master=old_master,sealed=pre,
        mac=proof(old_master,nonce,pre,wire,1,device,39))
    add('wrong_master',False,master=old_master)
    add('replaced_receipt',False,sealed=publish)
    add('wrong_before_policy',False,before='pre')
    add('wrong_after_policy',False,after='pre')
    add('retired_policy',False,before='retired')
    add('future_policy',False,before='future')
    add('bad_before_purpose',False,before='badpurpose')
    add('bad_after_device',False,after='baddevice')
    add('bad_before_source',False,before='badsource')
    add('bad_after_source',False,after='badsource')
    add('revision_change_after_auth',False,rev1=13)
    add('revision_rollback_after_auth',False,rev1=11)
    add('revision_stale_before_auth',False,floor=12)
    add('revised_before_without_new_hmac',False,rev0=13,rev1=13)
    add('source_mismatch',False,source=778)
    add('purpose_mismatch',False,purpose=2)
    add('device_mismatch',False,tag=device+1)
    add('output_alias_before',False,alias='alias')
    # Negative cases that independently mutate nonce and the authenticated proof.
    for idx in range(16):
        changed=bytearray(nonce);changed[idx]^=0x80
        add('nonce_flip_'+str(idx),False,issued=bytes(changed),echo=bytes(changed))
    for idx in (0,1,7,15,16,23,24,31):
        changed=bytearray(valid_proof);changed[idx]^=0x40
        add('proof_flip_'+str(idx),False,mac=bytes(changed))
    for idx in (0,4,8,16,24,40,80,95,96,112,127):
        changed=bytearray(post);changed[idx]^=0x20
        add('sealed_flip_'+str(idx),False,sealed=bytes(changed))
    # Challenge proofs derived with incorrect metadata MUST fail even if the B41 gate accepts.
    for idx,(revision,source,purp,dev,epoch) in enumerate([
            (13,777,1,device,40),(12,778,1,device,40),
            (12,777,2,device,40),(12,777,1,device+1,40),
            (12,777,1,device,41)]):
        add('proof_wrong_context_'+str(idx),False,
            mac=proof(new_master,nonce,post,wire,purp,dev,epoch,revision,source))
    expected_accept=sum(c[1] for c in cases)
    assert expected_accept==3,(len(cases),expected_accept)
    passed=0
    for idx,(name,expected,master,sealed,issued,echo,mac,purpose,tag,before,after,
             rev0,rev1,floor,source,alias) in enumerate(cases):
        artifacts={}
        for suffix,data in [('master',master),('receipt',sealed),('issued',issued),
                            ('echo',echo),('mac',mac)]:
            p=d/f'{idx}_{suffix}.bin';p.write_bytes(data);artifacts[suffix]=p
        result=run(c42,artifacts['master'],artifacts['receipt'],wire_file,
            artifacts['issued'],artifacts['echo'],artifacts['mac'],purpose,tag,before,
            after,rev0,rev1,floor,source,alias)
        assert result in ('B42_CHALLENGE=ACCEPT_TEST_ONLY','B42_CHALLENGE=DENIED_TEST_ONLY'),(name,result)
        assert (result=='B42_CHALLENGE=ACCEPT_TEST_ONLY')==expected,(name,result,expected)
        passed+=1
assert passed==len(cases)
print(f'B42_CHALLENGE=PASS_{passed}_CASES_3_ACCEPT_{passed-3}_DENY_NO_DB')
print('B42_TRUSTED_NONCE_ISSUANCE_SINGLE_USE_ATOMIC_CAS_ESP32=NOT_VERIFIED')
