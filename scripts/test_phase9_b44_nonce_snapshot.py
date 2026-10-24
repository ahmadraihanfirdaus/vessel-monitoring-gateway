#!/usr/bin/env python3
"""Independent Python struct/HMAC oracle for isolated C99 nonce ledger snapshots."""
from pathlib import Path
import hashlib,hmac,os,secrets,shutil,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
CC=os.getenv('VG_GCC') or shutil.which('gcc')
assert CC,'B44_GCC_NOT_FOUND'
DOMAIN=b'VG_PHASE9_B44_LEDGER_SNAPSHOT_HMAC_V1\x00'
HEADER=struct.Struct('<4sIQQII')
assert HEADER.size==32

def oracle(key,nonces,generation,source,count,*,magic=b'VG44',version=1,reserved=0):
    body=HEADER.pack(magic,version,generation,source,count,reserved)+nonces
    assert len(body)==160
    return body+hmac.new(key,DOMAIN+body,hashlib.sha256).digest()

with tempfile.TemporaryDirectory(prefix='vg_b44_') as temp:
    d=Path(temp);exe=d/('b44.exe' if os.name=='nt' else 'b44')
    cp=subprocess.run([CC,'-std=c99','-pedantic','-Wall','-Wextra','-Werror',
        '-Ifirmware/src','scripts/phase9_b44_nonce_snapshot_fixture.c','-o',str(exe)],
        cwd=ROOT,capture_output=True,text=True,timeout=90)
    assert cp.returncode==0,cp.stderr
    selftest=subprocess.run([str(exe),'selftest'],cwd=ROOT,capture_output=True,
        text=True,timeout=60)
    assert selftest.returncode==0,(selftest.stdout,selftest.stderr)
    assert 'B44_ALIAS_BOUNDS_FAILURE_IMMUTABLE=PASS' in selftest.stdout
    key=secrets.token_bytes(32)
    keyfile=d/'key.bin';keyfile.write_bytes(key)
    nonce_pool=[secrets.token_bytes(16) for _ in range(8)]
    while len(set(nonce_pool))!=8 or any(not any(n) for n in nonce_pool):
        nonce_pool=[secrets.token_bytes(16) for _ in range(8)]
    count=0;cases=[]
    def run(mode,secret,inp,out,generation,source,expected_count):
        result=subprocess.run([str(exe),mode,str(secret),str(inp),str(out),
            str(generation),str(source),str(expected_count)],cwd=ROOT,
            capture_output=True,text=True,timeout=60)
        assert result.returncode==0,(mode,result.stdout,result.stderr,result.returncode)
        return result.stdout.strip()
    for count in (0,1,3,8):
        nonces=b''.join(nonce_pool[:count])+bytes((8-count)*16)
        infile=d/f'nonces_{count}.bin';infile.write_bytes(nonces)
        snapshot=d/f'snapshot_{count}.bin';gen=200+count
        assert run('seal',keyfile,infile,snapshot,gen,777,count)=='B44_SEAL_ACCEPT_TEST_ONLY'
        blob=snapshot.read_bytes()
        assert len(blob)==192 and blob==oracle(key,nonces,gen,777,count)
        recovered=d/f'recovered_{count}.bin'
        assert run('restore',keyfile,snapshot,recovered,gen,777,count)==f'B44_RESTORE_ACCEPT_TEST_ONLY_GEN_{gen}'
        assert recovered.read_bytes()==nonces
        cases.append(f'valid_{count}')
        for floor in (gen+1,gen+13):
            denied=d/f'stale_{count}_{floor}.bin'
            assert run('restore',keyfile,snapshot,denied,floor,777,count)=='B44_RESTORE_DENIED_UNCHANGED_TEST_ONLY'
            assert not denied.exists()
            cases.append(f'stale_{count}_{floor}')
        rejected=d/f'wrong_source_{count}.bin'
        assert run('restore',keyfile,snapshot,rejected,gen,778,count)=='B44_RESTORE_DENIED_UNCHANGED_TEST_ONLY'
        assert not rejected.exists()
        cases.append(f'wrong_source_{count}')
    count=3;nonces=b''.join(nonce_pool[:count])+bytes(80);gen=203
    original=oracle(key,nonces,gen,777,count)
    cases.append('fixed_schema_python_oracle')
    # Explicit adversarial tests: HMAC recomputed with known test key must NOT
    # bypass semantic validation (format, reserved field, nonce ledger validity).
    tampered=[]
    for pos in (0,1,2,3,4,7,8,15,16,23,24,27,28,31,32,40,70,96,125,150,159,160,175,191):
        modified=bytearray(original);modified[pos]^=0x55
        tampered.append((f'corrupt_bit_{pos}',bytes(modified)))
    for name,blob in (
        ('wrong_magic_authenticated',oracle(key,nonces,gen,777,count,magic=b'BAD!')),
        ('wrong_version_authenticated',oracle(key,nonces,gen,777,count,version=2)),
        ('reserved_authenticated',oracle(key,nonces,gen,777,count,reserved=1)),
        ('source_authenticated_wrong',oracle(key,nonces,gen,778,count)),
        ('stale_authenticated',oracle(key,nonces,gen-1,777,count)),
        ('count_oversize_authenticated',oracle(key,nonces,gen,777,9)),
        ('nonzero_trailing_authenticated',oracle(key,nonces[:64]+b'\x01'+nonces[65:],gen,777,count)),
        ('zero_active_nonce_authenticated',oracle(key,bytes(16)+nonces[16:],gen,777,count)),
        ('duplicate_nonce_authenticated',oracle(key,nonces[:16]+nonces[:16]+nonces[32:],gen,777,count)),
        ('count_mismatch_authenticated',oracle(key,nonces,gen,777,count+1)),
    ):
        tampered.append((name,blob))
    for idx,(name,blob) in enumerate(tampered):
        filepath=d/f'tamper_{idx}.bin';filepath.write_bytes(blob)
        denied=d/f'rejected_{idx}.bin'
        assert run('restore',keyfile,filepath,denied,gen,777,count)=='B44_RESTORE_DENIED_UNCHANGED_TEST_ONLY',name
        assert not denied.exists(),name
        cases.append(name)
    wrongkey=d/'wrongkey.bin';wrongkey.write_bytes(secrets.token_bytes(32))
    snap=d/'canonical.bin';snap.write_bytes(original)
    denied=d/'keyfail.bin'
    assert run('restore',wrongkey,snap,denied,gen,777,count)=='B44_RESTORE_DENIED_UNCHANGED_TEST_ONLY'
    assert not denied.exists();cases.append('wrong_key')
    # Seal refuses inconsistent in-memory ledger without writing an output.
    invalid=[('bad_active_zero',bytes(16)+nonces[16:],3),
             ('bad_duplicate',nonces[:16]*2+nonces[32:],3),
             ('bad_tail',nonces[:48]+b'\xff'+nonces[49:],3),
             ('bad_count',nonces,9),('zero_generation',nonces,3)]
    for idx,(name,source_nonces,source_count) in enumerate(invalid):
        fp=d/f'bad_nonce_{idx}.bin';fp.write_bytes(source_nonces)
        out=d/f'bad_seal_{idx}.bin'
        chosen_gen=0 if name=='zero_generation' else gen
        assert run('seal',keyfile,fp,out,chosen_gen,777,source_count)=='B44_SEAL_DENIED_TEST_ONLY',name
        assert not out.exists(),name
        cases.append(name)
    # Conditional restart recovery is a separate process per invocation.
    # The untrusted snapshot alone cannot prove freshness without trusted floor.
    assert len(cases)==len(set(cases)),cases
print(f'B44_NONCE_SNAPSHOT=PASS_{len(cases)}_CROSS_PROCESS_AUTHENTICATED_AND_DENIAL_NO_DB')
print('B44_PYTHON_INDEPENDENT_STRUCT_HMAC_ORACLE=VERIFIED_HOST_ONLY')
print('B44_TRUSTED_GENERATION_FLOOR_CRASH_ATOMIC_STORE_THREAD_CAS_ESP32=NOT_VERIFIED')
