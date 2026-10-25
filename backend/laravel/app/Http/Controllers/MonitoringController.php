<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Services\DeviceEventReadService;
use App\Services\DeviceReadService;
use App\Services\MonitoringAccess;
use App\Support\DashboardSignalLabel;
use App\Support\DependencyUnavailableResponse;
use App\Support\MonitoringFreshness;
use App\Support\MonitoringEvidence;
use Carbon\CarbonImmutable;
use Illuminate\Database\QueryException;
use Illuminate\Http\Request;

class MonitoringController extends Controller
{
    public function __construct(private readonly MonitoringAccess $access, private readonly DeviceReadService $reads,
        private readonly DeviceEventReadService $events)
    {
    }

    public function __invoke(Request $request, ?string $device = null)
    {
        try {
            $user = $request->user('web');
            abort_unless($user instanceof User && $this->access->enabled($user), 403);
            if ($device === null) {
                return view('monitoring.devices', ['devices' => $this->access->devices($user)->orderBy('devices.device_id')->get()]);
            }
            $selected = $this->access->devices($user)->where('devices.device_id', $device)->first();
            // Same outcome for ungranted, disabled and nonexistent devices.
            abort_if($selected === null, 404);
            $snapshot = $this->reads->snapshot($selected);
            $state = $snapshot['state'];
            $health = $snapshot['health'];
            $events = $this->events->history($selected, 50, null, [])['items'];
            $stale = config('monitoring.stale_after_seconds');
            $offline = config('monitoring.offline_after_seconds');
            $now = CarbonImmutable::now('UTC');
            $sectionChannels = [];
            foreach (['safety', 'propulsion', 'navigation', 'power'] as $section) {
                $names = config('monitoring.channel_sections.'.$section, []);
                $sectionChannels[$section] = is_array($names)
                    ? array_intersect_key($state['channels'] ?? [], array_fill_keys(array_filter($names, 'is_string'), true)) : [];
            }

            return view('monitoring.index', [
                'deviceId' => $selected->device_id, 'state' => $state, 'health' => $health, 'events' => $events,
                'sampleFreshness' => MonitoringFreshness::classify($state['received_at'] ?? null, $now, $stale, $offline),
                'transportFreshness' => MonitoringFreshness::classify($health['last_seen_at'], $now, $stale, $offline),
                'sourceLabel' => DashboardSignalLabel::labels('unknown', $state['source_mode'] ?? '')['source_mode'],
                'sectionChannels' => $sectionChannels,
                'evidence' => (new MonitoringEvidence())->snapshot(),
            ]);
        } catch (QueryException $exception) {
            $response = DependencyUnavailableResponse::forConnectionFailure($exception);
            if ($response !== null) {
                return $response;
            }
            throw $exception;
        }
    }
}
