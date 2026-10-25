<section class="panel" aria-label="Alarms and Events"><h2>Alarms and Events</h2>
<p>50 event terakhir menurut penerimaan server. ACK bukan CLEAR; daftar ini tidak menentukan alarm aktif.</p>
@if($events === [])<p>Belum ada event tersimpan.</p>@else
<table><thead><tr><th>Type / alarm</th><th>Source / identity</th><th>Time</th><th>Alarm snapshot at transition</th></tr></thead><tbody>
@foreach($events as $event)<tr><td>{{ $event['event_type'] }} / {{ $event['linked_alarm_id'] }}</td>
<td>{{ $event['source_mode'] }} / {{ $event['boot_id'] }} / {{ $event['event_id'] }}</td>
<td>{{ $event['received_at'] }} UTC; device ms {{ $event['occurred_at_ms'] }}</td>
<td>@if(is_array($event['alarm'] ?? null))
<strong>{{ $event['alarm']['state'] }}</strong>
<p>Priority code (demo): {{ $event['alarm']['priority_code'] }}; reason code: {{ $event['alarm']['reason_code'] }}.</p>
<p>Boot-relative ms: raised {{ $event['alarm']['raised_at_ms'] }};
acknowledged {{ $event['alarm']['acknowledged_at_ms'] ?? 'NOT_ACKNOWLEDGED' }};
cleared {{ $event['alarm']['cleared_at_ms'] ?? 'NOT_CLEARED' }}.</p>
@else Metadata alarm lengkap tidak tersedia; tidak direkonstruksi dari event lain.
@endif</td></tr>@endforeach
</tbody></table>@endif</section>
