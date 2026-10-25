#ifndef VG_OFFLINE_RETIREMENT_H
#define VG_OFFLINE_RETIREMENT_H

#include "offline_transaction.h"
#include "offline_replay.h"
#include "event_commit_receipt.h"

typedef struct {
    void *context;
    bool (*verify)(void *, const void *, size_t, int, const void *, size_t, uint8_t [32]);
} vg_event_receipt_verifier;

typedef enum {
    VG_RETIRE_REJECTED = 0, VG_RETIRE_COMMITTED,
    VG_RETIRE_ALREADY_CONFIRMED, VG_RETIRE_IO_HALTED
} vg_offline_retire_result;

/* Volatile prefix release only after the caller has durable confirmation.
 * Full identity/metadata must match the first retained record. Preserve next ID,
 * last observation time and refusal counters; never mutate the live alarm. */
static inline bool vg_offline_release_confirmed_prefix(vg_event_journal_t *journal,
    vg_alarm_journal_t *metadata, const vg_offline_event *confirmed)
{
    if (!vg_offline_record_valid(confirmed) || !vg_offline_journal_follows(journal, journal) ||
        journal->count == 0u || !vg_offline_event_equal(&journal->events[0], &confirmed->event) ||
        !vg_offline_disjoint(journal, sizeof(*journal), confirmed, sizeof(*confirmed))) return false;
    if (metadata) {
        if (!confirmed->has_alarm || !vg_alarm_journal_matches(metadata, journal) ||
            !vg_alarm_metadata_equal(&metadata->entries[0].alarm, &confirmed->alarm) ||
            !vg_offline_disjoint(metadata, sizeof(*metadata), confirmed, sizeof(*confirmed)) ||
            !vg_offline_disjoint(metadata, sizeof(*metadata), journal, sizeof(*journal))) return false;
    } else if (confirmed->has_alarm) return false;
    size_t count = journal->count;
    for (size_t i = 1u; i < count; ++i) {
        journal->events[i - 1u] = journal->events[i];
        if (metadata) metadata->entries[i - 1u] = metadata->entries[i];
    }
    --journal->count;
    memset(&journal->events[journal->count], 0, sizeof(journal->events[0]));
    if (metadata) {
        --metadata->count;
        memset(&metadata->entries[metadata->count], 0, sizeof(metadata->entries[0]));
    }
    return true;
}

/* A running owner may reconcile a durable floor, but a fresh owner must use
 * a new boot identity rather than reusing an existing persisted namespace. */
static inline bool vg_offline_recovery_owner_valid(const vg_offline_state *state,
    const char *boot, bool already_owned)
{
    if (!vg_offline_valid(state, true) || !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN)) return false;
    if (already_owned || state->generation == 0u) return true;
    if (!strcmp(state->latest_boot, boot)) return false;
    for (size_t i = 0u; i < state->event_count; ++i)
        if (!strcmp(state->events[i].boot, boot)) return false;
    return true;
}

/* Caller holds its admission lock and supplies an already-confirmed floor.
 * Validate all inputs before mutation; working is a distinct bounded record. */
static inline bool vg_offline_strip_confirmed_prefix(vg_event_journal_t *journal,
    vg_alarm_journal_t *metadata, const char *boot, uint64_t floor, vg_offline_event *working)
{
    if (!vg_offline_journal_follows(journal, journal) || !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN) ||
        floor == UINT64_MAX || !working ||
        !vg_offline_disjoint(journal, sizeof(*journal), working, sizeof(*working)) ||
        !vg_offline_disjoint(journal, sizeof(*journal), boot, strlen(boot) + 1u) ||
        !vg_offline_disjoint(working, sizeof(*working), boot, strlen(boot) + 1u)) return false;
    if (metadata && (!vg_alarm_journal_matches(metadata, journal) ||
        !vg_offline_disjoint(metadata, sizeof(*metadata), journal, sizeof(*journal)) ||
        !vg_offline_disjoint(metadata, sizeof(*metadata), working, sizeof(*working)) ||
        !vg_offline_disjoint(metadata, sizeof(*metadata), boot, strlen(boot) + 1u))) return false;
    while (journal->count != 0u && journal->events[0].event_id <= floor) {
        memset(working, 0, sizeof(*working));
        memcpy(working->boot, boot, strlen(boot) + 1u);
        working->event = journal->events[0];
        if (metadata) { working->has_alarm = true; working->alarm = metadata->entries[0].alarm; }
        if (!vg_offline_release_confirmed_prefix(journal, metadata, working)) return false;
    }
    return true;
}

