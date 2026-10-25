#ifndef VG_OFFLINE_STATE_H
#define VG_OFFLINE_STATE_H

/* Bounded application data, not credentials. Canonical bytes, not struct dumps.
 * CRC detects accidental corruption; it is not authentication or durability.
 * Reuse the existing tested byte/CRC primitives; legacy host capacities remain
 * unchanged. Actual NVS IO is supplied separately. No application ACK deletion. */
#include "phase9_b18_checkpoint_host.h"
#include "core_event_journal.h"
#include "telemetry_contract.h"
#include "alarm_transition.h"

#define VG_OFFLINE_WIRE_MAX 4096u
#define VG_OFFLINE_EVENT_CAP 8u
/* Legacy VGS1 maximum remains 4862 bytes. Optional full metadata VGS2 adds
 * at most 8*35 bytes (5142 total); no application body/partition enlargement. */
#define VG_OFFLINE_SNAPSHOT_MAX 5184u

typedef struct {
    char boot[VG_TELEMETRY_MAX_ID_LEN + 1u];
    vg_journal_event_t event;
    bool has_alarm;
    vg_alarm_t alarm;
} vg_offline_event;

typedef struct {
    uint64_t generation;
    char device[VG_TELEMETRY_MAX_ID_LEN + 1u];
    char latest_boot[VG_TELEMETRY_MAX_ID_LEN + 1u];
    uint64_t latest_sequence;
    uint64_t rejected_critical_attempts;
    size_t latest_length;
    unsigned char latest[VG_OFFLINE_WIRE_MAX];
    size_t event_count;
    vg_offline_event events[VG_OFFLINE_EVENT_CAP];
} vg_offline_state;

typedef enum {
    VG_OFFLINE_REJECTED = 0, VG_OFFLINE_READY,
    VG_OFFLINE_CRITICAL_FULL, VG_OFFLINE_UNCHANGED
} vg_offline_merge_result;

static inline bool vg_offline_disjoint(const void *a, size_t an, const void *b, size_t bn)
{
    uintptr_t x = (uintptr_t)a, y = (uintptr_t)b;
    return a && b && x <= UINTPTR_MAX - an && y <= UINTPTR_MAX - bn &&
        (x + an <= y || y + bn <= x);
}

static inline bool vg_offline_event_valid(const vg_journal_event_t *e)
{
    return e && e->event_id > 0u && e->event_id < UINT64_MAX && e->source_id > 0u &&
        (e->source_mode == VG_SOURCE_SIMULATION || e->source_mode == VG_SOURCE_BENCH_TEST) &&
        e->type >= VG_EVENT_ALARM_RAISED && e->type <= VG_EVENT_RECOVERY;
}

static inline bool vg_offline_event_equal(const vg_journal_event_t *a, const vg_journal_event_t *b)
{
    return vg_alarm_transition_event_equal(a, b);
}

static inline bool vg_offline_record_equal(const vg_offline_event *a, const vg_offline_event *b)
{
    return a && b && !strcmp(a->boot, b->boot) && vg_offline_event_equal(&a->event, &b->event) &&
        a->has_alarm == b->has_alarm && (!a->has_alarm || vg_alarm_metadata_equal(&a->alarm, &b->alarm));
}

static inline bool vg_offline_journal_follows(const vg_event_journal_t *old,
    const vg_event_journal_t *next)
{
    if (!old || !next || !old->initialized || !next->initialized ||
        old->count > VG_JOURNAL_CAPACITY || next->count > VG_JOURNAL_CAPACITY || next->count < old->count) return false;
    for (size_t i = 0u; i < next->count; ++i) {
        const vg_journal_event_t *e = &next->events[i];
        if (!vg_offline_event_valid(e) || (i < old->count &&
            !vg_offline_event_equal(&old->events[i], e)) || (i > 0u &&
            (e->event_id <= next->events[i - 1u].event_id ||
             e->occurred_at_ms < next->events[i - 1u].occurred_at_ms))) return false;
    }
    return true;
}

