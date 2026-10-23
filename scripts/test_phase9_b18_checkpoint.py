#!/usr/bin/env python3
"""NET-002 host checkpoint codec, restart in a second process, corrupt input guards.
No MySQL, ESP NVS, app transport or firmware flash access."""
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'scripts/phase9_b18_checkpoint_fixture.c'


def run(argv):
    r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    if r.returncode:
        raise AssertionError(f'COMMAND_FAILED_{r.returncode}: {argv}\n{r.stdout}\n{r.stderr}')
    return r.stdout.strip()


def main():
    compiler=os.environ.get('VG_GCC') or shutil.which('gcc')
    if not compiler:
        raise AssertionError('GCC_MISSING')
    with tempfile.TemporaryDirectory(prefix='vg_b18_host_') as raw:
        temp=pathlib.Path(raw)
        exe=temp/('vg-b18-checkpoint.exe' if os.name=='nt' else 'vg-b18-checkpoint')
        compile_cmd=[compiler,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
                     '-Ifirmware/src',str(FIXTURE),'-o',str(exe)]
        run_from=subprocess.run(compile_cmd,cwd=ROOT,capture_output=True,text=True,timeout=45)
        if run_from.returncode:
            raise AssertionError('GCC_STRICT_COMPILE_FAILED\n'+run_from.stderr)
        snapshot=temp/'snapshot.bin'
        saved=run([str(exe),'save',str(snapshot)])
        assert 'B18_SAVE=PASS_COUNT_8_EVICTED_2_PENDING_OMITTED' in saved,saved
        data=snapshot.read_bytes()
        assert 27 <= len(data) <= 768
        restored=run([str(exe),'restore',str(snapshot)])
        assert restored=='B18_RESTART_RESTORE=PASS_8_EVENTS_2_EVICTED_LAST_ACK_7_NEW_PENDING_ONLY',restored
        negative=run([str(exe),'negative'])
        assert negative.startswith('B18_NEGATIVE=PASS_'),negative
        # A partial disk write and a silent bit flip must fail in a different process.
        for label,payload in [('truncated',data[:-1]),('corrupt',data[:8]+bytes([data[8]^1])+data[9:]),('trailing',data+b'!')]:
            bad=temp/(label+'.bin');bad.write_bytes(payload)
            proc=subprocess.run([str(exe),'restore',str(bad)],capture_output=True,timeout=20)
            assert proc.returncode==22 and not proc.stdout,(label,proc.returncode)
        # Original evidence bytes are immutable to the test; CRC is not authenticity.
        assert snapshot.read_bytes()==data
        print('B18_HOST_RESTART=PASS_SAVED_8_RESTORED_8_EVICTED_2_PENDING_RESET')
        print('B18_HOST_NEGATIVE=PASS_WRONG_ID_TRUNCATED_CORRUPT_TRAILING_ATOMIC')
        print('B18_CHECKPOINT_SHA256='+hashlib.sha256(data).hexdigest())
        print('B18_POWERLOSS_DURABILITY=NOT_VERIFIED_HOST_FIXTURE_ONLY')


if __name__=='__main__':
    main()
