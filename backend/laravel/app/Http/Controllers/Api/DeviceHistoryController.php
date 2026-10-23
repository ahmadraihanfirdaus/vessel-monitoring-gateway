<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Device;
use App\Services\DeviceReadService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Pagination\Cursor;
use Illuminate\Support\Facades\Validator;

class DeviceHistoryController extends Controller
{
    public function __construct(
        private readonly DeviceReadService $service
    ) {
    }

    public function __invoke(Request $request): JsonResponse
    {
        $device = $request->attributes->get('authenticated_device');

        if (! $device instanceof Device) {
            return response()->json([
                'error' => 'invalid_device_authentication',
            ], 401);
        }

        $validator = Validator::make($request->query(), [
            'limit' => ['sometimes', 'integer', 'min:1', 'max:100'],
            'cursor' => ['sometimes', 'string', 'max:2048'],
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'The given data was invalid.',
                'errors' => $validator->errors(),
            ], 422);
        }

        $validated = $validator->validated();

        $cursor = isset($validated['cursor']) ? (string) $validated['cursor'] : null;
        if ($cursor !== null) {
            // Only malformed user cursors receive 422. Do not disguise a
            // backend outage, service bug, or persistence exception as 422.
            try {
                $decoded = Cursor::fromEncoded($cursor);
            } catch (\Throwable) {
                $decoded = null;
            }
            if ($decoded === null) {
                return response()->json([
                    'message' => 'The given data was invalid.',
                    'errors' => [
                        'cursor' => ['The cursor field is invalid.'],
                    ],
                ], 422);
            }
        }

        return response()->json($this->service->history(
            $device,
            (int) ($validated['limit'] ?? 50),
            $cursor
        ));
    }
}
