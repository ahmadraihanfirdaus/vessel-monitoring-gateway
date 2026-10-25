<?php

/** CLI-server-only front controller for isolated real TCP tests, never deployment. */
use Illuminate\Foundation\Http\Middleware\ValidateCsrfToken;
use Illuminate\Http\Middleware\TrustProxies;
use Illuminate\Http\Request;
use Tests\Support\LiveHttpSafety;

if (PHP_SAPI !== 'cli-server' || ($_SERVER['REMOTE_ADDR'] ?? null) !== '127.0.0.1') {
    http_response_code(403);
    exit('Test server unavailable.');
}
require dirname(__DIR__).'/backend/laravel/vendor/autoload.php';

try {
    $profile = LiveHttpSafety::fromEnvironment();
    if (! hash_equals($profile['agent'], $_SERVER['HTTP_USER_AGENT'] ?? '')) {
        http_response_code(403);
        exit('Test server unavailable.');
    }
    $app = LiveHttpSafety::application($profile);
    LiveHttpSafety::assertOwnedRows($profile);
    // Explicit test deployment: one loopback TLS proxy; only its scheme header.
    TrustProxies::at(['127.0.0.1']);
    TrustProxies::withHeaders(Request::HEADER_X_FORWARDED_PROTO);
    // Enforce actual CSRF while retaining APP_ENV=testing for isolation guards.
    $app->bind(ValidateCsrfToken::class, static fn ($app) =>
        new class($app, $app['encrypter']) extends ValidateCsrfToken {
            protected function runningUnitTests() { return false; }
        });
    $app->handleRequest(Request::capture());
} catch (Throwable $exception) {
    http_response_code(503);
    header('Cache-Control: no-store, private');
    header('Content-Type: text/plain; charset=UTF-8');
    echo 'Isolated test request blocked.';
}
