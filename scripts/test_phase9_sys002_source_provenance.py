#!/usr/bin/env python3
"""SYS-002 narrow host provenance checks; no physical provider evidence."""
import os,subprocess,tempfile,unittest
from pathlib import Path
H=Path(__file__).resolve().parents[1]/'firmware/src'
class SourceProvenance(unittest.TestCase):
 def test_three_sources_unknown_rejection_and_no_mutation(self):
  code=r"""#include "sys002_source_provenance_host.h"
#include <assert.h>
#include <string.h>
int main(void){sys002_source_mode m=SYS002_SIMULATION;
 assert(sys002_parse_source("simulation",&m)&&m==SYS002_SIMULATION);
 assert(sys002_parse_source("bench_test",&m)&&m==SYS002_BENCH_TEST);
 assert(sys002_parse_source("physical",&m)&&m==SYS002_PHYSICAL);
 assert(!sys002_parse_source("live",&m)&&m==SYS002_PHYSICAL);
 assert(!sys002_parse_source("PHYSICAL",&m)&&m==SYS002_PHYSICAL);
 assert(!sys002_parse_source(0,&m)&&m==SYS002_PHYSICAL);
 assert(!sys002_parse_source("simulation",0));
 assert(!strcmp(sys002_source_label(SYS002_SIMULATION),"simulation"));
 assert(!strcmp(sys002_source_label(SYS002_BENCH_TEST),"bench_test"));
 assert(!strcmp(sys002_source_label(SYS002_PHYSICAL),"physical"));
 assert(sys002_source_label((sys002_source_mode)9)==0);return 0;}"""
  with tempfile.TemporaryDirectory(prefix='sys002-') as d:
   f=Path(d)/'m.c';exe=Path(d)/('m.exe' if os.name=='nt' else 'm');f.write_text(code)
   subprocess.run([os.environ.get('VG_HOST_CC','gcc'),'-std=c99','-Wall','-Wextra','-Werror','-I',str(H),str(f),'-o',str(exe)],check=True,capture_output=True,text=True)
   subprocess.run([str(exe)],check=True,capture_output=True,text=True)
if __name__=='__main__':unittest.main(verbosity=2)
