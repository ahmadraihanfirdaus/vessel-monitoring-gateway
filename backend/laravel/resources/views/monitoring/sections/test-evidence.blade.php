<section class="panel" aria-label="Test Evidence"><h2>Test Evidence</h2>
<p>Overall system: PARTIAL. Final verification approval: NOT_APPROVED.</p>
<p>Source mode dan data yang terlihat bukan hasil formal verifikasi. Tidak ada hasil PASS yang disimpulkan dari nilai telemetry.</p>
@if(!$evidence['available'])<p>UNKNOWN: evidence registry tidak tersedia atau gagal validasi.</p>@else
<p>Status formal yang tercatat dalam register repository; bukan pengujian yang dijalankan oleh halaman ini.</p>
<table><thead><tr><th>Scenario</th><th>Recorded status</th></tr></thead><tbody>
@foreach(array_merge($evidence['simulation'], $evidence['supplemental']) as $id => $status)
<tr><td>{{ $id }}</td><td>{{ $status }}</td></tr>
@endforeach</tbody></table>@endif
<p>ESP32/NVS, hardware, hosted CI, deployed TLS dan protokol formal yang belum dieksekusi: NOT_RUN.</p></section>
