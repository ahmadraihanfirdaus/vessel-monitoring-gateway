<?php

/** Two-process request barrier in the admitted test lease; no production route. */
if (PHP_SAPI !== 'cli' || count($argv) !== 4 || ($argv[3] ?? '') !== '--execute'
    || ! in_array($argv[1] ?? '', ['a', 'b'], true)
    || ! in_array($argv[2] ?? '', ['v10i', 'v11i', 'v11c', 'v11n'], true)) {
    fwrite(STDERR, "EVENT_RACE_BLOCKED: explicit supported CLI fixture action required.\n");
    exit(3);
}

require dirname(__DIR__).'/backend/laravel/vendor/autoload.php';

try {
    $profile = \Tests\Support\LiveHttpSafety::fromEnvironment();
    $app = \Tests\Support\LiveHttpSafety::application($profile);
    \Tests\Support\LiveHttpSafety::assertOwnedRows($profile);
    $lease = getenv('VG_LIVE_HTTP_LEASE');
    $folder = realpath(dirname($lease));
    if ($folder === false || is_link(dirname($lease)) || dirname($folder) !== realpath(sys_get_temp_dir())
        || ! str_starts_with(basename($folder), 'vg-live-http-')) {
        throw new RuntimeException('EVENT_RACE_BLOCKED: owned temporary root required.');
    }
    $role = $argv[1];
    $case = $argv[2];
    $base = $folder.DIRECTORY_SEPARATOR.'event-race-'.$case.'-'.$role;
    $payloadPath = $base.'.json';
    if (! is_file($payloadPath) || is_link($payloadPath) || filesize($payloadPath) > 4096) {
        throw new RuntimeException('EVENT_RACE_BLOCKED: bounded owned payload required.');
    }
    $raw = file_get_contents($payloadPath);
    $payload = json_decode($raw, true, 512, JSON_THROW_ON_ERROR | JSON_BIGINT_AS_STRING);
    if (($payload['device_id'] ?? null) !== $profile['device']
        || ($payload['boot_id'] ?? null) !== $case.'-'.$profile['id'] || ($payload['event_id'] ?? null) !== 1) {
        throw new RuntimeException('EVENT_RACE_BLOCKED: derived fixture identity required.');
    }
    if (\App\Models\MonitoringEvent::query()->where('device_id', $profile['device'])
        ->where('boot_id', $payload['boot_id'])->where('event_id', 1)->exists()) {
        throw new RuntimeException('EVENT_RACE_BLOCKED: fresh race identity required.');
    }
    // MariaDB 10.4 exposes tx_isolation; MySQL 8 exposes transaction_isolation.
    // Inspect only these nonsecret names without changing session isolation.
    $variables = \Illuminate\Support\Facades\DB::select(
        "SHOW SESSION VARIABLES WHERE Variable_name IN ('transaction_isolation', 'tx_isolation')"
    );
    $levels = array_values(array_unique(array_map(static fn ($row) => strtoupper((string) $row->Value), $variables)));
    $isolation = count($levels) === 1 ? $levels[0] : '';
    if (! in_array(str_replace('-', ' ', $isolation), ['REPEATABLE READ', 'READ COMMITTED'], true)) {
        throw new RuntimeException('EVENT_RACE_BLOCKED: unsupported isolation profile.');
    }
    $paused = false;
    \Illuminate\Support\Facades\DB::listen(static function ($query) use (&$paused, $payload, $base): void {
        $sql = strtolower($query->sql);
        $bindings = array_map('strval', $query->bindings);
        if ($paused || ! str_starts_with(ltrim($sql), 'select') || ! str_contains($sql, 'from `monitoring_events`')
            || ! in_array($payload['boot_id'], $bindings, true) || ! in_array($payload['device_id'], $bindings, true)) {
            return;
        }
        $paused = true;
        $ready = fopen($base.'.ready', 'x');
        if ($ready === false) {
            throw new RuntimeException('EVENT_RACE_BLOCKED: fresh barrier required.');
        }
        fwrite($ready, "READY\n");
        fclose($ready);
        $deadline = hrtime(true) + 20000000000;
        while (hrtime(true) < $deadline) {
            clearstatcache(true, $base.'.go');
            if (is_file($base.'.go') && ! is_link($base.'.go') && filesize($base.'.go') === 3
                && file_get_contents($base.'.go') === "GO\n") {
                return;
            }
            usleep(10000);
        }
        throw new RuntimeException('EVENT_RACE_BLOCKED: barrier timeout.');
    });
    $request = \Illuminate\Http\Request::create(rtrim(config('app.url'), '/').'/api/v1/events', 'POST', [], [], [], [
        'CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json',
        'HTTP_AUTHORIZATION' => 'Bearer '.getenv('VG_LIVE_DEVICE_TOKEN'),
        'HTTP_USER_AGENT' => $profile['agent'], 'REMOTE_ADDR' => '127.0.0.1', 'HTTPS' => 'on',
    ], $raw);
    if ($case === 'v11n') {
        // Exercise callers that own a surrounding transaction/read snapshot.
        \Illuminate\Support\Facades\DB::beginTransaction();
    }
    $kernel = $app->make(\Illuminate\Contracts\Http\Kernel::class);
    $response = $kernel->handle($request);
    $kernel->terminate($request, $response);
    if ($case === 'v11n') {
        if ($response->getStatusCode() < 400) {
            \Illuminate\Support\Facades\DB::commit();
        } else {
            \Illuminate\Support\Facades\DB::rollBack();
        }
    }
    if (! $paused) {
        throw new RuntimeException('EVENT_RACE_BLOCKED: intended transaction read was not observed.');
    }
    echo 'EVENT_RACE_ISOLATION='.str_replace(' ', '-', $isolation)."\n";
    echo 'EVENT_RACE_RESULT='.$response->getStatusCode()."\n";
} catch (Throwable $exception) {
    // Never print exception text, SQL bindings, request bodies or credentials.
    fwrite(STDERR, 'EVENT_RACE_BLOCKED: '.class_basename($exception)."\n");
    exit(3);
}
