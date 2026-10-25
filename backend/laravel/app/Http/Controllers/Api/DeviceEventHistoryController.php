<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Device;
use App\Services\DeviceEventReadService;
use App\Support\DependencyUnavailableResponse;
use App\Support\StrictDeviceHistoryCursor;
use Illuminate\Database\QueryException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

class DeviceEventHistoryController extends Controller
{
    public function __construct(private readonly DeviceEventReadService $service)
    {
    }

    public function __invoke(Request $request): JsonResponse
    {
        $device = $request->attributes->get('authenticated_device');
        if (! $device instanceof Device) {
            return response()->json(['error' => 'invalid_device_authentication'], 401);
        }

        $query = $request->query();
        if (array_diff(array_keys($query), ['limit', 'cursor', 'event_type', 'source_mode']) !== []) {
            return response()->json(['error' => 'unsupported_query_parameter'], 422);
        }

        $validator = Validator::make($query, [
            'limit' => ['sometimes', 'integer', 'min:1', 'max:100'],
            'cursor' => ['sometimes', 'string', 'max:2048'],
            'event_type' => ['sometimes', 'string', Rule::in(['alarm_raised', 'alarm_ack', 'alarm_cleared', 'fault'])],
            'source_mode' => ['sometimes', 'string', Rule::in(['simulation', 'bench_test'])],
        ]);
        if ($validator->fails()) {
            return response()->json([
                'message' => 'The given data was invalid.',
                'errors' => $validator->errors(),
            ], 422);
        }

        $validated = $validator->validated();
        $cursor = $validated['cursor'] ?? null;
        if ($cursor !== null && ! StrictDeviceHistoryCursor::isValid($cursor)) {
            return response()->json([
                'message' => 'The given data was invalid.',
                'errors' => ['cursor' => ['The cursor field is invalid.']],
            ], 422);
        }

        try {
            return response()->json($this->service->history($device, (int) ($validated['limit'] ?? 50), $cursor, $validated));
        } catch (QueryException $exception) {
            $response = DependencyUnavailableResponse::forConnectionFailure($exception);
            if ($response !== null) {
                return $response;
            }
            throw $exception;
        }
    }
}
