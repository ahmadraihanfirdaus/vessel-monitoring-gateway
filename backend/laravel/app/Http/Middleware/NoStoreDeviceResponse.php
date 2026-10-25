<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/** Refuse cache reuse of device-scoped HTTP results including error receipts. */
final class NoStoreDeviceResponse
{
    public function handle(Request $request, Closure $next): Response
    {
        $response = $next($request);
        $response->headers->set('Cache-Control', 'no-store, private');
        $response->headers->set('Pragma', 'no-cache');
        // Do not overwrite CORS or reverse-proxy Vary selections.
        $response->setVary('Authorization', false);

        return \App\Support\MonitoringResponse::decorate($request, $response);
    }
}
