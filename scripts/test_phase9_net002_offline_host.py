#!/usr/bin/env python3
"""NET-002 volatile host-only tests: not power-loss or ESP-NVS evidence."""
import os,subprocess,tempfile,unittest
from pathlib import Path
H=Path(__file__).resolve().parents[1]/'firmware/src'
def run(src):
 with tempfile.TemporaryDirectory(prefix='net002-') as d:
  p=Path(d)/'x.c';exe=Path(d)/('x.exe' if os.name=='nt' else 'x')
  p.write_text('#include "net002_offline_host_store.h"\n#include <assert.h>\n#include <string.h>\n'+src)
  subprocess.run([os.environ.get('VG_HOST_CC','gcc'),'-std=c99','-Wall','-Wextra','-Werror','-I',str(H),str(p),'-o',str(exe)],check=True,capture_output=True,text=True)
  subprocess.run([str(exe)],check=True,capture_output=True,text=True)
class Net002HostTest(unittest.TestCase):
 def test_latest_retains_good_after_invalid(self):run(r"""int main(void){net002_host_offline_store s;net002_host_init(&s);char x[]={1,2,3};assert(net002_host_set_latest(&s,x,3));assert(!net002_host_set_latest(&s,x,257));assert(s.latest_len==3&&s.latest[2]==3);return 0;}""")
 def test_missing_and_zero_rejected(self):run(r"""int main(void){net002_host_offline_store s;net002_host_init(&s);assert(!net002_host_set_latest(&s,0,4));assert(!net002_host_set_latest(&s,"",0));assert(!s.has_latest);return 0;}""")
 def test_bounded_event_eviction_visible(self):run(r"""int main(void){net002_host_offline_store s;net002_host_init(&s);for(int i=1;i<=12;i++)assert(net002_host_add_critical(&s,(uint32_t)i,0,"alarm"));net002_host_critical_event e;assert(s.count==8&&s.evicted_count==4);assert(net002_host_get_event(&s,0,&e)&&e.event_id==5);assert(net002_host_get_event(&s,7,&e)&&e.event_id==12);return 0;}""")
 def test_bad_event_does_not_evict(self):run(r"""int main(void){net002_host_offline_store s;net002_host_init(&s);assert(net002_host_add_critical(&s,1,0,"critical"));assert(!net002_host_add_critical(&s,2,0,""));assert(!net002_host_add_critical(&s,0,0,"critical"));assert(s.count==1&&s.evicted_count==0);return 0;}""")
if __name__=='__main__':unittest.main(verbosity=2)
