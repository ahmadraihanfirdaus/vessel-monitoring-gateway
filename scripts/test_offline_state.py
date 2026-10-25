"""Actual C99 codec/merge checks; injected faults are not physical NVS evidence."""
import unittest
import struct
import zlib
from phase9_b4_testlib import compile_c

COMMON = r'''
#include "offline_state.h"
#include <stdio.h>
static vg_offline_state empty, current, next, scratch, restored, sentinel;
static vg_event_journal_t journal;
static uint8_t raw[VG_OFFLINE_SNAPSHOT_MAX], before[VG_OFFLINE_SNAPSHOT_MAX];
static void setup(void) {
    assert(vg_offline_init(&empty,"storage:demo"));
    assert(vg_journal_init(&journal));
    uint64_t id;
    assert(vg_journal_append(&journal,7u,1u,VG_SOURCE_SIMULATION,VG_EVENT_ALARM_RAISED,UINT64_MAX-1u,&id));
    assert(vg_offline_merge(&empty,"boot-a",UINT64_MAX-1u,"packet",6u,&journal,&current)==VG_OFFLINE_READY);
    memset(&sentinel,0xA5,sizeof(sentinel));
}
int main(void) {
    setup();
'''


class OfflineStateTest(unittest.TestCase):
    def c(self, source):
        # Static shared declarations are deliberately touched for strict -Werror.
        return compile_c(COMMON+'(void)next;(void)scratch;(void)restored;(void)raw;(void)before;\n'+source+'\nreturn 0;}\n', extra_flags=('-Os',))

    def test_roundtrip_preserves_64bit_identity_and_event_fields(self):
        self.c(r'''
size_t n=0u;assert(vg_offline_pack(&current,raw,sizeof(raw),&n));
assert(vg_offline_unpack(raw,n,"storage:demo",&scratch,&restored));
assert(restored.latest_sequence==UINT64_MAX-1u&&restored.generation==1u);
assert(restored.events[0].event.occurred_at_ms==UINT64_MAX-1u);
assert(restored.events[0].event.linked_alarm_id==7u);
assert(restored.events[0].event.event_id==1u&&restored.event_count==1u);
assert(restored.latest_length==6u&&!memcmp(restored.latest,"packet",6u));
assert(!strcmp(restored.events[0].boot,"boot-a"));
assert(vg_offline_merge(&restored,"boot-a",UINT64_MAX,"last",4u,&journal,&next)==VG_OFFLINE_READY);
assert(next.latest_sequence==UINT64_MAX&&next.event_count==1u);
''')

    def test_all_truncations_and_every_corrupted_byte_preserve_output(self):
        self.c(r'''
size_t n=0u;assert(vg_offline_pack(&current,raw,sizeof(raw),&n));restored=sentinel;
for(size_t cut=0u;cut<n;cut++) {
 assert(!vg_offline_unpack(raw,cut,"storage:demo",&scratch,&restored));
 assert(!memcmp(&restored,&sentinel,sizeof(restored)));
}
for(size_t i=0u;i<n;i++) {
 raw[i]^=1u;assert(!vg_offline_unpack(raw,n,"storage:demo",&scratch,&restored));raw[i]^=1u;
 assert(!memcmp(&restored,&sentinel,sizeof(restored)));
}
assert(!vg_offline_unpack(raw,n,"other-device",&scratch,&restored));
raw[n]=0u;assert(!vg_offline_unpack(raw,n+1u,"storage:demo",&scratch,&restored));
''')

    def test_recalculated_checksum_cannot_hide_invalid_schema_or_metadata(self):
        self.c(r'''
size_t n=0u;assert(vg_offline_pack(&current,raw,sizeof(raw),&n));memcpy(before,raw,n);
size_t positions[]={0u,4u,31u,32u,n-13u,n-14u};
for(size_t i=0u;i<sizeof(positions)/sizeof(positions[0]);i++) {
 memcpy(raw,before,n);raw[positions[i]]=255u;
 uint32_t crc=vg_b18_crc32(raw,n-4u);for(unsigned j=0u;j<4u;j++)raw[n-4u+j]=(uint8_t)(crc>>(j*8u));
 restored=sentinel;assert(!vg_offline_unpack(raw,n,"storage:demo",&scratch,&restored));
 assert(!memcmp(&restored,&sentinel,sizeof(restored)));
}
''')

    def test_queue_replacement_requires_a_valid_cumulative_critical_prefix(self):
        self.c(r'''
vg_event_journal_t later=journal;
assert(vg_offline_journal_follows(&journal,&later));
uint64_t id;assert(vg_journal_append(&later,7u,1u,VG_SOURCE_SIMULATION,VG_EVENT_ALARM_ACK,UINT64_MAX-1u,&id));
assert(vg_offline_journal_follows(&journal,&later));
assert(!vg_offline_journal_follows(&later,&journal));
later.events[0].source_id=9u;assert(!vg_offline_journal_follows(&journal,&later));
later=journal;later.events[0].source_mode=VG_SOURCE_PHYSICAL;
assert(!vg_offline_journal_follows(&journal,&later));
later=journal;later.count=VG_JOURNAL_CAPACITY+1u;assert(!vg_offline_journal_follows(&journal,&later));
assert(!vg_offline_journal_follows(NULL,&journal));
''')

    def test_maximum_packet_and_eight_cross_boot_events_without_eviction(self):
        self.c(r'''
uint64_t id;
for(unsigned i=1u;i<8u;i++)assert(vg_journal_append(&journal,7u,1u,VG_SOURCE_SIMULATION,VG_EVENT_ALARM_ACK,UINT64_MAX-1u,&id));
unsigned char packet[VG_OFFLINE_WIRE_MAX];memset(packet,123,sizeof(packet));
assert(vg_offline_merge(&current,"boot-b",0u,packet,sizeof(packet),&journal,&next)==VG_OFFLINE_CRITICAL_FULL);
assert(next.event_count==8u&&next.rejected_critical_attempts==1u);
assert(!strcmp(next.events[0].boot,"boot-a"));
for(size_t i=1u;i<8u;i++)assert(!strcmp(next.events[i].boot,"boot-b"));
size_t n=0u;assert(vg_offline_pack(&next,raw,sizeof(raw),&n));assert(n<=VG_OFFLINE_SNAPSHOT_MAX);
assert(vg_offline_unpack(raw,n,"storage:demo",&scratch,&restored));
assert(restored.latest_length==sizeof(packet)&&!memcmp(restored.latest,packet,sizeof(packet)));
assert(vg_offline_merge(&restored,"boot-c",0u,"new",3u,&journal,&current)==VG_OFFLINE_CRITICAL_FULL);
assert(current.event_count==8u&&current.rejected_critical_attempts==9u);
assert(current.latest_length==3u&&!memcmp(current.latest,"new",3u));
for(size_t i=0u;i<8u;i++)assert(vg_offline_event_equal(&current.events[i].event,&restored.events[i].event));
''')

    def test_conflicts_regressions_aliasing_and_generation_exhaustion_are_atomic(self):
        self.c(r'''
next=sentinel;
assert(vg_offline_merge(&current,"boot-a",UINT64_MAX-2u,"packet",6u,&journal,&next)==VG_OFFLINE_REJECTED);
assert(vg_offline_merge(&current,"boot-a",UINT64_MAX-1u,"changed",7u,&journal,&next)==VG_OFFLINE_REJECTED);
assert(vg_offline_merge(&current,"boot-a",UINT64_MAX-1u,"packet",6u,&journal,&next)==VG_OFFLINE_UNCHANGED);
journal.events[0].linked_alarm_id=8u;
assert(vg_offline_merge(&current,"boot-a",UINT64_MAX,"packet",6u,&journal,&next)==VG_OFFLINE_REJECTED);
assert(!memcmp(&next,&sentinel,sizeof(next)));
journal.events[0].linked_alarm_id=7u;
vg_event_journal_t omitted;assert(vg_journal_init(&omitted));
assert(vg_offline_merge(&current,"boot-a",UINT64_MAX,"packet",6u,&omitted,&next)==VG_OFFLINE_REJECTED);
assert(vg_offline_merge(&current,"boot-a",UINT64_MAX,"packet",6u,&journal,&current)==VG_OFFLINE_REJECTED);
current.generation=UINT64_MAX;
assert(vg_offline_merge(&current,"boot-b",1u,"packet",6u,&journal,&next)==VG_OFFLINE_REJECTED);
assert(!memcmp(&next,&sentinel,sizeof(next)));
''')

    def test_output_capacity_and_bad_source_fail_without_erasing_previous_bytes(self):
        self.c(r'''
size_t n=99u;memset(raw,0xA5,sizeof(raw));memcpy(before,raw,sizeof(raw));
assert(!vg_offline_pack(&current,raw,10u,&n));assert(n==99u&&!memcmp(raw,before,sizeof(raw)));
assert(!vg_offline_pack(&current,(uint8_t*)&current,sizeof(current),&n));
journal.events[0].source_mode=VG_SOURCE_PHYSICAL;next=sentinel;
assert(vg_offline_merge(&current,"boot-b",1u,"packet",6u,&journal,&next)==VG_OFFLINE_REJECTED);
assert(!memcmp(&next,&sentinel,sizeof(next)));
assert(!vg_offline_unpack(raw,sizeof(raw),"storage:demo",&restored,&restored));
''')

    def test_maximum_names_and_saturated_rejection_counter_have_exact_bounds(self):
        self.c(r'''
char device[49],boot[49];memset(device,'d',48u);device[48]=0;memset(boot,'b',48u);boot[48]=0;
assert(vg_offline_init(&empty,device));uint64_t id;
for(unsigned i=1u;i<8u;i++)assert(vg_journal_append(&journal,7u,1u,VG_SOURCE_SIMULATION,VG_EVENT_ALARM_ACK,UINT64_MAX-1u,&id));
uint8_t packet[VG_OFFLINE_WIRE_MAX];memset(packet,0x21,sizeof(packet));
assert(vg_offline_merge(&empty,boot,0u,packet,sizeof(packet),&journal,&current)==VG_OFFLINE_READY);
size_t n=0u;assert(vg_offline_pack(&current,raw,sizeof(raw),&n));assert(n==4862u);
assert(vg_offline_unpack(raw,n,device,&scratch,&restored));
restored.rejected_critical_attempts=UINT64_MAX;
assert(vg_offline_merge(&restored,"other-boot",0u,"new",3u,&journal,&next)==VG_OFFLINE_CRITICAL_FULL);
assert(next.rejected_critical_attempts==UINT64_MAX&&next.event_count==8u);
next=sentinel;assert(vg_offline_merge(&current,boot,1u,packet,sizeof(packet)+1u,&journal,&next)==VG_OFFLINE_REJECTED);
assert(!memcmp(&next,&sentinel,sizeof(next)));
''')

    def test_independent_python_crc_and_binary_field_oracle(self):
        text = self.c(r'''
size_t n=0u;assert(vg_offline_pack(&current,raw,sizeof(raw),&n));
for(size_t i=0u;i<n;i++)printf("%02x",(unsigned)raw[i]);
putchar('\n');
''')
        raw = bytes.fromhex(text.strip())
        self.assertEqual(raw[:5], b'VGS1\x01')
        self.assertEqual(struct.unpack_from('<QQQHB', raw, 5), (1, 2**64-2, 0, 6, 1))
        self.assertEqual(struct.unpack_from('<I', raw, len(raw)-4)[0], zlib.crc32(raw[:-4]))
        pos = 32
        for value in (b'storage:demo', b'boot-a'):
            self.assertEqual(raw[pos], len(value))
            self.assertEqual(raw[pos+1:pos+1+len(value)], value)
            pos += 1+len(value)
        self.assertEqual(raw[pos:pos+6], b'packet')
        pos += 6
        self.assertEqual(raw[pos:pos+7], b'\x06boot-a')
        pos += 7
        # Core enums currently encode SIMULATION=1, ALARM_RAISED=1.
        self.assertEqual(struct.unpack_from('<QQIBBQ', raw, pos), (1, 7, 1, 1, 1, 2**64-2))
        self.assertEqual(pos+30+4, len(raw))


if __name__ == '__main__':
    unittest.main(verbosity=2)