static inline bool vg_offline_valid(const vg_offline_state *s, bool allow_empty)
{
    if (!s || !vg_tel_safe_token(s->device, VG_TELEMETRY_MAX_ID_LEN)) return false;
    if (s->generation == 0u) return allow_empty && s->latest_length == 0u &&
        s->event_count == 0u && s->latest_boot[0] == 0 && s->latest_sequence == 0u &&
        s->rejected_critical_attempts == 0u;
    if (!vg_tel_safe_token(s->latest_boot, VG_TELEMETRY_MAX_ID_LEN) ||
        s->latest_length == 0u || s->latest_length > VG_OFFLINE_WIRE_MAX ||
        s->event_count > VG_OFFLINE_EVENT_CAP) return false;
    for (size_t i = 0u; i < s->event_count; ++i) {
        if (!vg_tel_safe_token(s->events[i].boot, VG_TELEMETRY_MAX_ID_LEN) ||
            !vg_offline_event_valid(&s->events[i].event)) return false;
        if (s->events[i].has_alarm) {
            vg_alarm_transition_t transition = {s->events[i].event, s->events[i].alarm};
            if (!vg_alarm_transition_valid(&transition)) return false;
        }
        for (size_t j = 0u; j < i; ++j) {
            if (!strcmp(s->events[i].boot, s->events[j].boot) &&
                s->events[i].event.event_id == s->events[j].event.event_id) return false;
        }
    }
    return true;
}

static inline bool vg_offline_init(vg_offline_state *s, const char *device)
{
    if (!s || !vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !vg_offline_disjoint(s, sizeof(*s), device, strlen(device) + 1u)) return false;
    memset(s, 0, sizeof(*s));
    memcpy(s->device, device, strlen(device) + 1u);
    return true;
}

/* Inputs/output must be disjoint. No mutation on rejected/conflicting inputs.
 * Full storage preserves every existing critical entry and advances latest
 * bytes with an explicit partial result and saturated rejected-attempt count.
 * The input journal is cumulative within this boot; no eviction or ACK occurs. */
static inline vg_offline_merge_result vg_offline_merge(const vg_offline_state *old,
    const char *boot, uint64_t sequence, const void *wire, size_t length,
    const vg_event_journal_t *journal, vg_offline_state *out)
{
    if (!out || !vg_offline_valid(old, true) || old->generation == UINT64_MAX ||
        !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN) || !wire || length == 0u ||
        length > VG_OFFLINE_WIRE_MAX || !journal || !journal->initialized ||
        journal->count > VG_JOURNAL_CAPACITY ||
        !vg_offline_disjoint(old, sizeof(*old), out, sizeof(*out)) ||
        !vg_offline_disjoint(boot, strlen(boot) + 1u, out, sizeof(*out)) ||
        !vg_offline_disjoint(wire, length, out, sizeof(*out)) ||
        !vg_offline_disjoint(journal, sizeof(*journal), out, sizeof(*out))) return VG_OFFLINE_REJECTED;
    bool same_boot = old->generation != 0u && !strcmp(boot, old->latest_boot);
    if (same_boot && (sequence < old->latest_sequence || (sequence == old->latest_sequence &&
        (length != old->latest_length || memcmp(wire, old->latest, length))))) return VG_OFFLINE_REJECTED;
    size_t added = 0u;
    for (size_t i = 0u; i < journal->count; ++i) {
        const vg_journal_event_t *e = &journal->events[i];
        if (!vg_offline_event_valid(e) || (i > 0u &&
            (e->event_id <= journal->events[i - 1u].event_id ||
             e->occurred_at_ms < journal->events[i - 1u].occurred_at_ms))) return VG_OFFLINE_REJECTED;
        bool found = false;
        for (size_t j = 0u; j < old->event_count; ++j) {
            if (!strcmp(old->events[j].boot, boot) && old->events[j].event.event_id == e->event_id) {
                if (!vg_offline_event_equal(&old->events[j].event, e)) return VG_OFFLINE_REJECTED;
                found = true;
            }
        }
        if (!found) ++added;
    }
    /* Cumulative means previously retained records from this boot cannot
     * disappear from a later submission, including after storage recovery. */
    for (size_t i = 0u; i < old->event_count; ++i) {
        if (strcmp(old->events[i].boot, boot)) continue;
        bool found = false;
        for (size_t j = 0u; j < journal->count; ++j)
            if (vg_offline_event_equal(&old->events[i].event, &journal->events[j])) found = true;
        if (!found) return VG_OFFLINE_REJECTED;
    }
    if (same_boot && sequence == old->latest_sequence) {
        if (added != 0u) return VG_OFFLINE_REJECTED;
        return VG_OFFLINE_UNCHANGED;
    }
    *out = *old;
    out->generation++;
    memset(out->latest, 0, sizeof(out->latest));
    memcpy(out->latest, wire, length);
    out->latest_length = length;
    memset(out->latest_boot, 0, sizeof(out->latest_boot));
    memcpy(out->latest_boot, boot, strlen(boot) + 1u);
    out->latest_sequence = sequence;
    bool full = false;
    for (size_t i = 0u; i < journal->count; ++i) {
        const vg_journal_event_t *e = &journal->events[i];
        bool found = false;
        for (size_t j = 0u; j < old->event_count; ++j)
            if (!strcmp(old->events[j].boot, boot) && old->events[j].event.event_id == e->event_id) found = true;
        if (found) continue;
        if (out->event_count == VG_OFFLINE_EVENT_CAP) {
            full = true;
            if (out->rejected_critical_attempts != UINT64_MAX) out->rejected_critical_attempts++;
        } else {
            vg_offline_event *dest = &out->events[out->event_count++];
            memset(dest, 0, sizeof(*dest));
            memcpy(dest->boot, boot, strlen(boot) + 1u);
            dest->event = *e;
        }
    }
    return full ? VG_OFFLINE_CRITICAL_FULL : VG_OFFLINE_READY;
}

