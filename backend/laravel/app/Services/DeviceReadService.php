<?php

namespace App\Services;

use App\Models\Device;
use Carbon\CarbonImmutable;
use Illuminate\Pagination\Cursor;
use Illuminate\Support\Facades\DB;

class DeviceReadService
{
    public function state(Device $device): array
    {
        $sample = $this->latestSample($device->device_id);

        return [
            'device_id' => $device->device_id,
            'state' => $sample === null ? null : $this->sampleToArray($sample),
        ];
    }

    public function history(
        Device $device,
        int $limit,
        ?string $encodedCursor
    ): array {
        $cursor = null;

        if (is_string($encodedCursor) && $encodedCursor !== '') {
            $cursor = Cursor::fromEncoded($encodedCursor);
        }

        $paginator = DB::table('telemetry_samples')
            ->where('device_id', $device->device_id)
            ->orderByDesc('received_at')
            ->orderByDesc('id')
            ->cursorPaginate($limit, ['*'], 'cursor', $cursor);

        $items = [];
        foreach ($paginator->items() as $sample) {
            $items[] = $this->sampleToArray($sample);
        }

        return [
            'device_id' => $device->device_id,
            'items' => $items,
            'next_cursor' => $paginator->nextCursor()?->encode(),
        ];
    }

    public function health(Device $device): array
    {
        $sample = $this->latestSample($device->device_id);
        $lastSeenRaw = $device->getRawOriginal('last_seen_at');
        $ageSeconds = null;

        if (is_string($lastSeenRaw) && $lastSeenRaw !== '') {
            $lastSeen = CarbonImmutable::parse($lastSeenRaw);
            $ageSeconds = max(0, $lastSeen->diffInSeconds(now()));
        }

        return [
            'device_id' => $device->device_id,
            'enabled' => (bool) $device->enabled,
            'seen' => $lastSeenRaw !== null,
            'last_seen_at' => $lastSeenRaw,
            'last_boot_id' => $device->getRawOriginal('last_boot_id'),
            'last_sequence' => $device->getRawOriginal('last_sequence'),
            'latest_firmware_version' => $sample?->firmware_version,
            'latest_source_mode' => $sample?->source_mode,
            'latest_uptime_ms' => $sample?->uptime_ms,
            'latest_received_at' => $sample?->received_at,
            'age_seconds' => $ageSeconds,
        ];
    }

    private function latestSample(string $deviceId): ?object
    {
        return DB::table('telemetry_samples')
            ->where('device_id', $deviceId)
            ->orderByDesc('received_at')
            ->orderByDesc('id')
            ->first();
    }

    private function sampleToArray(object $sample): array
    {
        $channels = DB::table('telemetry_channels')
            ->where('telemetry_sample_id', $sample->id)
            ->orderBy('name')
            ->get()
            ->mapWithKeys(static function (object $channel): array {
                return [
                    $channel->name => [
                        'value' => $channel->value,
                        'quality' => $channel->quality,
                    ],
                ];
            })
            ->all();

        return [
            'schema_version' => $sample->schema_version,
            'device_id' => $sample->device_id,
            'firmware_version' => $sample->firmware_version,
            'boot_id' => $sample->boot_id,
            'sequence' => $sample->sequence,
            'uptime_ms' => $sample->uptime_ms,
            'source_mode' => $sample->source_mode,
            'received_at' => $sample->received_at,
            'channels' => $channels,
        ];
    }
}
