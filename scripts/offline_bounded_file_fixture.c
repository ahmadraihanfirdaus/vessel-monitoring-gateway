/* SUP013: shared actual file IO + offline transaction, not physical durability. */
#define VG_CONTINUOUS_FIXTURE_DEVICE "runtime:demo"
#define main unused_continuous_fixture_main
#include "continuous_simulation_fixture.c"
#undef main
#include "host_offline_file_io.h"

static file_disk disk;
static vg_offline_transaction transaction;
static vg_continuous_simulation_t runtime;
static vg_offline_event original[VG_OFFLINE_EVENT_CAP];
static uint8_t retained_raw[VG_OFFLINE_SNAPSHOT_MAX];

static void persist(void)
{
    const vg_offline_merge_result result = vg_offline_merge_with_alarms(&transaction.current,
        runtime.config.boot, runtime.latest_sequence, runtime.latest_wire, runtime.latest_length,
        &runtime.journal, &runtime.alarm_journal, &transaction.candidate);
    assert(result == VG_OFFLINE_READY || result == VG_OFFLINE_CRITICAL_FULL);
    assert(vg_offline_publish(&transaction));
}

int main(int argc, char **argv)
{
    assert(argc == 2);
    for (unsigned i = 0u; i < 2u; ++i) {
        const int n = snprintf(disk.paths[i], sizeof(disk.paths[i]), "%s/offline-slot%u.bin", argv[1], i);
        assert(n > 0 && (size_t)n < sizeof(disk.paths[i]));
    }
    const vg_offline_io io = {&disk, file_read, file_write, file_commit};
    assert(vg_offline_recover(&transaction, io, "runtime:demo"));
    assert(transaction.current.generation == 0u && transaction.selected == -1);
    vg_continuous_config_t config = test_config();
    strcpy(config.boot, "bounded-boot-a");
    assert(vg_continuous_init(&runtime, &config, 200u));
    bool full = false;
    for (unsigned i = 1u; i <= 64u; ++i) {
        assert(vg_continuous_poll(&runtime, (uint64_t)i * 200u) == VG_CONTINUOUS_ENCODED);
        persist();
        assert(vg_offline_recover(&transaction, io, "runtime:demo"));
        assert(transaction.current.generation == i && transaction.current.latest_sequence == i);
        assert(transaction.current.latest_length == runtime.latest_length);
        assert(!memcmp(transaction.current.latest, runtime.latest_wire, runtime.latest_length));
        if (!full && transaction.current.event_count == VG_OFFLINE_EVENT_CAP) {
            memcpy(original, transaction.current.events, sizeof(original));
            full = true;
        }
        if (full) {
            assert(transaction.current.event_count == VG_OFFLINE_EVENT_CAP);
            for (size_t j = 0u; j < VG_OFFLINE_EVENT_CAP; ++j)
                assert(vg_offline_record_equal(&original[j], &transaction.current.events[j]));
        }
    }
    assert(full && runtime.journal.rejected_full > 0u);
    const uint64_t ram_rejected = runtime.journal.rejected_full;
    /* A distinct new boot fills only latest state; old critical facts have no
     * authenticated receipt and cannot be removed to make room for new facts. */
    strcpy(config.boot, "bounded-boot-b");
    assert(vg_continuous_init(&runtime, &config, 200u));
    for (unsigned i = 1u; i <= 8u; ++i) {
        assert(vg_continuous_poll(&runtime, (uint64_t)i * 200u) == VG_CONTINUOUS_ENCODED);
        persist();
        assert(vg_offline_recover(&transaction, io, "runtime:demo"));
        assert(transaction.current.generation == 64u + i && transaction.current.latest_sequence == i);
        assert(!strcmp(transaction.current.latest_boot, "bounded-boot-b"));
        assert(transaction.current.event_count == VG_OFFLINE_EVENT_CAP);
        for (size_t j = 0u; j < VG_OFFLINE_EVENT_CAP; ++j)
            assert(vg_offline_record_equal(&original[j], &transaction.current.events[j]));
    }
    assert(transaction.current.rejected_critical_attempts > 0u && transaction.current.confirmed_event_id == 0u);
    /* Actual owned older-file corruption: latest selected file is untouched. */
    const unsigned older = (unsigned)transaction.selected ^ 1u;
    size_t raw_length = 0u;
    assert(file_read(&disk, older, retained_raw, sizeof(retained_raw), &raw_length) == VG_OFFLINE_READ_READY);
    retained_raw[0] ^= 1u;
    assert(file_write(&disk, older, retained_raw, raw_length) && file_commit(&disk));
    assert(vg_offline_recover(&transaction, io, "runtime:demo"));
    assert(transaction.current.generation == 72u && transaction.degraded);
    /* Restore only this test-owned corrupt byte, then demand valid healthy
     * reopen. No repair, erase or hidden empty initialization in the library. */
    retained_raw[0] ^= 1u;
    assert(file_write(&disk, older, retained_raw, raw_length) && file_commit(&disk));
    assert(vg_offline_recover(&transaction, io, "runtime:demo") && !transaction.degraded);
    assert(transaction.current.generation == 72u && transaction.current.event_count == 8u);
    printf("{\"generation\":72,\"latest_sequence\":8,\"retained\":%u,"
        "\"ram_rejected\":%llu,\"disk_rejected\":%llu,\"confirmed_floor\":%llu,"
        "\"older_corruption_preserved_latest\":true,\"healthy_reopen\":true,"
        "\"original_first_id\":%llu,\"original_last_id\":%llu}\n",
        (unsigned)transaction.current.event_count, (unsigned long long)ram_rejected,
        (unsigned long long)transaction.current.rejected_critical_attempts,
        (unsigned long long)transaction.current.confirmed_event_id,
        (unsigned long long)original[0].event.event_id,
        (unsigned long long)original[7].event.event_id);
    assert(transaction.current.latest_length <= sizeof(transaction.current.latest));
    assert(fwrite(transaction.current.latest, 1u, transaction.current.latest_length, stdout) == transaction.current.latest_length);
    putchar('\n');
    return 0;
}
