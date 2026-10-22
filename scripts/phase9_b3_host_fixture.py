#!/usr/bin/env python3
"""Batch 3 host-only compiler helper. No database, network or source writes."""
import os, subprocess, tempfile
from pathlib import Path
HEADER=Path(__file__).resolve().parents[1]/'firmware'/'src'
def compile_and_run(source):
    with tempfile.TemporaryDirectory(prefix='phase9-b3-host-') as folder:
        src=Path(folder)/'fixture.c'
        exe=Path(folder)/('fixture.exe' if os.name=='nt' else 'fixture')
        src.write_text('#include <assert.h>\n'+source,encoding='utf-8')
        cc=os.environ.get('VG_HOST_CC','gcc')
        subprocess.run([cc,'-std=c99','-Wall','-Wextra','-Werror','-pedantic',
            '-I',str(HEADER),str(src),'-o',str(exe)],check=True,capture_output=True,text=True)
        subprocess.run([str(exe)],check=True,capture_output=True,text=True)
