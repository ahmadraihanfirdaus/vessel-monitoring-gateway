<?php

namespace App\Services;

use App\Models\Device;
use Illuminate\Pagination\Cursor;
use Illuminate\Support\Facades\DB;

/** Receipt-ordered event facts; acknowledgement never implies alarm clearance. */
class DeviceEventReadService
{
    public function history(Device $device, int $limit, ?string $cursor, array $filters): array
    {
        $query = DB::table('monitoring_events')->where('device_id', $device->device_id);
        foreach (['event_type', 'source_mode'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
        }

        $page = $query->orderByDesc('received_at')->orderByDesc('id')
            ->cursorPaginate($limit, ['*'], 'cursor', $cursor === null ? null : Cursor::fromEncoded($cursor));

        $items = [];
        foreach ($page->items() as $event) {
            $items[] = [
                'schema_version' => $event->schema_version,
                'device_id' => $event->device_id,
                'boot_id' => $event->boot_id,
                // Decimal strings preserve all uint64 values in browser clients too.
                'event_id' => (string) $event->event_id,
                'linked_alarm_id' => (string) $event->linked_alarm_id,
                'source_id' => (string) $event->source_id,
                'source_mode' => $event->source_mode,
                'event_type' => $event->event_type,
                'occurred_at_ms' => (string) $event->occurred_at_ms,
                'received_at' => $event->received_at,
            ];
        }

        return [
            'device_id' => $device->device_id,
            'items' => $items,
            'next_cursor' => $page->nextCursor()?->encode(),
        ];
    }
}
