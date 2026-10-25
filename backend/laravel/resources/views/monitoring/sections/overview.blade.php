<section class="panel" aria-label="Overview"><h2>Overview</h2>
<p>Schema {{ $state['schema_version'] ?? 'UNKNOWN' }}; firmware {{ $state['firmware_version'] ?? 'UNKNOWN' }};
boot {{ $state['boot_id'] ?? 'UNKNOWN' }}; sequence {{ $state['sequence'] ?? 'UNKNOWN' }}.</p>
<p>Sample received (UTC): {{ $state['received_at'] ?? 'NONE' }}. Sample freshness: {{ $sampleFreshness['label'] }}.</p>
@include('monitoring.channel-table', ['channels' => $state['channels'] ?? []])</section>
