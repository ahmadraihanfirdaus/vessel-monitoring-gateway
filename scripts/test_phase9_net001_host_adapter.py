#!/usr/bin/env python3
'''NET-001 host-only proposed test SOURCE. NOT RUN by payload generation.

When separately authorized, this suite compiles a tiny C fixture using a
host compiler and injects fake nonblocking callbacks and caller-owned ticks.
All numeric values in fixtures are TEST DATA, NOT production configuration.
'''
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

HEADER = Path(__file__).resolve().parents[1] / 'firmware' / 'src' / 'network_transport_host_adapter.h'
COMPILER = os.environ.get('NET001_HOST_CC', 'gcc')

PREFIX = r'''
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include "network_transport_host_adapter.h"
struct fake { int begin_count, poll_count, cancel_count; bool begin_ok; net001_host_link link; };
static bool begin(void *ctx) { struct fake *f=ctx; f->begin_count++; return f->begin_ok; }
static net001_host_link observe(void *ctx) { struct fake *f=ctx; f->poll_count++; return f->link; }
static void cancel(void *ctx) { struct fake *f=ctx; f->cancel_count++; }
static net001_host_driver driver(struct fake *f) {
    net001_host_driver d={f, begin, observe, cancel}; return d;
}
/* Fixture-only values; not NET-001 runtime defaults. */
static net001_host_policy fixture_policy(void) {
    net001_host_policy p={10u,5u,2u}; return p;
}
'''

class Net001HostAdapterContractTests(unittest.TestCase):
    def compile_and_run_fixture(self, snippet):
        self.assertTrue(HEADER.is_file(), 'header draft must be copied into authorized test workspace')
        with tempfile.TemporaryDirectory(prefix='net001-host-test-') as tmp:
            program=Path(tmp)/'fixture.c'
            executable=Path(tmp)/('fixture.exe' if os.name=='nt' else 'fixture')
            program.write_text(PREFIX+'\n'+textwrap.dedent(snippet), encoding='utf-8')
            subprocess.run([COMPILER,'-std=c99','-Wall','-Wextra','-Werror',
                            '-I',str(HEADER.parent),str(program),'-o',str(executable)],
                            check=True, capture_output=True, text=True)
            subprocess.run([str(executable)],check=True,capture_output=True,text=True)

    def test_idle_connecting_ready_and_callback_budget(self):
        self.compile_and_run_fixture(r'''
            int main(void) {
                struct fake f={0}; f.begin_ok=true; f.link=NET001_LINK_PENDING;
                net001_host_adapter a={0}; assert(net001_host_init(&a,fixture_policy(),driver(&f)));
                assert(net001_host_step(&a,100u)==NET001_HOST_CONNECTING);
                assert(f.begin_count==1 && f.poll_count==0);
                assert(net001_host_step(&a,101u)==NET001_HOST_CONNECTING);
                f.link=NET001_LINK_UP;
                assert(net001_host_step(&a,102u)==NET001_HOST_READY);
                assert(a.attempts_in_cycle==0u && !a.exhausted);
                return 0;
            }
        ''')

    def test_timeout_backoff_and_second_attempt(self):
        self.compile_and_run_fixture(r'''
            int main(void) {
                struct fake f={0}; f.begin_ok=true; f.link=NET001_LINK_PENDING;
                net001_host_adapter a={0}; assert(net001_host_init(&a,fixture_policy(),driver(&f)));
                net001_host_step(&a,100u);
                assert(net001_host_step(&a,110u)==NET001_HOST_BACKOFF);
                assert(f.cancel_count==1);
                assert(net001_host_step(&a,114u)==NET001_HOST_BACKOFF);
                assert(net001_host_step(&a,115u)==NET001_HOST_IDLE);
                assert(net001_host_step(&a,116u)==NET001_HOST_CONNECTING);
                assert(f.begin_count==2);
                return 0;
            }
        ''')

    def test_bounded_retry_exhaustion_requires_reset(self):
        self.compile_and_run_fixture(r'''
            int main(void) {
                struct fake f={0}; f.begin_ok=false;
                net001_host_adapter a={0}; assert(net001_host_init(&a,fixture_policy(),driver(&f)));
                assert(net001_host_step(&a,0u)==NET001_HOST_BACKOFF);
                assert(net001_host_step(&a,5u)==NET001_HOST_IDLE);
                assert(net001_host_step(&a,6u)==NET001_HOST_IDLE);
                assert(a.exhausted && f.begin_count==2);
                net001_host_step(&a,500u); assert(f.begin_count==2);
                net001_host_reset(&a);assert(!a.exhausted);
                assert(net001_host_step(&a,501u)==NET001_HOST_BACKOFF);
                return 0;
            }
        ''')

    def test_ready_disconnect_cooldown(self):
        self.compile_and_run_fixture(r'''
            int main(void) {
                struct fake f={0}; f.begin_ok=true; f.link=NET001_LINK_UP;
                net001_host_adapter a={0}; assert(net001_host_init(&a,fixture_policy(),driver(&f)));
                net001_host_step(&a,2u);net001_host_step(&a,3u);
                f.link=NET001_LINK_DOWN;
                assert(net001_host_step(&a,4u)==NET001_HOST_BACKOFF);
                assert(f.cancel_count==1);
                assert(net001_host_step(&a,9u)==NET001_HOST_IDLE);
                assert(net001_host_step(&a,10u)==NET001_HOST_CONNECTING);
                return 0;
            }
        ''')

    def test_elapsed_tick_wrap(self):
        self.compile_and_run_fixture(r'''
            int main(void) {
                struct fake f={0}; f.begin_ok=true; f.link=NET001_LINK_PENDING;
                net001_host_adapter a={0}; assert(net001_host_init(&a,fixture_policy(),driver(&f)));
                net001_host_step(&a,UINT32_MAX-3u);
                assert(net001_host_step(&a,7u)==NET001_HOST_BACKOFF);
                return 0;
            }
        ''')

    def test_init_rejects_missing_callbacks_or_policy(self):
        self.compile_and_run_fixture(r'''
            int main(void) {
                struct fake f={0}; net001_host_adapter a={0};
                net001_host_policy p=fixture_policy();net001_host_driver d=driver(&f);
                p.connect_timeout_ms=0u;assert(!net001_host_init(&a,p,d));
                p=fixture_policy();p.reconnect_backoff_ms=0u;assert(!net001_host_init(&a,p,d));
                p=fixture_policy();p.max_attempts=0u;assert(!net001_host_init(&a,p,d));
                p=fixture_policy();d.begin=0;assert(!net001_host_init(&a,p,d));
                assert(!net001_host_init(0,p,driver(&f)));
                return 0;
            }
        ''')

if __name__ == '__main__':
    unittest.main()
