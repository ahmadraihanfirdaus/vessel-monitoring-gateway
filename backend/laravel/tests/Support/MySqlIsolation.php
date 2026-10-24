<?php

namespace Tests\Support;

use PDO;
use RuntimeException;

/** Test-only admission policy. Every check precedes transactions or migrations. */
final class MySqlIsolation
{
    public static function processEnvironment(): array
    {
        $values = [];
        foreach (['APP_ENV', 'DB_CONNECTION', 'DB_HOST', 'DB_PORT', 'DB_DATABASE',
            'DB_USERNAME', 'DB_PASSWORD', 'DB_URL', 'DATABASE_URL', 'DB_SOCKET',
            'VG_MYSQL_TEST_ACK', 'GITHUB_ACTIONS'] as $name) {
            $value = getenv($name);
            $values[$name] = $value === false ? null : $value;
        }

        return $values;
    }

    public static function assertEnvironment(array $env): void
    {
        $ci = ($env['GITHUB_ACTIONS'] ?? null) === 'true';
        $database = $ci ? 'vessel_gateway_ci' : 'vessel_gateway_codex_test';
        $port = $ci ? '3306' : '3307';
        if (($env['APP_ENV'] ?? null) !== 'testing'
            || ($env['DB_CONNECTION'] ?? null) !== 'mysql'
            || ($env['DB_HOST'] ?? null) !== '127.0.0.1'
            || ($env['DB_PORT'] ?? null) !== $port
            || ($env['DB_DATABASE'] ?? null) !== $database
            || ($env['VG_MYSQL_TEST_ACK'] ?? null) !== $database
            || ! is_string($env['DB_USERNAME'] ?? null)
            || $env['DB_USERNAME'] === ''
            || (! $ci && $env['DB_USERNAME'] !== 'vgw_codex')
            || ! is_string($env['DB_PASSWORD'] ?? null)) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: explicit isolated test configuration required.');
        }

        foreach (['DB_URL', 'DATABASE_URL', 'DB_SOCKET'] as $name) {
            if (($env[$name] ?? '') !== '' && ($env[$name] ?? null) !== null) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: connection overrides prohibited.');
            }
        }
    }

    public static function assertServer(array $env, string $version, ?string $database, array $catalogs): void
    {
        self::assertEnvironment($env);
        $ci = ($env['GITHUB_ACTIONS'] ?? null) === 'true';
        $engineMatches = $ci
            ? preg_match('/\A8\.[0-9]+\.[0-9]+(?:[-+].*)?\z/', $version) === 1 && stripos($version, 'mariadb') === false
            : $version === '10.4.32-MariaDB';
        if (! $engineMatches
            || $database !== $env['DB_DATABASE']) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: approved engine and matching test catalog required.');
        }

        $allowed = ['information_schema', 'mysql', 'performance_schema', 'sys', $database];
        // MariaDB exposes its default test catalog even to a separately scoped
        // account. verify() independently requires target-only explicit grants.
        if (! $ci) {
            $allowed[] = 'test';
        }
        if (! in_array($database, $catalogs, true) || array_diff($catalogs, $allowed) !== []) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: unrelated accessible catalog detected.');
        }
    }

    public static function assertEffectiveConfiguration(array $env, array $connection, string $default): void
    {
        self::assertEnvironment($env);
        if ($default !== 'mysql' || ($connection['driver'] ?? null) !== 'mysql'
            || ! empty($connection['url']) || ! empty($connection['unix_socket'])
            || ! empty($connection['read']) || ! empty($connection['write'])
            || ! empty($connection['prefix'])) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: effective connection override prohibited.');
        }
        foreach (['host' => 'DB_HOST', 'port' => 'DB_PORT', 'database' => 'DB_DATABASE',
            'username' => 'DB_USERNAME', 'password' => 'DB_PASSWORD'] as $key => $name) {
            if ((string) ($connection[$key] ?? '') !== $env[$name]) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: effective connection mismatch.');
            }
        }
    }

    public static function verify(PDO $pdo, array $env): void
    {
        self::assertEnvironment($env);
        $row = $pdo->query('SELECT VERSION() AS version, DATABASE() AS db, CURRENT_USER() AS account, @@port AS port')->fetch(PDO::FETCH_ASSOC);
        $catalogs = $pdo->query('SHOW DATABASES')->fetchAll(PDO::FETCH_COLUMN);
        self::assertServer($env, $row['version'], $row['db'], $catalogs);
        if ((string) $row['port'] !== $env['DB_PORT']
            || explode('@', $row['account'])[0] !== $env['DB_USERNAME']) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: server account or port mismatch.');
        }
        if (($env['GITHUB_ACTIONS'] ?? null) !== 'true') {
            self::assertLocalGrants($pdo->query('SHOW GRANTS FOR CURRENT_USER')->fetchAll(PDO::FETCH_COLUMN));
        }
    }

    public static function assertLocalGrants(array $grants): void
    {
        $hasTarget = false;
        foreach ($grants as $grant) {
            if (stripos($grant, 'WITH GRANT OPTION') !== false
                || preg_match('/\AGRANT\s+(.+?)\s+ON\s+(.+?)\s+TO\s/is', $grant, $matches) !== 1) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: unapproved account grants.');
            }
            $scope = str_replace('`', '', trim($matches[2]));
            if ($scope === 'vessel_gateway_codex_test.*') {
                $hasTarget = true;
            } elseif ($scope !== '*.*' || trim($matches[1]) !== 'USAGE') {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: account grants extend beyond approved test catalog.');
            }
        }
        if (! $hasTarget) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: target catalog grant required.');
        }
    }

    public static function assertMigratedAndEmpty(PDO $pdo): void
    {
        $tables = $pdo->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN);
        sort($tables);
        $expected = ['devices', 'migrations', 'monitoring_events', 'telemetry_channels', 'telemetry_samples'];
        if ($tables !== $expected) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: expected migrated test schema required.');
        }
        foreach (['devices', 'monitoring_events', 'telemetry_channels', 'telemetry_samples'] as $table) {
            if ((int) $pdo->query('SELECT COUNT(*) FROM '.$table)->fetchColumn() !== 0) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: preexisting application rows prohibited.');
            }
        }
    }
}
