"""Real native VGS2/legacy/publish checks with independent Python byte oracle."""
import struct
import unittest
import zlib
from phase9_b4_testlib import compile_c
from test_offline_transaction import COMMON as TRANSACTION_SETUP

BASE = r'''
#include "offline_transaction.h"
static vg_event_journal_t journal;
static vg_alarm_journal_t metadata;
static vg_alarm_id_allocator_t ids;
static vg_alarm_t alarm;
static vg_offline_state empty,current,next,scratch,restored,sentinel;
static uint8_t raw[VG_OFFLINE_SNAPSHOT_MAX],saved[VG_OFFLINE_SNAPSHOT_MAX];
static size_t length;
int main(void) {
assert(vg_journal_init(&journal));vg_alarm_id_allocator_init(&ids);
assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,0));uint64_t id;
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&id));
assert(vg_alarm_try_acknowledge(&alarm,0));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,0,&id));
assert(vg_alarm_try_clear_condition(&alarm,100));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_CLEARED,100,&id));
assert(vg_offline_init(&empty,"alarm:demo"));
assert(vg_offline_merge_with_alarms(&empty,"boot-a",42,"packet",6,&journal,&metadata,&current)==VG_OFFLINE_READY);
assert(vg_offline_valid(&current,false));
(void)next;(void)scratch;(void)restored;(void)sentinel;(void)raw;(void)saved;(void)length;
'''