/* Additive complete-metadata admission. Existing unknown historical metadata
 * cannot be reconstructed/retroactively upgraded through this interface. */
static inline vg_offline_merge_result vg_offline_merge_with_alarms(const vg_offline_state *old,
    const char *boot, uint64_t sequence, const void *wire, size_t length,
    const vg_event_journal_t *journal, const vg_alarm_journal_t *metadata, vg_offline_state *out)
{
    if (!vg_offline_valid(old, true) || !vg_alarm_journal_matches(metadata, journal) ||
        !vg_tel_safe_token(boot, VG_TELEMETRY_MAX_ID_LEN) || !out ||
        !vg_offline_disjoint(metadata, sizeof(*metadata), out, sizeof(*out))) return VG_OFFLINE_REJECTED;
    for (size_t i = 0u; i < old->event_count; ++i) {
        if (strcmp(old->events[i].boot, boot)) continue;
        for (size_t j = 0u; j < metadata->count; ++j)
            if (old->events[i].event.event_id == metadata->entries[j].event.event_id &&
                (!old->events[i].has_alarm ||
                 !vg_offline_event_equal(&old->events[i].event, &metadata->entries[j].event) ||
                 !vg_alarm_metadata_equal(&old->events[i].alarm, &metadata->entries[j].alarm))) return VG_OFFLINE_REJECTED;
    }
    vg_offline_merge_result result = vg_offline_merge(old, boot, sequence, wire, length, journal, out);
    if (result != VG_OFFLINE_READY && result != VG_OFFLINE_CRITICAL_FULL) return result;
    for (size_t i = 0u; i < out->event_count; ++i) {
        if (strcmp(out->events[i].boot, boot)) continue;
        for (size_t j = 0u; j < metadata->count; ++j) {
            if (out->events[i].event.event_id != metadata->entries[j].event.event_id) continue;
            out->events[i].has_alarm = true;
            out->events[i].alarm = metadata->entries[j].alarm;
            if (!out->events[i].alarm.has_acknowledged_at) out->events[i].alarm.acknowledged_at = 0u;
            if (!out->events[i].alarm.has_cleared_at) out->events[i].alarm.cleared_at = 0u;
        }
    }
    return result;
}

static inline void vg_offline_w64(vg_b18_writer *w, uint64_t v)
{
    for (unsigned i = 0u; i < 8u; ++i) vg_b18_w8(w, (uint8_t)(v >> (8u * i)));
}
static inline uint64_t vg_offline_r64(vg_b18_reader *r)
{
    uint64_t v = 0u;
    for (unsigned i = 0u; i < 8u; ++i) v |= (uint64_t)vg_b18_r8(r) << (8u * i);
    return v;
}
static inline void vg_offline_wstring(vg_b18_writer *w, const char *s)
{
    size_t n = strlen(s); vg_b18_w8(w, (uint8_t)n);
    for (size_t i = 0u; i < n; ++i) vg_b18_w8(w, (uint8_t)s[i]);
}
static inline bool vg_offline_rstring(vg_b18_reader *r, char *s)
{
    uint8_t n = vg_b18_r8(r);
    if (!r->ok || n == 0u || n > VG_TELEMETRY_MAX_ID_LEN || n > r->len - r->pos) return false;
    for (size_t i = 0u; i < n; ++i) {
        s[i] = (char)vg_b18_r8(r);
        if (s[i] == 0) return false;
    }
    s[n] = 0;
    return vg_tel_safe_token(s, VG_TELEMETRY_MAX_ID_LEN);
}

