<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Monitoring devices</title></head>
<body><main><h1>Monitoring devices</h1><p>Hanya perangkat aktif dengan grant eksplisit yang ditampilkan.</p>
<ul>@forelse($devices as $device)<li><a href="{{ route('monitoring.device', ['device' => $device->device_id]) }}">{{ $device->device_id }}</a></li>
@empty<li>Tidak ada perangkat yang diizinkan.</li>@endforelse</ul>
<form method="post" action="{{ route('logout') }}">@csrf<button type="submit">Sign out</button></form>
</main></body></html>