class AlarmOfflineMetadataTest(unittest.TestCase):
    def c(self, source):
        return compile_c(BASE+source+'\nreturn 0;}\n', extra_flags=('-Os',))

    def test_independent_vgs2_layout_crc_and_zero_vs_null_flags(self):
        raw = bytes.fromhex(self.c(r'''
assert(vg_offline_pack(&current,raw,sizeof(raw),&length));
for(size_t i=0;i<length;i++){printf("%02x",raw[i]);}
puts("");
assert(vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));
for(size_t i=0;i<3;i++)assert(restored.events[i].has_alarm&&vg_alarm_metadata_equal(&restored.events[i].alarm,&metadata.entries[i].alarm));
assert(!restored.events[0].alarm.has_acknowledged_at&&restored.events[1].alarm.has_acknowledged_at);
''').strip())
        string = lambda value: bytes([len(value)])+value
        expected = struct.pack('<IBQQQHB', 0x32534756, 2, 1, 42, 0, 6, 3)
        expected += string(b'alarm:demo')+string(b'boot-a')+b'packet'
        for index, (state, occurred, flags) in enumerate(((1, 0, 0), (2, 0, 1), (3, 100, 3))):
            expected += string(b'boot-a')+struct.pack('<QQIBBQ', index+1, 1, 7, 1, state, occurred)
            expected += struct.pack('<BIIBQQQB', 1, 3, 1001, state, 0, 0, 100 if state == 3 else 0, flags)
        expected += struct.pack('<I', zlib.crc32(expected))
        self.assertEqual(raw, expected)

    def test_all_truncations_corrupt_bytes_and_forged_flags_preserve_output(self):
        self.c(r'''
assert(vg_offline_pack(&current,raw,sizeof(raw),&length));memset(&sentinel,0xA5,sizeof(sentinel));restored=sentinel;
for(size_t cut=0;cut<length;cut++){
 assert(!vg_offline_unpack(raw,cut,"alarm:demo",&scratch,&restored));assert(!memcmp(&restored,&sentinel,sizeof(restored)));
}
for(size_t i=0;i<length;i++){
 raw[i]^=1;assert(!vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));raw[i]^=1;
 assert(!memcmp(&restored,&sentinel,sizeof(restored)));
}
memcpy(saved,raw,length);raw[length-5u]=4u;
vg_b18_writer trailer={raw+length-4u,4u,0u,true};vg_b18_w32(&trailer,vg_b18_crc32(raw,length-4u));
assert(!vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));
assert(!memcmp(&restored,&sentinel,sizeof(restored)));
memcpy(raw,saved,length);current.events[0].alarm.reason_code=0;memcpy(saved,raw,sizeof(raw));
assert(!vg_offline_pack(&current,raw,sizeof(raw),&length));assert(!memcmp(raw,saved,sizeof(raw)));
''')

    def test_legacy_bytes_remain_vgs1_and_unknown_history_is_not_reconstructed(self):
        self.c(r'''
assert(vg_offline_merge(&empty,"boot-a",42,"packet",6,&journal,&next)==VG_OFFLINE_READY);
assert(vg_offline_pack(&next,raw,sizeof(raw),&length));assert(raw[3]=='1'&&raw[4]==1);
assert(vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));
assert(!restored.events[0].has_alarm&&!restored.events[1].has_alarm&&!restored.events[2].has_alarm);
sentinel=current;
assert(vg_offline_merge_with_alarms(&restored,"boot-a",43,"new",3,&journal,&metadata,&current)==VG_OFFLINE_REJECTED);
assert(!memcmp(&current,&sentinel,sizeof(current)));
/* Legacy submission preserves already retained complete metadata. */
assert(vg_offline_merge(&current,"boot-a",43,"new",3,&journal,&next)==VG_OFFLINE_READY);
for(size_t i=0;i<3;i++)assert(next.events[i].has_alarm&&vg_alarm_metadata_equal(&next.events[i].alarm,&current.events[i].alarm));
/* A new boot may add complete records alongside explicit unknown old facts. */
assert(vg_offline_merge_with_alarms(&restored,"boot-b",1,"new",3,&journal,&metadata,&next)==VG_OFFLINE_READY);
assert(next.event_count==6&&!next.events[0].has_alarm&&next.events[3].has_alarm);
assert(vg_offline_pack(&next,raw,sizeof(raw),&length));
assert(vg_offline_unpack(raw,length,"alarm:demo",&scratch,&current));
assert(!current.events[0].has_alarm&&current.events[3].has_alarm);
''')

    def test_full_metadata_identity_conflict_and_aliases_fail_before_output_mutation(self):
        self.c(r'''
sentinel=next;metadata.entries[0].alarm.reason_code++;
assert(vg_offline_merge_with_alarms(&current,"boot-a",43,"new",3,&journal,&metadata,&next)==VG_OFFLINE_REJECTED);
assert(!memcmp(&next,&sentinel,sizeof(next)));
metadata.entries[0].alarm.reason_code--;
assert(vg_offline_merge_with_alarms(&current,"boot-a",43,"new",3,&journal,&metadata,&current)==VG_OFFLINE_REJECTED);
assert(vg_offline_merge_with_alarms(&current,"boot-a",42,"packet",6,&journal,&metadata,&next)==VG_OFFLINE_UNCHANGED);
''')

    def test_worst_case_exact_5142_bound_and_legacy_4862_bound(self):
        self.c(r'''
char device[49],boot[49];memset(device,'d',48);device[48]=0;memset(boot,'b',48);boot[48]=0;
assert(vg_offline_init(&empty,device));assert(vg_journal_init(&journal));memset(&metadata,0,sizeof(metadata));
vg_alarm_id_allocator_init(&ids);
for(unsigned i=0;i<8;i++){
 memset(&alarm,0,sizeof(alarm));assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,i));
 assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,i,&id));
}
static char body[4096];memset(body,'p',sizeof(body));
assert(vg_offline_merge_with_alarms(&empty,boot,1,body,sizeof(body),&journal,&metadata,&current)==VG_OFFLINE_READY);
memset(raw,0x37,sizeof(raw));memcpy(saved,raw,sizeof(raw));
assert(!vg_offline_pack(&current,raw,5141,&length));assert(!memcmp(raw,saved,sizeof(raw)));
assert(vg_offline_pack(&current,raw,sizeof(raw),&length));assert(length==5142);
assert(vg_offline_unpack(raw,length,device,&scratch,&restored));assert(restored.event_count==8);
assert(vg_offline_merge(&empty,boot,1,body,sizeof(body),&journal,&next)==VG_OFFLINE_READY);
assert(vg_offline_pack(&next,raw,sizeof(raw),&length));assert(length==4862&&raw[3]=='1');
''')

    def test_transaction_cannot_delete_or_mutate_retained_metadata(self):
        source = TRANSACTION_SETUP+r'''
vg_alarm_journal_t metadata={0};vg_alarm_t alarm={0};vg_alarm_id_allocator_t ids;vg_alarm_id_allocator_init(&ids);
assert(vg_journal_init(&journal));uint64_t id;
assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,20));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,20,&id));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-b",1,"new",3,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));assert(tx.current.events[1].has_alarm);
unsigned writes=d.writes;
tx.candidate=tx.current;tx.candidate.generation++;tx.candidate.latest_sequence++;tx.candidate.events[1].has_alarm=false;
assert(!vg_offline_publish(&tx)&&d.writes==writes);
tx.candidate=tx.current;tx.candidate.generation++;tx.candidate.latest_sequence++;tx.candidate.events[1].alarm.priority_code++;
assert(!vg_offline_publish(&tx)&&d.writes==writes);
assert(vg_offline_merge(&tx.current,"boot-b",2,"next",4,&journal,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));assert(vg_offline_recover(&tx,io,"disk:demo"));
assert(tx.current.events[1].has_alarm&&tx.current.events[1].alarm.priority_code==3);
return 0;}
'''
        compile_c(source, extra_flags=('-Os',))

    def test_every_vgs2_partial_write_preserves_selected_metadata_and_state(self):
        source = TRANSACTION_SETUP+r'''
memset(&d,0,sizeof(d));d.cut=SIZE_MAX;memset(&tx,0,sizeof(tx));
assert(vg_offline_recover(&tx,io,"disk:demo"));assert(vg_journal_init(&journal));
vg_alarm_journal_t metadata={0};vg_alarm_t alarm={0};vg_alarm_id_allocator_t ids;vg_alarm_id_allocator_init(&ids);uint64_t id;
assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,0));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&id));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-meta",1,"first",5,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));baseline=d;sentinel=tx.current;
static uint8_t body[4096];memset(body,0x37,sizeof(body));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-meta",2,body,sizeof(body),&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
size_t n;assert(vg_offline_pack(&tx.candidate,tx.raw[1],sizeof(tx.raw[1]),&n));assert(tx.raw[1][3]=='2');
for(size_t cut=0;cut<n;cut++){
 d=baseline;assert(vg_offline_recover(&tx,io,"disk:demo"));
 assert(vg_offline_merge_with_alarms(&tx.current,"boot-meta",2,body,sizeof(body),&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
 d.cut=cut;d.fail_write=true;assert(!vg_offline_publish(&tx)&&tx.halted);
 assert(!memcmp(&tx.current,&sentinel,sizeof(sentinel))&&!memcmp(d.bytes[0],baseline.bytes[0],baseline.length[0]));
 d.cut=SIZE_MAX;d.fail_write=false;assert(vg_offline_recover(&tx,io,"disk:demo"));
 assert(tx.current.generation==1&&tx.current.events[0].has_alarm&&tx.current.events[0].alarm.raised_at==0);
}
return 0;}
'''
        compile_c(source, extra_flags=('-Os',))

    def test_metadata_queue_prefix_and_sdk_contract_refuse_downgrade(self):
        self.c(r'''
vg_alarm_journal_t prefix=metadata;assert(vg_alarm_journal_follows(&prefix,&metadata));
metadata.entries[0].alarm.priority_code++;assert(!vg_alarm_journal_follows(&prefix,&metadata));
metadata=prefix;metadata.count--;assert(!vg_alarm_journal_follows(&prefix,&metadata));
metadata=prefix;metadata.entries[2].alarm.cleared_at++;assert(!vg_alarm_journal_follows(&prefix,&metadata));
''')
        from pathlib import Path
        sdk = (Path(__file__).resolve().parents[1]/'firmware/src/esp32_offline_store.c').read_text(encoding='utf-8')
        for required in ('vg_offline_merge_with_alarms', 'vg_alarm_journal_follows',
                         'storage->accepted_has_metadata && (!metadata',
                         'metadata && !storage->accepted_has_metadata && storage->accepted_journal.count != 0u',
                         'xSemaphoreTake(storage->lock, 0)'):
            self.assertIn(required, sdk)
        self.assertNotIn('nvs_flash_erase(', sdk)

    def test_uncertain_vgs2_commit_exposes_new_ack_only_after_explicit_recovery(self):
        source = TRANSACTION_SETUP+r'''
vg_alarm_journal_t metadata={0};vg_alarm_t alarm={0};vg_alarm_id_allocator_t ids;vg_alarm_id_allocator_init(&ids);
assert(vg_journal_init(&journal));uint64_t id;
assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,0));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,0,&id));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-meta",1,"first",5,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
assert(vg_offline_publish(&tx));sentinel=tx.current;
assert(vg_alarm_try_acknowledge(&alarm,100));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_ACK,100,&id));
assert(vg_offline_merge_with_alarms(&tx.current,"boot-meta",2,"second",6,&journal,&metadata,&tx.candidate)==VG_OFFLINE_READY);
d.fail_commit=true;assert(!vg_offline_publish(&tx)&&tx.halted);
assert(!memcmp(&tx.current,&sentinel,sizeof(sentinel))&&tx.current.event_count==2);
d.fail_commit=false;assert(vg_offline_recover(&tx,io,"disk:demo"));
assert(tx.current.generation==3&&tx.current.event_count==3);
assert(tx.current.events[2].has_alarm&&tx.current.events[2].alarm.state==VG_ALARM_STATE_ACTIVE_ACK);
assert(tx.current.events[2].alarm.has_acknowledged_at&&tx.current.events[2].alarm.acknowledged_at==100);
assert(!tx.current.events[2].alarm.has_cleared_at);
return 0;}
'''
        compile_c(source, extra_flags=('-Os',))


if __name__ == '__main__':
    unittest.main(verbosity=2)
