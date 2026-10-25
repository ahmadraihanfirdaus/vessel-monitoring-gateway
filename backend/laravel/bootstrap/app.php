<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        api: __DIR__.'/../routes/api.php',
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->alias([
            'telemetry.payload.size' => \App\Http\Middleware\EnsureTelemetryPayloadSize::class,
            'device.auth' => \App\Http\Middleware\AuthenticateDeviceToken::class,
            'device.response.no-store' => \App\Http\Middleware\NoStoreDeviceResponse::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->render(static function (\Illuminate\Database\QueryException $exception, \Illuminate\Http\Request $request) {
            if ($request->is('login', 'logout', 'monitoring', 'monitoring/*')) {
                return \App\Support\DependencyUnavailableResponse::forConnectionFailure($exception);
            }
            return null;
        });
        // Exceptions raised before controller/middleware completion (CSRF,
        // throttle, session/auth storage) must not become cacheable HTML.
        $exceptions->respond(static function (\Symfony\Component\HttpFoundation\Response $response, \Throwable $exception, \Illuminate\Http\Request $request) {
            return \App\Support\MonitoringResponse::decorate($request, $response);
        });
    })->create();