/* Full validation/size calculation precedes the first output byte. */
static inline bool vg_offline_pack(const vg_offline_state *s, uint8_t *raw,
    size_t capacity, size_t *written)
{
    if (!raw || !written || !vg_offline_valid(s, false) ||
        !vg_offline_disjoint(s, sizeof(*s), raw, capacity) ||
        !vg_offline_disjoint(s, sizeof(*s), written, sizeof(*written)) ||
        !vg_offline_disjoint(written, sizeof(*written), raw, capacity)) return false;
    size_t size = 4u + 1u + 8u + 8u + 8u + 2u + 1u + 4u +
        1u + strlen(s->device) + 1u + strlen(s->latest_boot) + s->latest_length;
    bool complete = false;
    for (size_t i = 0u; i < s->event_count; ++i) complete |= s->events[i].has_alarm;
    for (size_t i = 0u; i < s->event_count; ++i) size += 1u + strlen(s->events[i].boot) + 30u;
    if (complete) for (size_t i = 0u; i < s->event_count; ++i) size += 1u + (s->events[i].has_alarm ? 34u : 0u);
    if (size > capacity || size > VG_OFFLINE_SNAPSHOT_MAX) return false;
    vg_b18_writer w = {raw, size, 0u, true};
    vg_b18_w32(&w, complete ? UINT32_C(0x32534756) : UINT32_C(0x31534756)); /* VGS2 / unchanged VGS1 */
    vg_b18_w8(&w, complete ? 2u : 1u); vg_offline_w64(&w, s->generation);
    vg_offline_w64(&w, s->latest_sequence); vg_offline_w64(&w, s->rejected_critical_attempts);
    vg_b18_w8(&w, (uint8_t)s->latest_length); vg_b18_w8(&w, (uint8_t)(s->latest_length >> 8u));
    vg_b18_w8(&w, (uint8_t)s->event_count);
    vg_offline_wstring(&w, s->device); vg_offline_wstring(&w, s->latest_boot);
    for (size_t i = 0u; i < s->latest_length; ++i) vg_b18_w8(&w, s->latest[i]);
    for (size_t i = 0u; i < s->event_count; ++i) {
        const vg_journal_event_t *e = &s->events[i].event;
        vg_offline_wstring(&w, s->events[i].boot);
        vg_offline_w64(&w, e->event_id); vg_offline_w64(&w, e->linked_alarm_id);
        vg_b18_w32(&w, e->source_id); vg_b18_w8(&w, (uint8_t)e->source_mode);
        vg_b18_w8(&w, (uint8_t)e->type); vg_offline_w64(&w, e->occurred_at_ms);
        if (complete) {
            vg_b18_w8(&w, s->events[i].has_alarm ? 1u : 0u);
            if (s->events[i].has_alarm) {
                const vg_alarm_t *a = &s->events[i].alarm;
                vg_b18_w32(&w, a->priority_code); vg_b18_w32(&w, a->reason_code);
                vg_b18_w8(&w, (uint8_t)a->state); vg_offline_w64(&w, a->raised_at);
                vg_offline_w64(&w, a->has_acknowledged_at ? a->acknowledged_at : 0u);
                vg_offline_w64(&w, a->has_cleared_at ? a->cleared_at : 0u);
                vg_b18_w8(&w, (uint8_t)((a->has_acknowledged_at ? 1u : 0u) | (a->has_cleared_at ? 2u : 0u)));
            }
        }
    }
    vg_b18_w32(&w, vg_b18_crc32(raw, w.pos));
    *written = w.pos;
    return w.ok && w.pos == size;
}

