<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\TelemetryIngestRequest;
use App\Models\Device;
use App\Services\TelemetryIngestService;
use Illuminate\Http\JsonResponse;

class TelemetryIngestController extends Controller
{
    public function __invoke(
        TelemetryIngestRequest $request,
        TelemetryIngestService $ingestService
    ): JsonResponse {
        $device = $request->attributes->get('authenticated_device');

        if (! $device instanceof Device) {
            return response()->json([
                'error' => 'device_authentication_context_missing',
            ], 401);
        }

        $payload = $request->validated();

        if (! hash_equals($device->device_id, (string) $payload['device_id'])) {
            return response()->json([
                'error' => 'device_identity_mismatch',
            ], 403);
        }

        $result = $ingestService->ingest($device, $payload);

        return match ($result['status']) {
            TelemetryIngestService::CREATED => response()->json([
                'result' => 'created',
                'sample_id' => $result['sample_id'],
            ], 201),

            TelemetryIngestService::IDENTICAL => response()->json([
                'result' => 'identical_duplicate',
                'sample_id' => $result['sample_id'],
            ], 200),

            TelemetryIngestService::CONFLICTING => response()->json([
                'error' => 'conflicting_duplicate',
                'sample_id' => $result['sample_id'],
            ], 409),

            default => response()->json([
                'error' => 'telemetry_ingest_state_invalid',
            ], 500),
        };
    }
}
