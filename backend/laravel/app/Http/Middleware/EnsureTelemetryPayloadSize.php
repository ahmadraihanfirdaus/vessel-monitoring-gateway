<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureTelemetryPayloadSize
{
    public const MAX_BYTES = 4096;

    public function handle(Request $request, Closure $next): Response
    {
        $declaredLength = $request->headers->get('Content-Length');

        if (is_string($declaredLength)
            && ctype_digit($declaredLength)
            && (int) $declaredLength > self::MAX_BYTES) {
            return $this->tooLarge();
        }

        if (strlen($request->getContent()) > self::MAX_BYTES) {
            return $this->tooLarge();
        }

        // Reject non-JSON bodies *before* device lookup or ingest services.
        // Laravel's isJson() accepts application/json and +json media types.
        if (! $request->isJson()) {
            return response()->json([
                'error' => 'unsupported_telemetry_media_type',
            ], 415);
        }

        return $next($request);
    }

    private function tooLarge(): JsonResponse
    {
        return response()->json([
            'error' => 'telemetry_payload_too_large',
            'max_bytes' => self::MAX_BYTES,
        ], 413);
    }
}
