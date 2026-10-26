#ifndef VG_EVENT_DELIVERY_H
#define VG_EVENT_DELIVERY_H

#include "esp32_network_client.h"
#include "esp32_offline_store.h"

typedef enum {
    VG_DELIVERY_IDLE = 0, VG_DELIVERY_HTTP,
    VG_DELIVERY_RECEIPT, VG_DELIVERY_STORAGE
} vg_delivery_stage;

typedef struct {
    vg_delivery_stage stage;
    bool event_halted;
    uint64_t last_tag, tag, recovery_epoch;
    vg_net_kind kind;
    vg_replay_choice source;
    size_t source_index;
    vg_offline_event record;
    int status;
    uint8_t receipt[VG_EVENT_RECEIPT_LENGTH];
} vg_event_delivery;

typedef struct {
    const char *boot;
    vg_event_journal_t *journal;
    vg_alarm_journal_t *metadata;
    vg_replay_progress *progress;
    const vg_recovered_events *recovered;
    bool recovered_ready;
    uint64_t recovery_epoch;
} vg_delivery_context;

typedef enum {
    VG_DELIVERY_IGNORED = 0, VG_DELIVERY_TELEMETRY_DONE,
    VG_DELIVERY_RECEIPT_READY, VG_DELIVERY_NETWORK_FAILED,
    VG_DELIVERY_REJECTED, VG_DELIVERY_CONFIRMED,
    VG_DELIVERY_RESCHEDULED, VG_DELIVERY_UNRETIRED
} vg_delivery_result;

static inline bool vg_delivery_context_valid(const vg_delivery_context *context)
{
    return context && vg_tel_safe_token(context->boot, VG_TELEMETRY_MAX_ID_LEN) &&
        vg_offline_journal_follows(context->journal, context->journal) &&
        vg_alarm_journal_matches(context->metadata, context->journal) && context->progress &&
        context->progress->current_queued <= context->journal->count &&
        context->progress->recovered_unpublishable <= context->progress->recovered_visited &&
        (!context->recovered_ready || vg_recovered_events_valid(context->recovered)) &&
        context->progress->recovered_visited <= (context->recovered_ready ? context->recovered->event_count : 0u);
}

static inline void vg_delivery_close(vg_event_delivery *owner)
{
    uint64_t last = owner->last_tag;
    bool halted = owner->event_halted;
    memset(owner, 0, sizeof(*owner));
    owner->last_tag = last;
    owner->event_halted = halted;
}

static inline uint64_t vg_delivery_next_tag(const vg_event_delivery *owner)
{
    return owner && owner->stage == VG_DELIVERY_IDLE && owner->last_tag != UINT64_MAX
        ? owner->last_tag + 1u : 0u;
}

/* Queue accepted first; all arguments must have been validated before submit.
 * Caller halts publication if this invariant unexpectedly fails afterwards. */
static inline bool vg_delivery_begin(vg_event_delivery *owner, vg_net_kind kind, uint64_t tag,
    const vg_offline_event *record, vg_replay_choice source, size_t index, uint64_t recovery_epoch)
{
    if (!owner || !tag || tag != vg_delivery_next_tag(owner) ||
        (kind != VG_NET_TELEMETRY && kind != VG_NET_EVENT)) return false;
    if (kind == VG_NET_EVENT && (owner->event_halted || !vg_offline_record_valid(record) ||
        (source != VG_REPLAY_CURRENT && source != VG_REPLAY_RECOVERED) || index >= VG_OFFLINE_EVENT_CAP ||
        !vg_offline_disjoint(owner, sizeof(*owner), record, sizeof(*record)))) return false;
    if (kind == VG_NET_TELEMETRY && (record || source != VG_REPLAY_NONE)) return false;
    owner->stage = VG_DELIVERY_HTTP;
    owner->last_tag = tag;
    owner->tag = tag;
    owner->kind = kind;
    owner->source = source;
    owner->source_index = index;
    owner->recovery_epoch = recovery_epoch;
    if (record) owner->record = *record;
    return true;
}

/* Queue acceptance is not delivery. Rewind only the failed immutable fact's
 * source cursor; never move a reset/new recovery view forward or infer an ACK.
 * Caller consumes the matching completion before attempting a transport reset. */
