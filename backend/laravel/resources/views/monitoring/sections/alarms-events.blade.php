<section class="panel" aria-label="Alarms and Events"><h2>Alarms and Events</h2>
<p>50 event terakhir menurut penerimaan server. ACK bukan CLEAR; daftar ini tidak menentukan alarm aktif.</p>
@if($events === [])<p>Belum ada event tersimpan.</p>@else
<table><thead><tr><th>Type / alarm</th><th>Source / identity</th><th>Time</th></tr></thead><tbody>
@foreach($events as $event)<tr><td>{{ $event['event_type'] }} / {{ $event['linked_alarm_id'] }}</td>
<td>{{ $event['source_mode'] }} / {{ $event['boot_id'] }} / {{ $event['event_id'] }}</td>
<td>{{ $event['received_at'] }} UTC; device ms {{ $event['occurred_at_ms'] }}</td></tr>@endforeach
</tbody></table>@endif</section>