/* Scratch may change on failure; output never does. Neither aliases inputs. */
static inline bool vg_offline_unpack(const uint8_t *raw, size_t length,
    const char *device, vg_offline_state *scratch, vg_offline_state *out)
{
    if (!raw || length < 40u || length > VG_OFFLINE_SNAPSHOT_MAX || !scratch || !out ||
        !vg_tel_safe_token(device, VG_TELEMETRY_MAX_ID_LEN) ||
        !vg_offline_disjoint(scratch, sizeof(*scratch), out, sizeof(*out)) ||
        !vg_offline_disjoint(raw, length, scratch, sizeof(*scratch)) ||
        !vg_offline_disjoint(raw, length, out, sizeof(*out)) ||
        !vg_offline_disjoint(device, strlen(device) + 1u, scratch, sizeof(*scratch)) ||
        !vg_offline_disjoint(device, strlen(device) + 1u, out, sizeof(*out))) return false;
    vg_b18_reader trailer = {raw + length - 4u, 4u, 0u, true};
    if (vg_b18_r32(&trailer) != vg_b18_crc32(raw, length - 4u)) return false;
    vg_b18_reader r = {raw, length - 4u, 0u, true};
    uint32_t magic = vg_b18_r32(&r);
    uint8_t version = vg_b18_r8(&r);
    bool complete = magic == UINT32_C(0x32534756) && version == 2u;
    if (!complete && (magic != UINT32_C(0x31534756) || version != 1u)) return false;
    memset(scratch, 0, sizeof(*scratch));
    scratch->generation = vg_offline_r64(&r);
    scratch->latest_sequence = vg_offline_r64(&r);
    scratch->rejected_critical_attempts = vg_offline_r64(&r);
    scratch->latest_length = vg_b18_r8(&r);
    scratch->latest_length |= (size_t)vg_b18_r8(&r) << 8u;
    scratch->event_count = vg_b18_r8(&r);
    if (!r.ok || scratch->latest_length == 0u || scratch->latest_length > VG_OFFLINE_WIRE_MAX ||
        scratch->event_count > VG_OFFLINE_EVENT_CAP ||
        !vg_offline_rstring(&r, scratch->device) || strcmp(scratch->device, device) ||
        !vg_offline_rstring(&r, scratch->latest_boot) || scratch->latest_length > r.len - r.pos) return false;
    for (size_t i = 0u; i < scratch->latest_length; ++i) scratch->latest[i] = vg_b18_r8(&r);
    bool has_metadata = false;
    for (size_t i = 0u; i < scratch->event_count; ++i) {
        vg_journal_event_t *e = &scratch->events[i].event;
        if (!vg_offline_rstring(&r, scratch->events[i].boot)) return false;
        e->event_id = vg_offline_r64(&r); e->linked_alarm_id = vg_offline_r64(&r);
        e->source_id = vg_b18_r32(&r); e->source_mode = (vg_source_mode_t)vg_b18_r8(&r);
        e->type = (vg_event_type_t)vg_b18_r8(&r); e->occurred_at_ms = vg_offline_r64(&r);
        if (complete) {
            uint8_t present = vg_b18_r8(&r);
            if (present > 1u) return false;
            scratch->events[i].has_alarm = present != 0u;
            has_metadata |= present != 0u;
            if (present != 0u) {
                vg_alarm_t *a = &scratch->events[i].alarm;
                a->id = e->linked_alarm_id; a->source_id = e->source_id; a->source_mode = e->source_mode;
                a->priority_code = vg_b18_r32(&r); a->reason_code = vg_b18_r32(&r);
                a->state = (vg_alarm_state_t)vg_b18_r8(&r); a->raised_at = vg_offline_r64(&r);
                a->acknowledged_at = vg_offline_r64(&r); a->cleared_at = vg_offline_r64(&r);
                uint8_t flags = vg_b18_r8(&r);
                if (flags > 3u) return false;
                a->has_acknowledged_at = (flags & 1u) != 0u; a->has_cleared_at = (flags & 2u) != 0u;
                a->acknowledged = a->has_acknowledged_at;
                a->condition_active = a->state != VG_ALARM_STATE_CLEARED;
                if ((!a->has_acknowledged_at && a->acknowledged_at != 0u) ||
                    (!a->has_cleared_at && a->cleared_at != 0u)) return false;
            }
        }
    }
    if (!r.ok || r.pos != r.len || (complete && !has_metadata) || !vg_offline_valid(scratch, false)) return false;
    *out = *scratch;
    return true;
}

#endif
