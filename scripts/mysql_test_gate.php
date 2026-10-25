<?php

/** Only the explicitly selected testing file; no schema changes outside migrations. */
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;
use Tests\Support\MySqlIsolation;
use Tests\Support\TestApplication;
use Tests\Support\TestEnvironment;
use Tests\Support\TestSchema;

require dirname(__DIR__).'/backend/laravel/vendor/autoload.php';

try {
    $audit = TestEnvironment::prepare(getenv('VG_USE_TESTING_ENV') === '1');
    $env = MySqlIsolation::processEnvironment();
    MySqlIsolation::assertEnvironment($env);
    $app = TestApplication::create();
    MySqlIsolation::assertEffectiveConfiguration($env,
        $app['config']->get('database.connections.mysql'), $app['config']->get('database.default'));
    MySqlIsolation::assertAncillaryConfiguration($app['config']->get('session'), $app['config']->get('cache.stores.database'), $app['config']->get('auth'));
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
    $modes = ['--check', '--inspect', '--inspect-legacy', '--upgrade-existing', '--roundtrip-existing', '--migrate', '--migration-roundtrip'];
    if (! in_array($mode, $modes, true)) {
        throw new RuntimeException('MYSQL_TEST_BLOCKED: unsupported gate mode.');
    }
    $existing = in_array($mode, ['--inspect', '--inspect-legacy', '--upgrade-existing', '--roundtrip-existing'], true);
    $legacy = in_array($mode, ['--inspect-legacy', '--upgrade-existing'], true);
    $tables = static function () use ($pdo): array {
        $names = $pdo->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN);
        sort($names);
        return $names;
    };
    if ($existing) {
        TestSchema::assertMigratedAndEmpty($pdo, $legacy);
        echo $legacy ? "DATABASE_LEGACY_ADMISSION=PASS_FIVE_TABLES_FOUR_MIGRATIONS_ZERO_APPLICATION_ROWS\n"
            : "DATABASE_POSTCHECK=PASS_TEN_TABLES_FIVE_MIGRATIONS_ZERO_APPLICATION_ROWS\n";
        if (in_array($mode, ['--inspect', '--inspect-legacy'], true)) {
            exit(0);
        }
    } else {
        if ($tables() !== []) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: empty test catalog required.');
        }
        TestSchema::assertNoExtraObjects($pdo);
        echo "MYSQL_TEST_PREFLIGHT=PASS_EMPTY_APPROVED_CATALOG\n";
        if ($mode === '--check') {
            exit(0);
        }
    }
    $expectedFiles = array_map(static fn ($path) => basename($path, '.php'),
        glob(dirname(__DIR__).'/backend/laravel/database/migrations/*.php'));
    sort($expectedFiles);
    if ($expectedFiles !== TestSchema::migrations()) {
        throw new RuntimeException('MYSQL_TEST_BLOCKED: source migration inventory mismatch.');
    }
    $migrate = static function () use ($pdo): void {
        if (Artisan::call('migrate', ['--force' => true, '--no-interaction' => true]) !== 0) {
            throw new RuntimeException('MYSQL_TEST_FAIL: migration apply.');
        }
        TestSchema::assertMigratedAndEmpty($pdo);
        echo "MYSQL_MIGRATION_APPLY=PASS\n";
    };
    if ($mode !== '--roundtrip-existing') {
        $migrate();
    }
    if ($mode === '--upgrade-existing') {
        echo "MYSQL_MIGRATION_UPGRADE=PASS_EXACT_EMPTY_LEGACY_TO_CURRENT\n";
        exit(0);
    }
    if (in_array($mode, ['--migration-roundtrip', '--roundtrip-existing'], true)) {
        if (Artisan::call('migrate:rollback', ['--step' => count(TestSchema::migrations()), '--force' => true, '--no-interaction' => true]) !== 0
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
