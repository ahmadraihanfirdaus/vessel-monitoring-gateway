#ifndef VG_OFFLINE_TRANSACTION_H
#define VG_OFFLINE_TRANSACTION_H

#include "offline_state.h"

typedef enum {
    VG_OFFLINE_READ_ABSENT = 0, VG_OFFLINE_READ_READY,
    VG_OFFLINE_READ_INVALID, VG_OFFLINE_READ_ERROR
} vg_offline_read_result;

typedef struct {
    void *context;
    vg_offline_read_result (*read)(void *, unsigned, uint8_t *, size_t, size_t *);
    bool (*write)(void *, unsigned, const uint8_t *, size_t);
    bool (*commit)(void *);
} vg_offline_io;

typedef struct {
    vg_offline_io io;
    bool ready;
    bool halted;
    bool degraded;
    int selected; /* -1 means both slots positively absent, not unreadable. */
    vg_offline_state current;
    vg_offline_state candidate;
    vg_offline_state scratch;
    uint8_t raw[2][VG_OFFLINE_SNAPSHOT_MAX];
} vg_offline_transaction;

/* Recovery is explicit. IO error or two invalid/ambiguous slots never becomes
 * empty initialization. Valid older data can be restored with degraded=true;
 * that does not establish absence of a newer committed/power-lost state. */
static inline bool vg_offline_recover(vg_offline_transaction *tx, vg_offline_io io,
    const char *device)
{
    if (!tx || !io.read || !io.write || !io.commit ||
        !vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !vg_offline_disjoint(tx, sizeof(*tx), device, strlen(device) + 1u)) return false;
    tx->ready = false;
    tx->halted = true;
    size_t lengths[2] = {0u, 0u};
    uint64_t generations[2] = {0u, 0u};
    bool valid[2] = {false, false};
    vg_offline_read_result status[2];
    for (unsigned i = 0u; i < 2u; ++i) {
        status[i] = io.read(io.context, i, tx->raw[i], sizeof(tx->raw[i]), &lengths[i]);
        if ((unsigned)status[i] >= (unsigned)VG_OFFLINE_READ_ERROR) return false;
        if (status[i] == VG_OFFLINE_READ_READY) {
            valid[i] = vg_offline_unpack(tx->raw[i], lengths[i], device, &tx->scratch, &tx->candidate);
            if (valid[i]) generations[i] = tx->candidate.generation;
        }
    }
    int selected = -1;
    if (valid[0] && valid[1]) {
        if (generations[0] == generations[1] &&
            (lengths[0] != lengths[1] || memcmp(tx->raw[0], tx->raw[1], lengths[0]))) return false;
        selected = generations[0] >= generations[1] ? 0 : 1;
    } else if (valid[0] || valid[1]) {
        selected = valid[0] ? 0 : 1;
    } else if (status[0] != VG_OFFLINE_READ_ABSENT || status[1] != VG_OFFLINE_READ_ABSENT) {
        return false;
    }
    if (selected >= 0) {
        if (!vg_offline_unpack(tx->raw[selected], lengths[selected], device, &tx->scratch, &tx->candidate)) return false;
    } else if (!vg_offline_init(&tx->candidate, device)) return false;
    tx->current = tx->candidate;
    tx->selected = selected;
    tx->io = io;
    tx->degraded = selected >= 0 && !(valid[0] && valid[1]);
    tx->halted = false;
    tx->ready = true;
    return true;
}

/* Candidate is already merged/validated. The selected slot is never written.
 * A failed write/commit/readback halts further writes until explicit recovery.
 * Memory publication occurs only after exact readback; SDK readback is not a
 * substitute for physical flash power-loss/durability tests. */
static inline bool vg_offline_publish(vg_offline_transaction *tx)
{
    if (!tx || !tx->ready || tx->halted || !tx->io.read || !tx->io.write || !tx->io.commit ||
        tx->current.generation == UINT64_MAX ||
        !vg_offline_valid(&tx->current, true) || !vg_offline_valid(&tx->candidate, false) ||
        strcmp(tx->current.device, tx->candidate.device) ||
        tx->candidate.generation != tx->current.generation + 1u ||
        tx->selected < -1 || tx->selected > 1 ||
        ((tx->current.generation == 0u) != (tx->selected == -1))) return false;
    if (tx->candidate.rejected_critical_attempts < tx->current.rejected_critical_attempts ||
        (!strcmp(tx->candidate.latest_boot, tx->current.latest_boot) &&
         tx->candidate.latest_sequence <= tx->current.latest_sequence)) return false;
    /* The transaction boundary also enforces retention; a future caller must
     * not bypass merge admission and accidentally publish journal deletion. */
    for (size_t i = 0u; i < tx->current.event_count; ++i) {
        bool found = false;
        for (size_t j = 0u; j < tx->candidate.event_count; ++j) {
            if (vg_offline_record_equal(&tx->current.events[i], &tx->candidate.events[j])) found = true;
        }
        if (!found) return false;
    }
    unsigned target = tx->selected == 0 ? 1u : 0u;
    size_t expected = 0u, actual = 0u;
    if (!vg_offline_pack(&tx->candidate, tx->raw[target], sizeof(tx->raw[target]), &expected)) return false;
    tx->halted = true;
    if (!tx->io.write(tx->io.context, target, tx->raw[target], expected) ||
        !tx->io.commit(tx->io.context) ||
        tx->io.read(tx->io.context, target, tx->raw[target ^ 1u], sizeof(tx->raw[target ^ 1u]), &actual) != VG_OFFLINE_READ_READY ||
        actual != expected || memcmp(tx->raw[target], tx->raw[target ^ 1u], expected)) return false;
    tx->current = tx->candidate;
    tx->selected = (int)target;
    tx->degraded = tx->current.generation == 1u;
    tx->halted = false;
    return true;
}

#endif
