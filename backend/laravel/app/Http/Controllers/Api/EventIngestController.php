<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\EventIngestRequest;
use App\Models\Device;
use App\Services\EventIngestService;
use Illuminate\Http\JsonResponse;

class EventIngestController extends Controller
{
    public function __construct(
        private readonly EventIngestService $service
    ) {
    }

    public function __invoke(EventIngestRequest $request): JsonResponse
    {
        $device = $request->attributes->get('authenticated_device');

        if (! $device instanceof Device) {
            return response()->json([
                'error' => 'invalid_device_authentication',
            ], 401);
        }

        $payload = $request->validated();

        if ((string) $payload['device_id'] !== $device->device_id) {
            return response()->json([
                'error' => 'device_identity_mismatch',
            ], 403);
        }

        $result = $this->service->ingest($device, $payload);

        return response()->json($result['body'], $result['status']);
    }
}
