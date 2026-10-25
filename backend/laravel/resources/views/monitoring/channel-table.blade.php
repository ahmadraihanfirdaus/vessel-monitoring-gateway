@if($channels === [])
<p>Tidak ada channel yang tersedia/ditetapkan untuk bagian ini. Tidak diasumsikan bernilai nol atau aman.</p>
@else
<table><thead><tr><th>Channel</th><th>Value (wire units)</th><th>Quality</th></tr></thead><tbody>
@foreach($channels as $name => $channel)
<tr><td>{{ $name }}</td><td>
@if(in_array($channel['quality'], ['valid','stale'], true) && $channel['value'] !== null)
{{ $channel['value'] }}
@if(($simulationPresentation ?? false) && ($description = \App\Support\SimulationChannelPresentation::describe((string) $name, $channel['value'])) !== null)
<small>{{ $description }}</small>
@endif
@else
&mdash;
@endif
</td><td><span class="badge">{{ strtoupper($channel['quality']) }}</span></td></tr>
@endforeach
</tbody></table>
@endif
