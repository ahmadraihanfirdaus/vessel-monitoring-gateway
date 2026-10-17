<?php

namespace App\Http\Middleware;

use App\Services\DeviceTokenAuthenticator;
use Closure;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AuthenticateDeviceToken
{
    public function __construct(
        private readonly DeviceTokenAuthenticator $authenticator
    ) {
    }

    public function handle(Request $request, Closure $next): Response
    {
        $bearerToken = $request->bearerToken();

        if (! is_string($bearerToken)
            || strlen($bearerToken) < 32
            || strlen($bearerToken) > 256) {
            return $this->unauthorized();
        }

        $device = $this->authenticator->resolve($bearerToken);

        if ($device === null) {
            return $this->unauthorized();
        }

        if (! $device->enabled) {
            return response()->json([
                'error' => 'device_disabled',
            ], 403);
        }

        $request->attributes->set('authenticated_device', $device);

        return $next($request);
    }

    private function unauthorized(): JsonResponse
    {
        return response()->json([
            'error' => 'invalid_device_authentication',
        ], 401);
    }
}
