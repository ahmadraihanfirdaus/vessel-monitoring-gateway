<section class="panel" aria-label="Device Health"><h2>Device Health</h2><dl>
<dt>Last server receipt (UTC)</dt><dd>{{ $health['last_seen_at'] ?? 'NEVER SEEN' }}</dd>
<dt>Transport freshness</dt><dd>@include('monitoring.freshness', ['scope' => 'transport', 'freshness' => $transportFreshness])
/ snapshot age {{ $transportFreshness['age_seconds'] ?? 'UNKNOWN' }} s</dd>
<dt>Latest firmware / source</dt><dd>{{ $health['latest_firmware_version'] ?? 'UNKNOWN' }} / {{ $health['latest_source_mode'] ?? 'UNKNOWN' }}</dd>
<dt>High-water boot / sequence</dt><dd>{{ $health['last_boot_id'] ?? 'UNKNOWN' }} / {{ $health['last_sequence'] ?? 'UNKNOWN' }}</dd>
</dl><p>Receipt dan high-water facts tidak membuktikan urutan lintas boot atau kondisi fisik.</p></section>
