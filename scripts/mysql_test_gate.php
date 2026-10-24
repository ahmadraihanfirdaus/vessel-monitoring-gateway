<?php

/** Only the explicitly selected testing file; no schema changes outside migrations. */
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;
use Tests\Support\MySqlIsolation;
use Tests\Support\TestApplication;
use Tests\Support\TestEnvironment;

require dirname(__DIR__).'/backend/laravel/vendor/autoload.php';

try {
    $audit = TestEnvironment::prepare(getenv('VG_USE_TESTING_ENV') === '1');
    $env = MySqlIsolation::processEnvironment();
    MySqlIsolation::assertEnvironment($env);
    $app = TestApplication::create();
    MySqlIsolation::assertEffectiveConfiguration($env,
        $app['config']->get('database.connections.mysql'), $app['config']->get('database.default'));
    $pdo = DB::connection('mysql')->getPdo();
    MySqlIsolation::verify($pdo, $env);
    $audit['effective_target'] = ['host' => $env['DB_HOST'], 'port' => $env['DB_PORT'],
        'database' => $env['DB_DATABASE'], 'username' => $env['DB_USERNAME'], 'driver' => 'mysql'];
    $audit['effective_app_testing'] = $app->environment() === 'testing';
    $audit['runtime'] = ['php_version' => PHP_VERSION, 'php_binary' => PHP_BINARY];
    $appKey = $app['config']->get('app.key');
    $decodedKey = is_string($appKey) && str_starts_with($appKey, 'base64:')
        ? base64_decode(substr($appKey, 7), true) : $appKey;
    $audit['app_key_configured'] = is_string($appKey) && $appKey !== '';
    $audit['app_key_cipher_compatible'] = is_string($decodedKey)
        && \Illuminate\Encryption\Encrypter::supported($decodedKey, $app['config']->get('app.cipher'));
    $audit['app_key_source'] = getenv('VG_TEST_EPHEMERAL_KEY') === '1'
        ? 'ephemeral_runner_process' : 'configured_testing_environment';
    $audit['engine'] = $pdo->query('SELECT VERSION()')->fetchColumn();
    echo 'TEST_CONFIG_AUDIT='.json_encode($audit, JSON_UNESCAPED_SLASHES)."\n";
    $mode = $argv[1] ?? '--check';
    if (! in_array($mode, ['--check', '--inspect', '--roundtrip-existing', '--migrate', '--migration-roundtrip'], true)) {
        throw new RuntimeException('MYSQL_TEST_BLOCKED: unsupported gate mode.');
    }
    if (in_array($mode, ['--inspect', '--roundtrip-existing'], true)) {
        MySqlIsolation::assertMigratedAndEmpty($pdo);
        $migrationNames = $pdo->query('SELECT migration FROM migrations ORDER BY migration')->fetchAll(PDO::FETCH_COLUMN);
        $expectedMigrations = array_map(static fn ($path) => basename($path, '.php'),
            glob(dirname(__DIR__).'/backend/laravel/database/migrations/*.php'));
        sort($expectedMigrations);
        if ($migrationNames !== $expectedMigrations) {
            throw new RuntimeException('MYSQL_TEST_FAIL: migration repository inventory mismatch.');
        }
        foreach (['routines' => 'routine_schema', 'events' => 'event_schema', 'triggers' => 'trigger_schema'] as $table => $column) {
            $statement = $pdo->prepare('SELECT COUNT(*) FROM information_schema.'.$table.' WHERE '.$column.' = ?');
            $statement->execute([$env['DB_DATABASE']]);
            if ((int) $statement->fetchColumn() !== 0) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: unexpected test schema objects.');
            }
        }
        echo "DATABASE_POSTCHECK=PASS_FIVE_TABLES_FOUR_MIGRATIONS_ZERO_APPLICATION_ROWS\n";
        if ($mode === '--inspect') {
            exit(0);
        }
    }
    // Empty schema is mandatory, including views/routines/events. This runner
    // refuses an existing migrated schema; it never resets a populated database.
    foreach (['tables' => 'table_schema', 'routines' => 'routine_schema',
        'events' => 'event_schema'] as $table => $column) {
        $statement = $pdo->prepare('SELECT COUNT(*) FROM information_schema.'.$table.' WHERE '.$column.' = ?');
        $statement->execute([$env['DB_DATABASE']]);
        if ($mode !== '--roundtrip-existing' && (int) $statement->fetchColumn() !== 0) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: empty test catalog required.');
        }
    }
    if ($mode !== '--roundtrip-existing') {
        echo "MYSQL_TEST_PREFLIGHT=PASS_EMPTY_APPROVED_CATALOG\n";
    }
    if ($mode === '--check') {
        exit(0);
    }
    $expected = ['devices', 'migrations', 'monitoring_events', 'telemetry_channels', 'telemetry_samples'];
    $tables = static function () use ($pdo): array {
        $names = $pdo->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN);
        sort($names);
        return $names;
    };
    $migrate = static function () use ($expected, $tables): void {
        if (Artisan::call('migrate', ['--force' => true, '--no-interaction' => true]) !== 0
            || $tables() !== $expected) {
            throw new RuntimeException('MYSQL_TEST_FAIL: migration apply or schema inventory.');
        }
        echo "MYSQL_MIGRATION_APPLY=PASS\n";
    };
    if ($mode !== '--roundtrip-existing') {
        $migrate();
    }
    if (in_array($mode, ['--migration-roundtrip', '--roundtrip-existing'], true)) {
        if (Artisan::call('migrate:rollback', ['--step' => 4, '--force' => true, '--no-interaction' => true]) !== 0
            || $tables() !== ['migrations']
            || (int) $pdo->query('SELECT COUNT(*) FROM migrations')->fetchColumn() !== 0) {
            throw new RuntimeException('MYSQL_TEST_FAIL: migration rollback inventory.');
        }
        echo "MYSQL_MIGRATION_ROLLBACK=PASS\n";
        $migrate();
        echo "MYSQL_MIGRATION_REAPPLY=PASS\n";
    }
} catch (Throwable $exception) {
    // Deliberately exclude driver exception messages, SQL bindings, and config.
    $message = $exception instanceof RuntimeException
        && preg_match('/\AMYSQL_TEST_(?:BLOCKED|FAIL): [A-Za-z0-9 ._-]+\z/', $exception->getMessage())
        ? $exception->getMessage() : 'MYSQL_TEST_BLOCKED: dependency or connection check failed.';
    fwrite(STDERR, $message."\n");
    exit(3);
}
