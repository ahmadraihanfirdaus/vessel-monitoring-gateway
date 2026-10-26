'use strict';
/* Receipt display expiry only. No telemetry fetch, value mutation or client wall clock. */
(function () {
    const ranks = {LIVE: 0, STALE: 1, OFFLINE: 2};
    function integer(value) {
        if (typeof value !== 'string' || !/^(0|[1-9][0-9]*)$/.test(value)) return null;
        const n = Number(value);
        return Number.isSafeInteger(n) ? n : null;
    }
    function status(data, elapsed) {
        if (!Number.isFinite(elapsed) || elapsed < 0) return 'UNKNOWN';
        if (data.label === 'OFFLINE' && data.reason === 'NO RECEIPT') return 'OFFLINE';
        const age = integer(data.ageMs), stale = integer(data.staleMs), offline = integer(data.offlineMs);
        if (!Object.hasOwn(ranks, data.label) || age === null || stale === null || offline === null
            || stale < 1 || offline <= stale || !Number.isSafeInteger(age + Math.ceil(elapsed))) return 'UNKNOWN';
        const total = age + Math.ceil(elapsed);
        const computed = total >= offline ? 'OFFLINE' : total >= stale ? 'STALE' : 'LIVE';
        return ranks[computed] < ranks[data.label] ? data.label : computed;
    }
    function navigationStart(performance) {
        const entries = performance.getEntriesByType('navigation');
        if (entries.length !== 1) return null;
        const entry = entries[0];
        if (!['navigate', 'reload'].includes(entry.type) || !Number.isFinite(entry.requestStart)
            || entry.requestStart < 0 || !Number.isFinite(entry.responseStart)
            || entry.responseStart < entry.requestStart) return null;
        return entry.requestStart;
    }
    if (typeof module === 'object' && module.exports) {
        module.exports = {integer, status, navigationStart}; return;
    }
    const nodes = Array.from(document.querySelectorAll('[data-vg-freshness-scope]'));
    // Default HTML is an explicit neutral SNAPSHOT if this script cannot execute.
    const facts = new Map(nodes.map(node => [node, Object.freeze({label: node.dataset.vgLabel, reason: node.dataset.vgReason,
        ageMs: node.dataset.vgAgeMs, staleMs: node.dataset.vgStaleMs, offlineMs: node.dataset.vgOfflineMs})]));
    let start = null, previous = -1, invalid = false;
    try { start = navigationStart(performance); } catch { invalid = true; }
    function expire() {
        let elapsed = NaN;
        try {
            const current = performance.now();
            if (start === null || !Number.isFinite(current) || current < start || current < previous) invalid = true;
            previous = current;
            if (!invalid) elapsed = current - start;
        } catch { invalid = true; }
        for (const node of nodes) {
            const label = status(facts.get(node), elapsed);
            // Once a displayed status expires it cannot revive in this document.
            const before = node.dataset.vgDisplayed;
            const final = before === 'UNKNOWN' ? 'UNKNOWN'
                : (ranks[before] > ranks[label] ? before : label);
            node.textContent = final;
            node.classList.remove('SNAPSHOT', 'LIVE', 'STALE', 'OFFLINE', 'UNKNOWN');
            node.classList.add(final);
            node.dataset.vgDisplayed = final;
        }
    }
    const refresh = expire;
    refresh();
    setInterval(refresh, 250);
    addEventListener('pageshow', event => { if (event.persisted) invalid = true; refresh(); });
    addEventListener('pagehide', () => { invalid = true; refresh(); });
    document.addEventListener('visibilitychange', () => { if (document.hidden) invalid = true; refresh(); });
    document.addEventListener('freeze', () => { invalid = true; refresh(); });
})();
