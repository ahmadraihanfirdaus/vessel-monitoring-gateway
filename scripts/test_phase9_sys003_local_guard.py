#!/usr/bin/env python3
"""SYS-003 fake callbacks only; cannot establish real firmware separation."""
import os, subprocess, tempfile, unittest
from pathlib import Path
HEADER = Path(__file__).resolve().parents[1] / 'firmware' / 'src'
class Sys003HostContractTests(unittest.TestCase):
    def compile_fixture(self, network):
        source = r"""
#include <assert.h>
#include "network_outage_local_guard.h"
typedef struct { int sample,evaluate,alarm; } counts;
static void s(void *p) { ((counts *)p)->sample++; }
static void e(void *p) { ((counts *)p)->evaluate++; }
static void a(void *p) { ((counts *)p)->alarm++; }
int main(void) {
 counts c={0};sys003_local_driver d={&c,s,e,a};
 assert(sys003_local_step(d,NETWORK_STATE));
 assert(c.sample==1&&c.evaluate==1&&c.alarm==1);
 assert(!sys003_local_step((sys003_local_driver){0},NETWORK_STATE));
 return 0;
}
""".replace('NETWORK_STATE', network)
        with tempfile.TemporaryDirectory(prefix='sys003-host-') as d:
            p=Path(d)/'fixture.c';out=Path(d)/('fixture.exe' if os.name=='nt' else 'fixture')
            p.write_text(source,encoding='utf-8')
            subprocess.run([os.environ.get('SYS003_HOST_CC','gcc'),'-std=c99','-Wall','-Wextra','-Werror','-I',str(HEADER),str(p),'-o',str(out)],check=True,capture_output=True,text=True)
            subprocess.run([str(out)],check=True,capture_output=True,text=True)
    def test_idle(self): self.compile_fixture('NET001_HOST_IDLE')
    def test_connecting(self): self.compile_fixture('NET001_HOST_CONNECTING')
    def test_ready(self): self.compile_fixture('NET001_HOST_READY')
    def test_backoff(self): self.compile_fixture('NET001_HOST_BACKOFF')
if __name__ == '__main__': unittest.main()
