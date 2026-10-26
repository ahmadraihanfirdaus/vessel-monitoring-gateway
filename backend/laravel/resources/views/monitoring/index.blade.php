<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vessel Monitoring &middot; Development Dashboard</title>
<style>
:root { font-family:system-ui,sans-serif; color-scheme:dark; }
body { margin:0; padding:1.5rem; background:#111827; color:#f9fafb; }
main { max-width:1200px; margin:auto; } a { color:#93c5fd; }
.panel { border:1px solid #64748b; border-radius:8px; padding:1rem; background:#1f2937; overflow:auto; }
.badge { display:inline-block; border:1px solid #cbd5e1; border-radius:4px; padding:.2rem .5rem; font-weight:bold; }
.LIVE { border-color:#4ade80; } .STALE { border-color:#facc15; } .OFFLINE,.UNKNOWN { border-color:#fb7185; }
.sections { display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:1rem; margin-top:1rem; }
table { width:100%; border-collapse:collapse; } th,td { padding:.4rem; text-align:left; border-bottom:1px solid #64748b; }
h2 { font-size:1.15rem; } nav a { margin-right:1rem; } dt { font-weight:bold; } dd { overflow-wrap:anywhere; }
</style>
<script defer src="{{ asset('assets/monitoring-freshness.js') }}?v={{ $freshnessAssetHash }}"></script>
</head><body><main>
<header><h1>Integrated Vessel Monitoring &mdash; Development</h1>
<p>Perangkat: <strong>{{ $deviceId }}</strong>. Monitoring prototype; read-only.</p>
<nav><a href="{{ route('monitoring.index') }}">Devices</a><a href="{{ url()->current() }}">Refresh data</a></nav>
<form method="post" action="{{ route('logout') }}">@csrf<button type="submit">Sign out</button></form>
</header>
<section class="panel" aria-label="Status data aktual">
<p>Telemetry: @include('monitoring.freshness', ['scope' => 'sample', 'freshness' => $sampleFreshness])
<span class="badge">{{ $sourceLabel }}</span></p>
<p>{{ $sampleFreshness['reason'] }}; snapshot age: {{ $sampleFreshness['age_seconds'] ?? 'UNKNOWN' }} s.</p>
<p>Transport receipt: @include('monitoring.freshness', ['scope' => 'transport', 'freshness' => $transportFreshness])
{{ $transportFreshness['reason'] }}.</p>
<p>Waktu penerimaan server bukan waktu global pengukuran. Nilai tersimpan dapat berasal dari replay.</p>
<p>Snapshot server: {{ $snapshotAt }}. Status receipt dapat kedaluwarsa di halaman ini;
nilai, kualitas, alarm, dan sumber tetap snapshot. Gunakan Refresh data untuk GET terbaru.
Jika script/timing tidak tersedia, label SNAPSHOT hanya berlaku saat snapshot server.</p>
@if($state === null)<p>DATA NOT CONNECTED: telemetry belum tersambung; tidak ada sample tersimpan.</p>@endif
</section>
<div class="sections">
@include('monitoring.sections.overview')
@include('monitoring.sections.safety')
@include('monitoring.sections.propulsion')
@include('monitoring.sections.navigation')
@include('monitoring.sections.power')
@include('monitoring.sections.alarms-events')
@include('monitoring.sections.device-health')
@include('monitoring.sections.test-evidence')
</div></main></body></html>
