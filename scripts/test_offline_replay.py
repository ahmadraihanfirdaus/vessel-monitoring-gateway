"""Native recovered-view/serialization/fairness faults; SDK IO is not simulated."""
import json
from pathlib import Path
import unittest
from phase9_b4_testlib import compile_c
from test_alarm_offline_metadata import BASE

ROOT = Path(__file__).resolve().parents[1]
PREFIX = '#include "offline_replay.h"\nstatic vg_recovered_events view,saved_view;\nstatic char encoded[1024];\n'


class OfflineReplayTest(unittest.TestCase):
    def c(self, source):
        return compile_c(PREFIX+BASE+'\n(void)view;(void)saved_view;(void)encoded;\n'+source+'\nreturn 0;}\n', extra_flags=('-Os',))

    def test_full_metadata_is_an_immutable_zero_time_snapshot(self):
        raw = self.c(r'''
assert(vg_recovered_events_capture(&current,true,&view));saved_view=view;
assert(view.degraded && view.generation==1 && view.event_count==3);
memset(&current,0,sizeof(current));memset(&metadata,0,sizeof(metadata));
for(size_t i=0;i<3;i++){
assert(vg_recovered_event_json(&view,i,encoded,sizeof(encoded))==VG_REPLAY_ENCODED);puts(encoded);
}
assert(memcmp(&view,&saved_view,sizeof(view))==0);
''')
        packets = [json.loads(line) for line in raw.splitlines()]
        self.assertEqual([p['event_id'] for p in packets], [1, 2, 3])
        self.assertEqual([p['boot_id'] for p in packets], ['boot-a']*3)
        self.assertEqual([p['schema_version'] for p in packets], ['1.1']*3)
        self.assertEqual([p['alarm']['acknowledged_at_ms'] for p in packets], [None, 0, 0])
        self.assertEqual([p['alarm']['cleared_at_ms'] for p in packets], [None, None, 100])

    def test_legacy_is_exact_nine_fields_without_fabricated_metadata(self):
        packet = json.loads(self.c(r'''
assert(vg_offline_init(&empty,"alarm:demo"));
assert(vg_offline_merge(&empty,"legacy-boot",7,"packet",6,&journal,&next)==VG_OFFLINE_READY);
assert(vg_recovered_events_capture(&next,false,&view));
assert(vg_recovered_event_json(&view,0,encoded,sizeof(encoded))==VG_REPLAY_ENCODED);puts(encoded);
'''))
        self.assertEqual(packet, dict(schema_version='1.0', device_id='alarm:demo', boot_id='legacy-boot',
            event_id=1, linked_alarm_id=1, source_id=7, source_mode='simulation',
            event_type='alarm_raised', occurred_at_ms=0))

    def test_maximum_unsigned_values_and_bench_source_preserve_identity(self):
        packet = json.loads(self.c(r'''
assert(vg_recovered_events_capture(&current,false,&view));view.event_count=1;
vg_offline_event *record=&view.events[0];record->has_alarm=false;
record->event=(vg_journal_event_t){UINT64_MAX-1,UINT64_MAX,UINT32_MAX,VG_SOURCE_BENCH_TEST,VG_EVENT_FAULT,UINT64_MAX};
assert(vg_recovered_event_json(&view,0,encoded,sizeof(encoded))==VG_REPLAY_ENCODED);puts(encoded);
'''))
        self.assertEqual(packet['event_id'], 2**64-2)
        self.assertEqual(packet['linked_alarm_id'], 2**64-1)
        self.assertEqual(packet['occurred_at_ms'], 2**64-1)
        self.assertEqual(packet['source_id'], 2**32-1)
        self.assertEqual(packet['source_mode'], 'bench_test')

    def test_duplicate_identity_rejects_same_boot_but_allows_different_boot(self):
        self.c(r'''
assert(vg_recovered_events_capture(&current,false,&view));view.event_count=2;
view.events[1]=view.events[0];assert(!vg_recovered_events_valid(&view));
strcpy(view.events[1].boot,"another-boot");assert(vg_recovered_events_valid(&view));
assert(vg_recovered_event_json(&view,1,encoded,sizeof(encoded))==VG_REPLAY_ENCODED);
''')

    def test_capture_invalid_or_alias_does_not_publish_or_mutate(self):
        self.c(r'''
memset(&view,0x5a,sizeof(view));saved_view=view;
next=current;next.event_count=VG_OFFLINE_EVENT_CAP+1;
assert(!vg_recovered_events_capture(&next,false,&view));assert(memcmp(&view,&saved_view,sizeof(view))==0);
assert(!vg_recovered_events_capture(&current,false,(vg_recovered_events*)&current));
assert(!vg_recovered_events_capture(NULL,false,&view));
assert(vg_offline_init(&empty,"alarm:demo"));
assert(!vg_recovered_events_capture(&empty,true,&view));
assert(vg_recovered_events_capture(&empty,false,&view));assert(view.generation==0 && view.event_count==0 && !view.degraded);
''')

    def test_bounded_fields_source_metadata_and_generation_corruption_refused(self):
        self.c(r'''
assert(vg_recovered_events_capture(&current,false,&view));saved_view=view;
memset(view.device,'x',sizeof(view.device));assert(!vg_recovered_events_valid(&view));view=saved_view;
memset(view.events[0].boot,'x',sizeof(view.events[0].boot));assert(!vg_recovered_events_valid(&view));view=saved_view;
view.events[0].event.source_mode=VG_SOURCE_PHYSICAL;assert(!vg_recovered_events_valid(&view));view=saved_view;
view.events[0].alarm.reason_code=0;assert(!vg_recovered_events_valid(&view));view=saved_view;
view.generation=0;assert(!vg_recovered_events_valid(&view));view=saved_view;
view.event_count=VG_OFFLINE_EVENT_CAP+1;assert(!vg_recovered_events_valid(&view));
''')

    def test_buffer_boundary_and_alias_cannot_damage_retained_view(self):
        self.c(r'''
assert(vg_recovered_events_capture(&current,false,&view));saved_view=view;
assert(vg_recovered_event_json(&view,0,encoded,sizeof(encoded))==VG_REPLAY_ENCODED);size_t n=strlen(encoded);
assert(vg_recovered_event_json(&view,0,encoded,n)==VG_REPLAY_BUFFER_REFUSED);
assert(vg_recovered_event_json(&view,0,encoded,n+1)==VG_REPLAY_ENCODED);
assert(vg_recovered_event_json(&view,0,(char*)&view,sizeof(view))==VG_REPLAY_INVALID);
assert(vg_recovered_event_json(&view,3,encoded,sizeof(encoded))==VG_REPLAY_INVALID);
assert(vg_recovered_event_json(&view,0,NULL,1)==VG_REPLAY_INVALID);
assert(memcmp(&view,&saved_view,sizeof(view))==0);
''')

    def test_unsupported_legacy_is_explicit_and_retained_while_next_can_encode(self):
        self.c(r'''
assert(vg_recovered_events_capture(&current,false,&view));view.events[0].has_alarm=false;
view.events[0].event.type=VG_EVENT_RECOVERY;saved_view=view;
assert(vg_recovered_event_json(&view,0,encoded,sizeof(encoded))==VG_REPLAY_UNSUPPORTED_TYPE);
assert(vg_recovered_event_json(&view,1,encoded,sizeof(encoded))==VG_REPLAY_ENCODED);
assert(memcmp(&view,&saved_view,sizeof(view))==0);
''')

    def test_full_sources_alternate_and_backpressure_does_not_advance(self):
        self.c(r'''
vg_replay_progress progress={0};progress.prefer_recovered=true;
for(size_t i=0;i<8;i++){
for(size_t retry=0;retry<100;retry++)assert(vg_replay_choose(&progress,8,8)==VG_REPLAY_RECOVERED);
assert(progress.recovered_visited==i && progress.current_queued==i);
assert(vg_replay_mark(&progress,8,8,VG_REPLAY_RECOVERED,false));
assert(vg_replay_choose(&progress,8,8)==VG_REPLAY_CURRENT);
assert(vg_replay_mark(&progress,8,8,VG_REPLAY_CURRENT,false));
}
assert(vg_replay_choose(&progress,8,8)==VG_REPLAY_NONE);
''')

    def test_current_progress_survives_new_recovery_and_unsupported_does_not_block(self):
        self.c(r'''
vg_replay_progress progress={0};
assert(vg_replay_mark(&progress,0,2,VG_REPLAY_CURRENT,false));
progress.recovered_visited=0;progress.recovered_unpublishable=0;progress.prefer_recovered=true;
assert(vg_replay_mark(&progress,2,2,VG_REPLAY_RECOVERED,true));
assert(progress.recovered_unpublishable==1 && progress.current_queued==1);
assert(vg_replay_mark(&progress,2,2,VG_REPLAY_CURRENT,false));
assert(vg_replay_mark(&progress,2,2,VG_REPLAY_RECOVERED,false));
assert(vg_replay_choose(&progress,2,2)==VG_REPLAY_NONE);
''')

    def test_invalid_progress_wrong_source_and_fake_unsupported_do_not_advance(self):
        self.c(r'''
vg_replay_progress progress={0},copy=progress;
assert(!vg_replay_mark(&progress,1,1,VG_REPLAY_RECOVERED,false));assert(memcmp(&progress,&copy,sizeof(progress))==0);
assert(!vg_replay_mark(&progress,1,1,VG_REPLAY_CURRENT,true));assert(memcmp(&progress,&copy,sizeof(progress))==0);
assert(vg_replay_choose(&progress,9,1)==VG_REPLAY_CHOICE_INVALID);
progress.current_queued=2;assert(vg_replay_choose(&progress,1,1)==VG_REPLAY_CHOICE_INVALID);
progress=copy;progress.recovered_unpublishable=1;assert(vg_replay_choose(&progress,1,1)==VG_REPLAY_CHOICE_INVALID);
''')

    def test_actual_worker_and_sdk_use_zero_wait_shared_path_without_deletion(self):
        worker = (ROOT/'firmware/src/esp32_offline_store.c').read_text(encoding='utf-8')
        caller = (ROOT/'firmware/src/esp32_continuous_main.h').read_text(encoding='utf-8')
        self.assertIn('vg_recovered_events_capture(&ctx->transaction.current,', worker)
        self.assertIn('xQueueCreate(1u, sizeof(vg_recovered_events))', worker)
        self.assertIn('xQueueReceive(storage->recovered, out, 0)', worker)
        for name in ('vg_storage_take_recovered_events', 'vg_recovered_event_json', 'vg_replay_choose', 'vg_replay_mark'):
            self.assertIn(name, caller)
        for text in ('nvs_erase', 'gpio_set_level', 'vg_offline_publish('):
            self.assertNotIn(text, caller)

    def test_full_eight_boot_view_encodes_all_records_and_ninth_is_refused(self):
        self.c(r'''
next=current;next.event_count=8;
for(size_t i=0;i<8;i++){
next.events[i]=current.events[0];next.events[i].boot[0]=(char)('a'+i);next.events[i].boot[1]=0;
}
assert(vg_recovered_events_capture(&next,false,&view));saved_view=view;
for(size_t i=0;i<8;i++)assert(vg_recovered_event_json(&view,i,encoded,sizeof(encoded))==VG_REPLAY_ENCODED);
assert(view.event_count==8 && sizeof(view)<2048);
next.event_count=9;assert(!vg_recovered_events_capture(&next,false,&view));
assert(memcmp(&view,&saved_view,sizeof(view))==0);
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
