<?php

namespace App\Services;

use App\Models\Device;
use App\Models\MonitoringEvent;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;

class EventIngestService
{
    public function ingest(Device $device, array $payload): array
    {
        return DB::transaction(function () use ($device, $payload): array {
            $existing = $this->findExisting(
                $device->device_id,
                (string) $payload['boot_id'],
                (string) $payload['event_id']
            );

            if ($existing !== null) {
                return $this->duplicateResult($existing, $payload);
            }

            try {
                MonitoringEvent::query()->create([
                    'device_id' => $device->device_id,
                    'schema_version' => (string) $payload['schema_version'],
                    'boot_id' => (string) $payload['boot_id'],
                    'event_id' => (string) $payload['event_id'],
                    'linked_alarm_id' => (string) $payload['linked_alarm_id'],
                    'source_id' => (int) $payload['source_id'],
                    'source_mode' => (string) $payload['source_mode'],
                    'event_type' => (string) $payload['event_type'],
                    'occurred_at_ms' => (string) $payload['occurred_at_ms'],
                    'received_at' => now(),
                ]);
            } catch (QueryException $exception) {
                if (! $this->isMySqlDuplicateKey($exception)) {
                    throw $exception;
                }

                $raced = $this->findExisting(
                    $device->device_id,
                    (string) $payload['boot_id'],
                    (string) $payload['event_id']
                );

                if ($raced === null) {
                    throw $exception;
                }

                return $this->duplicateResult($raced, $payload);
            }

            return [
                'status' => 201,
                'body' => ['result' => 'event_persisted'],
            ];
        });
    }

    private function findExisting(
        string $deviceId,
        string $bootId,
        string $eventId
    ): ?MonitoringEvent {
        return MonitoringEvent::query()
            ->where('device_id', $deviceId)
            ->where('boot_id', $bootId)
            ->where('event_id', $eventId)
            ->first();
    }

    private function duplicateResult(
        MonitoringEvent $event,
        array $payload
    ): array {
        if ($this->semanticallyEqual($event, $payload)) {
            return [
                'status' => 200,
                'body' => ['result' => 'identical_event_duplicate'],
            ];
        }

        return [
            'status' => 409,
            'body' => ['error' => 'conflicting_event_duplicate'],
        ];
    }

    private function semanticallyEqual(
        MonitoringEvent $event,
        array $payload
    ): bool {
        return $event->device_id === (string) $payload['device_id']
            && $event->schema_version === (string) $payload['schema_version']
            && $event->boot_id === (string) $payload['boot_id']
            && (string) $event->event_id === (string) $payload['event_id']
            && (string) $event->linked_alarm_id === (string) $payload['linked_alarm_id']
            && (string) $event->source_id === (string) $payload['source_id']
            && $event->source_mode === (string) $payload['source_mode']
            && $event->event_type === (string) $payload['event_type']
            && (string) $event->occurred_at_ms === (string) $payload['occurred_at_ms'];
    }

    private function isMySqlDuplicateKey(QueryException $exception): bool
    {
        $sqlState = $exception->errorInfo[0] ?? null;
        $driverCode = (int) ($exception->errorInfo[1] ?? 0);

        return $sqlState === '23000' && $driverCode === 1062;
    }
}