static inline bool vg_delivery_retry_failed_event(const vg_event_delivery *owner, vg_delivery_context *context)
{
    if (!owner || owner->stage != VG_DELIVERY_HTTP || owner->kind != VG_NET_EVENT ||
        !vg_delivery_context_valid(context) || !vg_offline_record_valid(&owner->record) ||
        owner->source_index >= VG_OFFLINE_EVENT_CAP || owner->recovery_epoch > context->recovery_epoch ||
        !vg_offline_disjoint(context->progress, sizeof(*context->progress), owner, sizeof(*owner)) ||
        !vg_offline_disjoint(context->progress, sizeof(*context->progress), context, sizeof(*context)) ||
        !vg_offline_disjoint(context->progress, sizeof(*context->progress), context->journal, sizeof(*context->journal)) ||
        !vg_offline_disjoint(context->progress, sizeof(*context->progress), context->metadata, sizeof(*context->metadata)) ||
        (context->recovered_ready && !vg_offline_disjoint(context->progress, sizeof(*context->progress),
            context->recovered, sizeof(*context->recovered))))
        return false;
    if (owner->source == VG_REPLAY_CURRENT) {
        size_t index = owner->source_index;
        if (strcmp(owner->record.boot, context->boot) || index >= context->journal->count ||
            !owner->record.has_alarm || !vg_offline_event_equal(&owner->record.event, &context->journal->events[index]) ||
            !vg_alarm_metadata_equal(&owner->record.alarm, &context->metadata->entries[index].alarm)) return false;
        if (context->progress->current_queued > index) context->progress->current_queued = index;
    } else if (owner->source == VG_REPLAY_RECOVERED) {
        if (owner->recovery_epoch == context->recovery_epoch) {
            size_t index = owner->source_index;
            if (!context->recovered_ready || index >= context->recovered->event_count ||
                !vg_offline_record_equal(&owner->record, &context->recovered->events[index]) ||
                context->progress->recovered_unpublishable > index) return false;
            if (context->progress->recovered_visited > index) context->progress->recovered_visited = index;
        } /* A newer recovery epoch owns its own cursor; do not touch it. */
    } else return false;
    return true;
}

static inline vg_delivery_result vg_delivery_receive_http(vg_event_delivery *owner, const vg_net_completion *completion,
    vg_delivery_context *context)
{
    if (!owner || !completion || owner->stage != VG_DELIVERY_HTTP || completion->tag != owner->tag)
        return VG_DELIVERY_IGNORED;
    if (!completion->completed || (completion->http_status != 200 && completion->http_status != 201)) {
        if (owner->kind == VG_NET_EVENT) {
            // Invalid overlapping caller state cannot be made safe by clearing
            // the owner, which could itself overwrite retained facts/cursors.
            if (context && ((!vg_offline_disjoint(owner, sizeof(*owner), context, sizeof(*context))) ||
                (context->progress && !vg_offline_disjoint(owner, sizeof(*owner), context->progress, sizeof(*context->progress))) ||
                (context->journal && !vg_offline_disjoint(owner, sizeof(*owner), context->journal, sizeof(*context->journal))) ||
                (context->metadata && !vg_offline_disjoint(owner, sizeof(*owner), context->metadata, sizeof(*context->metadata))) ||
                (context->recovered_ready && context->recovered && !vg_offline_disjoint(owner, sizeof(*owner),
                    context->recovered, sizeof(*context->recovered)))))
                return VG_DELIVERY_REJECTED;
            if (!vg_delivery_retry_failed_event(owner, context)) {
                owner->event_halted = true;
                vg_delivery_close(owner);
                return VG_DELIVERY_REJECTED;
            }
        }
        vg_delivery_close(owner);
        return VG_DELIVERY_NETWORK_FAILED;
    }
    if (owner->kind == VG_NET_TELEMETRY) {
        vg_delivery_close(owner);
        return VG_DELIVERY_TELEMETRY_DONE;
    }
    if (!completion->event_receipt_media_valid || completion->response_length != VG_EVENT_RECEIPT_LENGTH) {
        owner->event_halted = true;
        vg_delivery_close(owner);
        return VG_DELIVERY_REJECTED;
    }
    memcpy(owner->receipt, completion->response, sizeof(owner->receipt));
    owner->status = completion->http_status;
    owner->stage = VG_DELIVERY_RECEIPT;
    return VG_DELIVERY_RECEIPT_READY; /* Authentication remains in the worker. */
}

static inline bool vg_delivery_prior_fact_pending(const vg_offline_event *record, const vg_delivery_context *context)
{
    if (!vg_offline_record_valid(record) || !vg_delivery_context_valid(context) || strcmp(record->boot, context->boot))
        return false;
    if (context->journal->count && context->journal->events[0].event_id < record->event.event_id) return true;
    if (context->recovered_ready)
        for (size_t i = context->progress->recovered_visited; i < context->recovered->event_count; ++i)
            if (!strcmp(context->recovered->events[i].boot, context->boot) &&
                context->recovered->events[i].event.event_id < record->event.event_id) return true;
    return false;
}

