import unittest
from phase9_b8_testlib import compile_and_run
class Ack(unittest.TestCase):
 def test_verified_exactly_once_monotonic(self):
  compile_and_run(r'''
#include "phase9_b8_ack_window.h"
int main(void){phase9_b8_ack_window w;phase9_b8_ack_init(&w);
assert(phase9_b8_ack_begin(&w,12u,77u));
assert(!phase9_b8_ack_begin(&w,13u,88u));
assert(!phase9_b8_ack_commit(&w,12u,78u,true,true,true));
assert(!phase9_b8_ack_commit(&w,12u,77u,false,true,true));
assert(!phase9_b8_ack_commit(&w,12u,77u,true,false,true));
assert(!phase9_b8_ack_commit(&w,12u,77u,true,true,false));
assert(w.last_accepted_sequence==0u&&w.pending);
assert(phase9_b8_ack_commit(&w,12u,77u,true,true,true));
assert(w.last_accepted_sequence==12u&&!w.pending);
assert(!phase9_b8_ack_commit(&w,12u,77u,true,true,true));
assert(!phase9_b8_ack_begin(&w,12u,78u));
assert(phase9_b8_ack_begin(&w,13u,80u));
phase9_b8_ack_cancel(&w);assert(!w.pending);
assert(phase9_b8_ack_begin(&w,13u,80u));return 0;}
''')
if __name__=='__main__':unittest.main(verbosity=2)
