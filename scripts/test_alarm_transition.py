"""Real strict C99 immutable alarm-transition checks; no hardware/persistence claim."""
import json
import unittest
from phase9_b4_testlib import compile_c

BASE = r'''
#include "alarm_transition.h"
static vg_event_journal_t journal, before_journal;
static vg_alarm_journal_t metadata, before_metadata;
static vg_alarm_id_allocator_t ids;
static vg_alarm_t alarm;
static char wire[4097];
int main(void) {
assert(vg_journal_init(&journal));vg_alarm_id_allocator_init(&ids);
assert(vg_alarm_try_raise(&ids,&alarm,7u,VG_SOURCE_SIMULATION,3u,1001u,0u));
uint64_t event_id=99u;
(void)before_journal;(void)before_metadata;(void)wire;(void)event_id;
'''


class AlarmTransitionTest(unittest.TestCase):
    def c(self, source):
        return compile_c(BASE+source+'\nreturn 0;}\n', extra_flags=('-Os',))

    def test_full_lifecycle_is_immutable_and_zero_times_are_not_null(self):
        raw = self.c(r'''
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0u,&event_id));
assert(event_id==1u&&vg_alarm_journal_matches(&metadata,&journal));
assert(vg_alarm_try_acknowledge(&alarm,0u));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,0u,&event_id));
assert(alarm.condition_active&&alarm.state==VG_ALARM_STATE_ACTIVE_ACK);
assert(vg_alarm_try_clear_condition(&alarm,100u));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_CLEARED,100u,&event_id));
assert(metadata.count==3&&metadata.entries[0].alarm.state==VG_ALARM_STATE_ACTIVE_UNACK);
for(size_t i=0;i<3;i++){assert(vg_alarm_transition_json(&metadata.entries[i],"alarm:demo","boot-a",wire,sizeof(wire)));puts(wire);}
''')
        packets = [json.loads(line) for line in raw.splitlines()]
        self.assertEqual([packet['alarm']['state'] for packet in packets], ['active_unack', 'active_ack', 'cleared'])
        self.assertEqual([packet['alarm']['raised_at_ms'] for packet in packets], [0, 0, 0])
        self.assertEqual([packet['alarm']['acknowledged_at_ms'] for packet in packets], [None, 0, 0])
        self.assertEqual([packet['alarm']['cleared_at_ms'] for packet in packets], [None, None, 100])
        self.assertEqual(packets[0]['alarm']['priority_code'], 3)
        self.assertEqual(packets[0]['alarm']['reason_code'], 1001)

    def test_mismatched_transition_never_partially_appends(self):
        self.c(r'''
before_journal=journal;before_metadata=metadata;
assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,0u,&event_id));
assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,1u,&event_id));
assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_FAULT,0u,&event_id));
assert(!memcmp(&before_journal,&journal,sizeof(journal))&&!memcmp(&before_metadata,&metadata,sizeof(metadata))&&event_id==99u);
alarm.source_mode=VG_SOURCE_PHYSICAL;assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&event_id));
''')

    def test_full_journal_keeps_snapshots_and_refusal_counter_saturates(self):
        self.c(r'''
for(size_t i=0;i<8;i++){
 if(i!=0u){memset(&alarm,0,sizeof(alarm));assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,i));}
 assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,i,&event_id));
}
before_metadata=metadata;event_id=99;
assert(vg_alarm_try_acknowledge(&alarm,8));
assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,8,&event_id));
assert(journal.rejected_full==1&&event_id==99&&!memcmp(&metadata,&before_metadata,sizeof(metadata)));
journal.rejected_full=UINT64_MAX;assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,8,&event_id));
assert(journal.rejected_full==UINT64_MAX);
''')

    def test_identity_source_state_and_action_time_are_bound(self):
        self.c(r'''
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&event_id));
vg_alarm_transition_t good=metadata.entries[0],bad=good;
bad.event.linked_alarm_id++;assert(!vg_alarm_transition_valid(&bad));
bad=good;bad.event.source_id++;assert(!vg_alarm_transition_valid(&bad));
bad=good;bad.event.source_mode=VG_SOURCE_BENCH_TEST;assert(!vg_alarm_transition_valid(&bad));
bad=good;bad.event.occurred_at_ms++;assert(!vg_alarm_transition_valid(&bad));
bad=good;bad.alarm.priority_code=0;assert(!vg_alarm_transition_valid(&bad));
bad=good;bad.event.event_id=0;assert(!vg_alarm_transition_valid(&bad));
bad=good;bad.alarm.reason_code++;assert(vg_alarm_transition_valid(&bad));assert(!vg_alarm_transition_equal(&good,&bad));
''')

    def test_uint64_and_u32_boundaries_stay_exact_on_wire(self):
        raw = self.c(r'''
journal.next_id=UINT64_MAX-1u;ids.next_id=UINT64_MAX-1u;memset(&alarm,0,sizeof(alarm));
assert(vg_alarm_try_raise(&ids,&alarm,UINT32_MAX,VG_SOURCE_BENCH_TEST,UINT32_MAX,UINT32_MAX,UINT64_MAX));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,UINT64_MAX,&event_id));
assert(vg_alarm_transition_json(&metadata.entries[0],"alarm:demo","boot-max",wire,sizeof(wire)));puts(wire);
assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,UINT64_MAX,&event_id));
''')
        packet = json.loads(raw)
        self.assertEqual(packet['event_id'], 2**64-2)
        self.assertEqual(packet['linked_alarm_id'], 2**64-2)
        self.assertEqual(packet['alarm']['raised_at_ms'], 2**64-1)
        self.assertEqual(packet['alarm']['priority_code'], 2**32-1)

    def test_aliases_and_corrupt_prefix_are_rejected(self):
        self.c(r'''
assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&journal.next_id));
assert(journal.count==0&&metadata.count==0);
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&event_id));
assert(!vg_alarm_transition_json(&metadata.entries[0],"alarm:demo","boot",(char*)&metadata,sizeof(metadata)));
strcpy(wire,"device");assert(!vg_alarm_transition_json(&metadata.entries[0],wire,"boot",wire,sizeof(wire)));
assert(!vg_alarm_transition_json(&metadata.entries[0],"bad/id","boot",wire,sizeof(wire)));
assert(!vg_alarm_transition_json(&metadata.entries[0],"device","boot",wire,1));
metadata.entries[0].event.source_id++;assert(!vg_alarm_journal_matches(&metadata,&journal));
before_journal=journal;assert(!vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&event_id));
assert(!memcmp(&journal,&before_journal,sizeof(journal)));
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
