#!/usr/bin/env python3
"""SYS-004 host-only read-only topic allowlist tests; not an integrated API gate."""
import os,subprocess,tempfile,unittest
from pathlib import Path
H=Path(__file__).resolve().parents[1]/'firmware/src'
class Sys004TopicGate(unittest.TestCase):
 def test_allowlist_and_blocklist(self):
  code=r"""#include "sys004_no_actuator_host_gate.h"
#include <assert.h>
int main(void){assert(sys004_host_allow_topic("telemetry.read"));
assert(sys004_host_allow_topic("diagnostic.read"));
assert(sys004_host_allow_topic("health.read"));
assert(!sys004_host_allow_topic("engine.start"));
assert(!sys004_host_allow_topic("steering.set"));
assert(!sys004_host_allow_topic("radio.transmit"));
assert(!sys004_host_allow_topic("ignition.on"));
assert(!sys004_host_allow_topic("telemetry.read "));
assert(!sys004_host_allow_topic("TELEMETRY.READ"));
assert(!sys004_host_allow_topic(""));assert(!sys004_host_allow_topic(0));return 0;}"""
  with tempfile.TemporaryDirectory(prefix='sys004-') as d:
   f=Path(d)/'x.c';exe=Path(d)/('x.exe' if os.name=='nt' else 'x');f.write_text(code)
   subprocess.run([os.environ.get('VG_HOST_CC','gcc'),'-std=c99','-Wall','-Wextra','-Werror','-I',str(H),str(f),'-o',str(exe)],check=True,capture_output=True,text=True)
   subprocess.run([str(exe)],check=True,capture_output=True,text=True)
if __name__=='__main__':unittest.main(verbosity=2)
