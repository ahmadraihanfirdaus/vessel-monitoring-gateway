<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vessel Monitoring · Development Dashboard</title>
  <style>
    :root { font-family: system-ui, sans-serif; color-scheme: dark; }
    body { margin: 0; padding: 2rem; background: #111827; color: #f9fafb; }
    main { max-width: 1100px; margin: auto; }
    .panel { border: 1px solid #475569; border-radius: 12px; padding: 1rem; background: #1f2937; }
    .badge { display: inline-block; border-radius: 5px; border: 1px solid #94a3b8; padding: .3rem .55rem; margin: .2rem; font-weight: bold; }
    .muted { color: #d1d5db; }
    .sections { display: grid; grid-template-columns: repeat(auto-fit,minmax(235px,1fr)); gap: .8rem; margin-top: 1rem; }
    h2 { font-size: 1.05rem; }
  </style>
</head>
<body>
<main>
  <header><h1>Integrated Vessel Monitoring — Development</h1>
    <p class="muted">Monitoring prototype. Belum tersambung ke data perangkat atau layanan realtime.</p>
  </header>
  <section class="panel" aria-label="Legenda kualitas data">
    <h2>Indikator kualitas dan sumber data</h2>
    <p>Legenda ini bukan status perangkat aktual. Status asli memerlukan integrasi authenticated read model.</p>
    <span class="badge">LIVE</span><span class="badge">STALE</span>
    <span class="badge">OFFLINE</span><span class="badge">SIMULATION</span>
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
  </div>
</main>
</body>
</html>
