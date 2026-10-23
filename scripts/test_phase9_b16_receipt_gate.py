"""Compile production-header receipt admission with strict GCC, no database/network."""
import os, pathlib, subprocess, tempfile, re
R=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='vg-b16-') as td:
    binary=pathlib.Path(td)/('b16.exe' if os.name=='nt' else 'b16')
    cc=os.getenv('CC','gcc')
    build=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
        '-I',str(R/'firmware/src'),str(R/'scripts/phase9_b16_receipt_fixture.c'),'-o',str(binary)],
        cwd=R,capture_output=True,text=True,timeout=60)
    assert build.returncode==0,(build.stdout,build.stderr)
    run=subprocess.run([str(binary)],cwd=R,capture_output=True,timeout=20)
    assert run.returncode==0 and run.stderr==b'',(run.returncode,run.stderr)
    output=run.stdout.decode('ascii').strip()
    assert re.fullmatch(r'B16_RECEIPT_GATE=PASS_21_CASES_HOST_ONLY',output),repr(output)
print('B16_RECEIPT_GATE=PASS_21_HOST_CASES')