/* Queue admission only, not authentication. Unknown current-prefix requests
 * wait for normal state admission rather than starving the worker's state job. */
static inline bool vg_offline_receipt_queue_admissible(const vg_event_journal_t *accepted,
    const vg_alarm_journal_t *metadata, const char *boot, uint64_t floor, const vg_offline_event *record)
{
    if (!vg_offline_record_valid(record) || !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN) ||
        floor == UINT64_MAX || !vg_offline_journal_follows(accepted, accepted) ||
        (metadata && !vg_alarm_journal_matches(metadata, accepted))) return false;
    if (strcmp(record->boot, boot) || record->event.event_id <= floor) return true;
    for (size_t i = 0u; i < accepted->count; ++i) {
        if (accepted->events[i].event_id <= floor) continue;
        return vg_offline_event_equal(&accepted->events[i], &record->event) &&
            (metadata ? (record->has_alarm && vg_alarm_metadata_equal(&metadata->entries[i].alarm, &record->alarm))
                      : !record->has_alarm);
    }
    return false;
}

/* Exact immutable record + cryptographically verified receipt. The SDK binds
 * the callback to actual PSA/profile verification; it is not a success flag.
 * Working buffer may change on refusal; published state/IO never do. Accepted
 * prefix is required for current-boot facts, including full-storage refusals. */
