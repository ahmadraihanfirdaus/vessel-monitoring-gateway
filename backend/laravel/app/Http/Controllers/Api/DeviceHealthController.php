<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Device;
use App\Services\DeviceReadService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class DeviceHealthController extends Controller
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

        return response()->json(
            $this->service->health($device)
        );
    }
}
