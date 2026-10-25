<?php

namespace Tests\Support;

use PDO;
use RuntimeException;

/** Exact isolated test inventories, including the explicitly admitted upgrade source. */
final class TestSchema
{
    public static function tables(bool $legacy = false): array
    {
        $tables = ['devices', 'migrations', 'monitoring_events', 'telemetry_channels', 'telemetry_samples'];
        if (! $legacy) {
            $tables = array_merge($tables, ['cache', 'cache_locks', 'monitoring_device_access', 'sessions', 'users']);
        }
        sort($tables);
        return $tables;
    }

    public static function migrations(bool $legacy = false): array
    {
        $names = ['2026_10_17_100001_create_devices_table', '2026_10_17_100002_create_telemetry_samples_table',
            '2026_10_17_100003_create_telemetry_channels_table', '2026_10_18_100004_create_monitoring_events_table'];
        if (! $legacy) {
            $names[] = '2026_10_25_100005_create_monitoring_access_tables';
        }
        return $names;
    }

    public static function assertNoExtraObjects(PDO $pdo): void
    {
        foreach (['routines' => 'routine_schema', 'events' => 'event_schema', 'triggers' => 'trigger_schema'] as $table => $column) {
            if ((int) $pdo->query('SELECT COUNT(*) FROM information_schema.'.$table.' WHERE '.$column.' = DATABASE()')->fetchColumn() !== 0) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: unexpected test schema objects.');
            }
        }
    }

    public static function assertMigratedAndEmpty(PDO $pdo, bool $legacy = false): void
    {
        $tables = $pdo->query('SHOW FULL TABLES')->fetchAll(PDO::FETCH_NUM);
        $names = [];
        foreach ($tables as [$name, $type]) {
            if ($type !== 'BASE TABLE') {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: non-table schema objects prohibited.');
            }
            $names[] = $name;
        }
        sort($names);
        if ($names !== self::tables($legacy)) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: expected migrated test schema required.');
        }
        foreach (array_diff($names, ['migrations']) as $table) {
            if ((int) $pdo->query('SELECT COUNT(*) FROM '.$table)->fetchColumn() !== 0) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: preexisting application rows prohibited.');
            }
        }
        if ($pdo->query('SELECT migration FROM migrations ORDER BY migration')->fetchAll(PDO::FETCH_COLUMN) !== self::migrations($legacy)) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: migration repository inventory mismatch.');
        }
        self::assertNoExtraObjects($pdo);
    }
}