static inline vg_offline_retire_result vg_offline_retire(vg_offline_transaction *tx,
    const char *current_boot, const vg_offline_event *record,
    const vg_event_journal_t *accepted, const vg_alarm_journal_t *metadata,
    const vg_event_receipt_verifier *verifier, int status, const void *receipt, size_t receipt_length,
    char *working, size_t capacity)
{
    if (!tx || !tx->ready || tx->halted || !tx->io.read || !tx->io.write || !tx->io.commit ||
        !vg_offline_valid(&tx->current, false) || tx->current.generation == UINT64_MAX ||
        tx->selected < 0 || tx->selected > 1 ||
        !vg_tel_safe_token(current_boot, VG_TELEMETRY_MAX_ID_LEN) ||
        strcmp(current_boot, tx->current.latest_boot) || !vg_offline_record_valid(record) ||
        !verifier || !verifier->verify || !receipt || receipt_length != VG_EVENT_RECEIPT_LENGTH ||
        (status != 200 && status != 201) || !working || capacity == 0u || capacity > VG_OFFLINE_WIRE_MAX + 1u ||
        !vg_offline_disjoint(tx, sizeof(*tx), record, sizeof(*record)) ||
        !vg_offline_disjoint(tx, sizeof(*tx), receipt, receipt_length) ||
        !vg_offline_disjoint(tx, sizeof(*tx), current_boot, strlen(current_boot) + 1u) ||
        !vg_offline_disjoint(tx, sizeof(*tx), verifier, sizeof(*verifier)) ||
        !vg_offline_disjoint(tx, sizeof(*tx), working, capacity) ||
        !vg_offline_disjoint(record, sizeof(*record), working, capacity) ||
        !vg_offline_disjoint(receipt, receipt_length, working, capacity) ||
        !vg_offline_disjoint(current_boot, strlen(current_boot) + 1u, working, capacity) ||
        !vg_offline_disjoint(verifier, sizeof(*verifier), working, capacity)) return VG_RETIRE_REJECTED;
    bool current = !strcmp(current_boot, record->boot);
    bool covered = current && !strcmp(current_boot, tx->current.latest_boot) &&
        record->event.event_id <= tx->current.confirmed_event_id;
    size_t found = tx->current.event_count;
    for (size_t i = 0u; i < tx->current.event_count; ++i) {
        const vg_offline_event *stored = &tx->current.events[i];
        if (!strcmp(stored->boot, record->boot)) {
            if (current && !covered && stored->event.event_id < record->event.event_id)
                return VG_RETIRE_REJECTED;
            if (stored->event.event_id == record->event.event_id) {
                if (!vg_offline_record_equal(stored, record)) return VG_RETIRE_REJECTED;
                found = i;
            }
        }
    }
    if (current && !covered) {
        if (strcmp(current_boot, tx->current.latest_boot) || !accepted ||
            !vg_offline_journal_follows(accepted, accepted) ||
            !vg_offline_disjoint(tx, sizeof(*tx), accepted, sizeof(*accepted)) ||
            !vg_offline_disjoint(working, capacity, accepted, sizeof(*accepted))) return VG_RETIRE_REJECTED;
        if (metadata) {
            if (!vg_alarm_journal_matches(metadata, accepted) ||
                !vg_offline_disjoint(tx, sizeof(*tx), metadata, sizeof(*metadata)) ||
                !vg_offline_disjoint(working, capacity, metadata, sizeof(*metadata))) return VG_RETIRE_REJECTED;
        }
        bool accepted_target = false;
        for (size_t i = 0u; i < accepted->count; ++i) {
            const vg_journal_event_t *event = &accepted->events[i];
            if (event->event_id <= tx->current.confirmed_event_id) continue;
            if (event->event_id < record->event.event_id) return VG_RETIRE_REJECTED;
            if (event->event_id != record->event.event_id) continue;
            if (!vg_offline_event_equal(event, &record->event) ||
                (metadata ? (!record->has_alarm ||
                    !vg_alarm_metadata_equal(&metadata->entries[i].alarm, &record->alarm)) : record->has_alarm))
                return VG_RETIRE_REJECTED;
            accepted_target = true;
        }
        /* Older valid recovery may resurrect a server-confirmed stored prefix
         * already released from RAM. It remains the oldest stored fact and may
         * be authenticated again without rewinding RAM IDs or inventing data. */
        if (!accepted_target && found == tx->current.event_count) return VG_RETIRE_REJECTED;
    }
    if (vg_offline_event_json(record, tx->current.device, working, capacity) != VG_REPLAY_ENCODED)
        return VG_RETIRE_REJECTED;
    uint8_t digest[32] = {0}, claimed[32] = {0};
    const uint8_t *raw_receipt = (const uint8_t *)receipt;
    bool authenticated = !memcmp(raw_receipt, "VGR1:", 5u) && raw_receipt[69] == (uint8_t)':' &&
        vg_receipt_unhex32(raw_receipt + 5u, claimed) &&
        verifier->verify(verifier->context, working, strlen(working), status, receipt, receipt_length, digest) &&
        vg_receipt_equal32(claimed, digest);
    vg_receipt_zero(digest, sizeof(digest));
    vg_receipt_zero(claimed, sizeof(claimed));
    if (!authenticated) return VG_RETIRE_REJECTED;
    if (covered || (!current && found == tx->current.event_count)) return VG_RETIRE_ALREADY_CONFIRMED;
    tx->candidate = tx->current;
    tx->candidate.generation++;
    if (found < tx->current.event_count) {
        for (size_t i = found + 1u; i < tx->candidate.event_count; ++i)
            tx->candidate.events[i - 1u] = tx->candidate.events[i];
        --tx->candidate.event_count;
        memset(&tx->candidate.events[tx->candidate.event_count], 0, sizeof(tx->candidate.events[0]));
    }
    if (current) tx->candidate.confirmed_event_id = record->event.event_id;
    if (!vg_offline_candidate_base_valid(tx)) return VG_RETIRE_REJECTED;
    /* Candidate is constructed only from this authenticated exact target; no
     * caller-supplied replacement snapshot can remove any unrelated record. */
    if (!vg_offline_commit_readback_admitted(tx))
        return tx->halted ? VG_RETIRE_IO_HALTED : VG_RETIRE_REJECTED;
    return VG_RETIRE_COMMITTED;
}

#endif