/* A recovered predecessor of a current fact must be authenticated first. This
 * bounded exception to alternation prevents one-inflight receipt deadlock. */
static inline vg_replay_choice vg_delivery_choose(vg_delivery_context *context)
{
    if (!vg_delivery_context_valid(context)) return VG_REPLAY_CHOICE_INVALID;
    if (context->recovered_ready && context->progress->current_queued < context->journal->count) {
        uint64_t next = context->journal->events[context->progress->current_queued].event_id;
        for (size_t i = context->progress->recovered_visited; i < context->recovered->event_count; ++i)
            if (!strcmp(context->recovered->events[i].boot, context->boot) &&
                context->recovered->events[i].event.event_id < next)
                context->progress->prefer_recovered = true;
    }
    return vg_replay_choose(context->progress,
        context->recovered_ready ? context->recovered->event_count : 0u, context->journal->count);
}

/* No fact is removed. A reply for a newer fact may be discarded and requested
 * again idempotently after recovered prerequisites. A newer recovery view has
 * already reset its own cursor, so an old source index must not rewind it. */
static inline bool vg_delivery_reschedule(vg_event_delivery *owner, vg_delivery_context *context)
{
    if (!owner || !vg_delivery_context_valid(context) || owner->kind != VG_NET_EVENT ||
        (owner->stage != VG_DELIVERY_RECEIPT && owner->stage != VG_DELIVERY_STORAGE)) return false;
    if (owner->source == VG_REPLAY_CURRENT) {
        if (context->progress->current_queued > owner->source_index)
            context->progress->current_queued = owner->source_index;
    } else if (owner->source == VG_REPLAY_RECOVERED && owner->recovery_epoch == context->recovery_epoch &&
        context->progress->recovered_visited > owner->source_index) {
        context->progress->recovered_visited = owner->source_index;
    }
    vg_delivery_close(owner);
    return true;
}

static inline bool vg_delivery_receipt_submitted(vg_event_delivery *owner)
{
    if (!owner || owner->kind != VG_NET_EVENT || owner->stage != VG_DELIVERY_RECEIPT) return false;
    owner->stage = VG_DELIVERY_STORAGE;
    return true;
}

static inline vg_delivery_result vg_delivery_receive_storage(vg_event_delivery *owner,
    const vg_storage_retirement_completion *completion, vg_delivery_context *context)
{
    if (!owner || !completion || owner->stage != VG_DELIVERY_STORAGE || completion->tag != owner->tag)
        return VG_DELIVERY_IGNORED;
    if (!vg_delivery_context_valid(context)) {
        owner->event_halted = true;
        vg_delivery_close(owner);
        return VG_DELIVERY_REJECTED;
    }
    if (completion->result == VG_RETIRE_IO_HALTED) {
        vg_delivery_close(owner);
        return VG_DELIVERY_UNRETIRED;
    }
    if (completion->result != VG_RETIRE_COMMITTED && completion->result != VG_RETIRE_ALREADY_CONFIRMED) {
        if (vg_delivery_prior_fact_pending(&owner->record, context) && vg_delivery_reschedule(owner, context))
            return VG_DELIVERY_RESCHEDULED;
        owner->event_halted = true;
        vg_delivery_close(owner);
        return VG_DELIVERY_REJECTED;
    }
    if (completion->generation == 0u || (!strcmp(owner->record.boot, context->boot) &&
        completion->confirmed_event_id < owner->record.event.event_id)) {
        owner->event_halted = true;
        vg_delivery_close(owner);
        return VG_DELIVERY_REJECTED;
    }
    if (!strcmp(owner->record.boot, context->boot) && context->journal->count != 0u) {
        uint64_t first = context->journal->events[0].event_id;
        if (first < owner->record.event.event_id) {
            return vg_delivery_reschedule(owner, context) ? VG_DELIVERY_RESCHEDULED : VG_DELIVERY_REJECTED;
        }
        if (first == owner->record.event.event_id) {
            if (!vg_offline_release_confirmed_prefix(context->journal, context->metadata, &owner->record)) {
                owner->event_halted = true;
                vg_delivery_close(owner);
                return VG_DELIVERY_REJECTED;
            }
            if (context->progress->current_queued != 0u) --context->progress->current_queued;
        }
    }
    vg_delivery_close(owner);
    return VG_DELIVERY_CONFIRMED;
}

#endif
