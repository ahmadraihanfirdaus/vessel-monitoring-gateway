<?php

namespace App\Services;

use App\Models\Device;
use App\Models\TelemetrySample;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use RuntimeException;

class TelemetryIngestService
{
    public const CREATED = 'created';

    public const IDENTICAL = 'identical_duplicate';

    public const CONFLICTING = 'conflicting_duplicate';

    public function ingest(Device $device, array $payload): array
    {
        try {
            return DB::transaction(
                fn (): array => $this->ingestWithinTransaction($device, $payload)
            );
        } catch (QueryException $exception) {
            if (! $this->isMySqlDuplicateKey($exception)) {
                throw $exception;
            }

            return DB::transaction(function () use ($device, $payload): array {
                $device = Device::query()
                    ->whereKey($device->getKey())
                    ->lockForUpdate()
                    ->firstOrFail();
                $existing = $this->findExisting($device, $payload);

                if ($existing === null) {
                    throw new RuntimeException(
                        'Duplicate-key race occurred but the telemetry row could not be reloaded.'
                    );
                }

                return $this->classifyExisting($device, $existing, $payload);
            });
        }
    }

    private function ingestWithinTransaction(Device $device, array $payload): array
    {
        // Serialize state changes for this device; the unique telemetry key
        // remains the independent idempotency/concurrency backstop.
        $device = Device::query()
            ->whereKey($device->getKey())
            ->lockForUpdate()
            ->firstOrFail();

        $existing = $this->findExisting($device, $payload);

        if ($existing !== null) {
            return $this->classifyExisting($device, $existing, $payload);
        }

        $sample = TelemetrySample::query()->create([
            'device_id' => $device->device_id,
            'schema_version' => $payload['schema_version'],
            'firmware_version' => $payload['firmware_version'],
            'boot_id' => $payload['boot_id'],
            'sequence' => $this->normalizeUnsignedInteger($payload['sequence']),
            'uptime_ms' => $this->normalizeUnsignedInteger($payload['uptime_ms']),
            'source_mode' => $payload['source_mode'],
            'received_at' => now(),
        ]);

        foreach ($payload['channels'] as $rawName => $channel) {
            $sample->channels()->create([
                'name' => (string) $rawName,
                'quality' => $channel['quality'],
                'value' => $channel['value'],
            ]);
        }

        $this->updateDeviceCommunicationState($device, $payload);

        return [
            'status' => self::CREATED,
            'sample_id' => $sample->id,
        ];
    }

    private function findExisting(Device $device, array $payload): ?TelemetrySample
    {
        return TelemetrySample::query()
            ->with('channels')
            ->where('device_id', $device->device_id)
            ->where('boot_id', $payload['boot_id'])
            ->where(
                'sequence',
                $this->normalizeUnsignedInteger($payload['sequence'])
            )
            ->first();
    }

    private function classifyExisting(
        Device $device,
        TelemetrySample $existing,
        array $payload
    ): array {
        if (! $this->semanticallyEqual($existing, $payload)) {
            return [
                'status' => self::CONFLICTING,
                'sample_id' => $existing->id,
            ];
        }

        // A replayed identical sample proves receipt, not a newer cursor.
        $this->updateDeviceCommunicationState($device, $payload, true);

        return [
            'status' => self::IDENTICAL,
            'sample_id' => $existing->id,
        ];
    }

    private function semanticallyEqual(
        TelemetrySample $existing,
        array $payload
    ): bool {
        if ($existing->schema_version !== $payload['schema_version']
            || $existing->firmware_version !== $payload['firmware_version']
            || $this->normalizeUnsignedInteger($existing->uptime_ms)
                !== $this->normalizeUnsignedInteger($payload['uptime_ms'])
            || $existing->source_mode !== $payload['source_mode']) {
            return false;
        }

        $storedChannels = $existing->channels
            ->keyBy(fn ($channel): string => (string) $channel->name);

        if ($storedChannels->count() !== count($payload['channels'])) {
            return false;
        }

        foreach ($payload['channels'] as $rawName => $incoming) {
            $name = (string) $rawName;
            $stored = $storedChannels->get($name);

            if ($stored === null || $stored->quality !== $incoming['quality']) {
                return false;
            }

            if (! $this->sameNullableNumber($stored->value, $incoming['value'])) {
                return false;
            }
        }

        return true;
    }

    private function sameNullableNumber(mixed $stored, mixed $incoming): bool
    {
        if ($stored === null || $incoming === null) {
            return $stored === null && $incoming === null;
        }

        return (float) $stored === (float) $incoming;
    }

    private function normalizeUnsignedInteger(mixed $value): string
    {
        if (is_int($value) && $value >= 0) {
            return (string) $value;
        }

        if (is_string($value)
            && preg_match('/\A(?:0|[1-9][0-9]*)\z/', $value) === 1) {
            return $value;
        }

        throw new RuntimeException('Validated unsigned integer is invalid.');
    }

    private function updateDeviceCommunicationState(
        Device $device,
        array $payload,
        bool $identicalDuplicate = false
    ): void {
        // last_seen_at is server-side receipt time, including valid duplicates.
        $updates = ['last_seen_at' => now()];

        if (! $identicalDuplicate) {
            $sequence = $this->normalizeUnsignedInteger($payload['sequence']);
            $lastBootId = $device->getRawOriginal('last_boot_id');
            $lastSequence = $device->getRawOriginal('last_sequence');

            // Sequence is only comparable within a single boot. Preserve the
            // high-water mark when distinct samples arrive out of order.
            if ($lastBootId !== $payload['boot_id']
                || $lastSequence === null
                || $this->compareUnsignedDecimalStrings(
                    $sequence,
                    $this->normalizeUnsignedInteger($lastSequence)
                ) > 0) {
                $updates['last_boot_id'] = $payload['boot_id'];
                $updates['last_sequence'] = $sequence;
            }
        }

        $device->forceFill($updates)->save();
    }

    private function compareUnsignedDecimalStrings(string $left, string $right): int
    {
        // Decimal strings avoid overflow on unsigned BIGINT above PHP_INT_MAX.
        return strlen($left) <=> strlen($right) ?: strcmp($left, $right);
    }

    private function isMySqlDuplicateKey(QueryException $exception): bool
    {
        $sqlState = $exception->errorInfo[0] ?? null;
        $driverCode = (int) ($exception->errorInfo[1] ?? 0);

        return $sqlState === '23000' && $driverCode === 1062;
    }
}
