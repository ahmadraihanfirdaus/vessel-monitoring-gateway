<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Device;
use App\Support\DependencyUnavailableResponse;
use Illuminate\Database\QueryException;
use App\Services\DeviceReadService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use App\Support\StrictDeviceHistoryCursor;
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
        if ($cursor !== null && ! StrictDeviceHistoryCursor::isValid($cursor)) {
            return response()->json([
                'message' => 'The given data was invalid.',
                'errors' => [
                    'cursor' => ['The cursor field is invalid.'],
                ],
            ], 422);
        }

        try {
            return response()->json($this->service->history(
                $device,
                (int) ($validated['limit'] ?? 50),
                $cursor
            ));
        } catch (QueryException $exception) {
            $response = DependencyUnavailableResponse::forConnectionFailure($exception);
            if ($response !== null) {
                return $response;
            }
            throw $exception;
        }
    }
}
