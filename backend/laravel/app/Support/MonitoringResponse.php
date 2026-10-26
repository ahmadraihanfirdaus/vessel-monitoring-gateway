<?php

namespace App\Support;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

final class MonitoringResponse
{
    public static function decorate(Request $request, Response $response): Response
    {
        if ($request->is('/', 'login', 'logout', 'monitoring', 'monitoring/*')) {
            $response->headers->set('Cache-Control', 'no-store, private');
            $response->headers->set('Pragma', 'no-cache');
            $response->setVary(implode(', ', array_unique([...$response->getVary(), 'Cookie'])));
            $response->headers->set('Referrer-Policy', 'no-referrer');
            $response->headers->set('X-Content-Type-Options', 'nosniff');
            $script = $request->routeIs('monitoring.device') && $response->getStatusCode() === 200
                && str_starts_with((string) $response->headers->get('Content-Type'), 'text/html') ? "'self'" : "'none'";
            $response->headers->set('Content-Security-Policy', "default-src 'self'; script-src $script; connect-src 'none'; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'");
        }
        return $response;
    }
}
