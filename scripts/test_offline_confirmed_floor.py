"""Actual VGS3 codec/merge bounds; synthetic floors do not authorize live deletion."""
import struct
import unittest
import zlib
from phase9_b4_testlib import compile_c
from test_alarm_offline_metadata import BASE
from test_offline_transaction import COMMON as TRANSACTION_SETUP

FLOOR = r'''
/* Synthetic codec state only. Runtime retirement must authenticate separately. */
current.events[0]=current.events[1];current.events[1]=current.events[2];current.event_count=2;
current.confirmed_event_id=1;assert(vg_offline_valid(&current,false));
'''


class OfflineConfirmedFloorTest(unittest.TestCase):
    def c(self, source, floor=True):
        return compile_c(BASE+(FLOOR if floor else '')+source+'\nreturn 0;}\n', extra_flags=('-Os',))

    def test_independent_vgs3_bytes_crc_metadata_zero_null_and_floor(self):
        raw = bytes.fromhex(self.c(r'''
assert(vg_offline_pack(&current,raw,sizeof(raw),&length));
for(size_t i=0;i<length;i++){printf("%02x",raw[i]);}puts("");
assert(vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));
assert(restored.confirmed_event_id==1 && restored.event_count==2);
assert(restored.events[0].alarm.has_acknowledged_at && restored.events[0].alarm.acknowledged_at==0);
assert(!restored.events[0].alarm.has_cleared_at);
''').strip())
        string = lambda value: bytes([len(value)])+value
        expected = struct.pack('<IBQQQQHB', 0x33534756, 3, 1, 1, 42, 0, 6, 2)
        expected += string(b'alarm:demo')+string(b'boot-a')+b'packet'
        for event_id, state, occurred, flags in ((2, 2, 0, 1), (3, 3, 100, 3)):
            expected += string(b'boot-a')+struct.pack('<QQIBBQ', event_id, 1, 7, 1, state, occurred)
            expected += struct.pack('<BIIBQQQB', 1, 3, 1001, state, 0, 0, 100 if state == 3 else 0, flags)
        expected += struct.pack('<I', zlib.crc32(expected))
        self.assertEqual(raw, expected)

    def test_every_truncation_corruption_and_rechecksummed_invalid_floor_preserves_output(self):
        self.c(r'''
assert(vg_offline_pack(&current,raw,sizeof(raw),&length));memcpy(saved,raw,length);
memset(&sentinel,0xa5,sizeof(sentinel));restored=sentinel;
for(size_t n=0;n<length;n++){
assert(!vg_offline_unpack(raw,n,"alarm:demo",&scratch,&restored));assert(!memcmp(&restored,&sentinel,sizeof(restored)));
}
for(size_t i=0;i<length;i++){
raw[i]^=1;assert(!vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));raw[i]^=1;
assert(!memcmp(&restored,&sentinel,sizeof(restored)));
}
uint64_t invalid[3]={0,2,UINT64_MAX};
for(size_t k=0;k<3;k++){
memcpy(raw,saved,length);for(unsigned i=0;i<8;i++)raw[13u+i]=(uint8_t)(invalid[k]>>(8u*i));
vg_b18_writer trailer={raw+length-4u,4u,0u,true};vg_b18_w32(&trailer,vg_b18_crc32(raw,length-4u));
assert(!vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));assert(!memcmp(&restored,&sentinel,sizeof(restored)));
}
''')

    def test_confirmed_prefix_cannot_resurrect_from_cumulative_same_boot_submissions(self):
        self.c(r'''
assert(vg_offline_merge_with_alarms(&current,"boot-a",43,"next",4,&journal,&metadata,&next)==VG_OFFLINE_READY);
assert(next.confirmed_event_id==1 && next.event_count==2);
for(size_t i=0;i<next.event_count;i++)assert(next.events[i].event.event_id>1);
memset(&alarm,0,sizeof(alarm));assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1002,101));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,101,&id));
assert(vg_offline_merge_with_alarms(&current,"boot-a",44,"later",5,&journal,&metadata,&next)==VG_OFFLINE_READY);
assert(next.confirmed_event_id==1 && next.event_count==3 && next.events[2].event.event_id==4);
''')

    def test_new_boot_resets_only_scoped_floor_and_preserves_other_retained_facts(self):
        self.c(r'''
assert(vg_offline_merge_with_alarms(&current,"boot-b",1,"new",3,&journal,&metadata,&next)==VG_OFFLINE_READY);
assert(next.confirmed_event_id==0 && next.event_count==5);
assert(!strcmp(next.events[0].boot,"boot-a") && next.events[0].event.event_id==2);
assert(!strcmp(next.events[2].boot,"boot-b") && next.events[2].event.event_id==1);
assert(vg_offline_pack(&next,raw,sizeof(raw),&length));assert(raw[3]=='2'&&raw[4]==2);
''')

    def test_vgs3_supports_unknown_or_no_retained_metadata_without_inventing_it(self):
        self.c(r'''
for(size_t i=0;i<current.event_count;i++){current.events[i].has_alarm=false;memset(&current.events[i].alarm,0,sizeof(current.events[i].alarm));}
assert(vg_offline_pack(&current,raw,sizeof(raw),&length));assert(raw[3]=='3');
assert(vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));assert(!restored.events[0].has_alarm);
current.event_count=0;
assert(vg_offline_pack(&current,raw,sizeof(raw),&length));
assert(vg_offline_unpack(raw,length,"alarm:demo",&scratch,&restored));
assert(restored.event_count==0 && restored.confirmed_event_id==1);
''')

    def test_maximum_vgs3_5150_bytes_fits_unchanged_5184_allocation(self):
        self.c(r'''
char device[49],boot[49];memset(device,'d',48);device[48]=0;memset(boot,'b',48);boot[48]=0;
assert(vg_offline_init(&empty,device));assert(vg_journal_init(&journal));journal.next_id=2;
memset(&metadata,0,sizeof(metadata));vg_alarm_id_allocator_init(&ids);
for(unsigned i=0;i<8;i++){
memset(&alarm,0,sizeof(alarm));assert(vg_alarm_try_raise(&ids,&alarm,7,VG_SOURCE_SIMULATION,3,1001,i));
assert(vg_alarm_journal_append(&journal,&metadata,&alarm,VG_EVENT_ALARM_RAISED,i,&id));
}
static char body[4096];memset(body,'p',sizeof(body));
assert(vg_offline_merge_with_alarms(&empty,boot,1,body,sizeof(body),&journal,&metadata,&current)==VG_OFFLINE_READY);
current.confirmed_event_id=1;memset(raw,0x37,sizeof(raw));memcpy(saved,raw,sizeof(raw));
assert(VG_OFFLINE_SNAPSHOT_MAX==5184);
assert(!vg_offline_pack(&current,raw,5149,&length));assert(!memcmp(raw,saved,sizeof(raw)));
assert(vg_offline_pack(&current,raw,5150,&length));assert(length==5150);
assert(vg_offline_unpack(raw,length,device,&scratch,&restored));assert(restored.event_count==8 && restored.confirmed_event_id==1);
''', floor=False)

    def test_ordinary_publication_cannot_invent_or_advance_floor(self):
        compile_c(TRANSACTION_SETUP+r'''
assert(vg_journal_init(&journal));
assert(vg_offline_merge(&tx.current,"boot-b",1,"new",3,&journal,&tx.candidate)==VG_OFFLINE_READY);
unsigned writes=d.writes;tx.candidate.confirmed_event_id=1;
assert(vg_offline_valid(&tx.candidate,false));assert(!vg_offline_publish(&tx));assert(d.writes==writes);
tx.candidate.confirmed_event_id=0;assert(vg_offline_publish(&tx));writes=d.writes;
assert(vg_offline_merge(&tx.current,"boot-b",2,"newer",5,&journal,&tx.candidate)==VG_OFFLINE_READY);
tx.candidate.confirmed_event_id=1;assert(vg_offline_valid(&tx.candidate,false));
assert(!vg_offline_publish(&tx));assert(d.writes==writes && tx.current.confirmed_event_id==0);
return 0;}
''', extra_flags=('-Os',))


if __name__ == '__main__':
    unittest.main(verbosity=2)
