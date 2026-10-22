#!/usr/bin/env python3
"""Host-only fixture compiler and PHP CLI bridge; no repo, DB, or network write."""
import os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def compile_c(source):
    with tempfile.TemporaryDirectory(prefix='phase9-b4-') as td:
        src=Path(td)/'fixture.c';exe=Path(td)/('f.exe' if os.name=='nt' else 'f')
        src.write_text('#include <assert.h>\n'+source,encoding='utf-8')
        cc=os.environ.get('VG_HOST_CC','gcc')
        b=subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic','-I',str(ROOT/'firmware'/'src'),str(src),'-o',str(exe)],capture_output=True,text=True)
        if b.returncode:raise AssertionError('COMPILE_FAIL '+b.stdout+b.stderr)
        p=subprocess.run([str(exe)],capture_output=True,text=True)
        if p.returncode:raise AssertionError('RUNTIME_FAIL '+p.stdout+p.stderr)
        return p.stdout
def php_accepts(raw):
    code="require 'backend/laravel/app/Support/Phase9B4IngestContract.php'; echo App\\Support\\Phase9B4IngestContract::acceptsSynthetic(stream_get_contents(STDIN)) ? 'ACCEPT' : 'REJECT';"
    r=subprocess.run([os.environ.get('VG_PHP_CLI','php'),'-r',code],cwd=ROOT,input=raw,text=True,capture_output=True)
    if r.returncode:raise AssertionError('PHP_ERROR '+r.stdout+r.stderr)
    assert r.stdout in ('ACCEPT','REJECT'),r.stdout
    return r.stdout=='ACCEPT'
