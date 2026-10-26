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
error_log('VG_LIVE_STAGE=AUTOLOAD_DONE');

try {
    $profile = LiveHttpSafety::fromEnvironment();
    if (! hash_equals($profile['agent'], $_SERVER['HTTP_USER_AGENT'] ?? '')) {
        http_response_code(403);
        exit('Test server unavailable.');
    }
    if (parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH) === '/assets/monitoring-freshness.js'
        && in_array($_SERVER['REQUEST_METHOD'] ?? '', ['GET', 'HEAD'], true)) {
        header('Content-Type: text/javascript; charset=UTF-8');
        header('X-Content-Type-Options: nosniff');
        header('Cache-Control: no-cache');
        if ($_SERVER['REQUEST_METHOD'] === 'GET') {
            readfile(dirname(__DIR__).'/backend/laravel/public/assets/monitoring-freshness.js');
        }
        exit;
    }
    error_log('VG_LIVE_STAGE=PROFILE_ADMITTED');
    $app = LiveHttpSafety::application($profile);
    error_log('VG_LIVE_STAGE=APPLICATION_ADMITTED');
    LiveHttpSafety::assertOwnedRows($profile);
    error_log('VG_LIVE_STAGE=ROWS_ADMITTED');
    // Explicit test deployment: one loopback TLS proxy; only its scheme header.
    TrustProxies::at(['127.0.0.1']);
    TrustProxies::withHeaders(Request::HEADER_X_FORWARDED_PROTO);
    // Enforce actual CSRF while retaining APP_ENV=testing for isolation guards.
    $app->bind(ValidateCsrfToken::class, static fn ($app) =>
        new class($app, $app['encrypter']) extends ValidateCsrfToken {
            protected function runningUnitTests() { return false; }
        });
    $app->handleRequest(Request::capture());
    error_log('VG_LIVE_STAGE=REQUEST_DONE');
} catch (Throwable $exception) {
    http_response_code(503);
    // Private owned test listener only: class category, never exception values.
    header('X-VG-Test-Failure: '.(in_array(get_class($exception), [RuntimeException::class, LogicException::class], true)
        ? get_class($exception) : 'OTHER'));
    header('Cache-Control: no-store, private');
    header('Content-Type: text/plain; charset=UTF-8');
    echo 'Isolated test request blocked.';
}
