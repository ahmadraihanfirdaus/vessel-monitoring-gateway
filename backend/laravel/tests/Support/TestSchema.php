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

    public static function migrations(bool $legacy = false, bool $previous = false): array
    {
        if ($legacy && $previous) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: ambiguous migration admission profile.');
        }
        $names = ['2026_10_17_100001_create_devices_table', '2026_10_17_100002_create_telemetry_samples_table',
            '2026_10_17_100003_create_telemetry_channels_table', '2026_10_18_100004_create_monitoring_events_table'];
        if (! $legacy) {
            $names[] = '2026_10_25_100005_create_monitoring_access_tables';
            if (! $previous) {
                $names[] = '2026_10_25_100006_add_alarm_metadata_to_monitoring_events';
            }
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

    public static function assertMigratedAndEmpty(PDO $pdo, bool $legacy = false, bool $previous = false): void
    {
        self::assertCatalog($pdo, $legacy, $previous);
        foreach (array_diff(self::tables($legacy), ['migrations']) as $table) {
            if ((int) $pdo->query('SELECT COUNT(*) FROM '.$table)->fetchColumn() !== 0) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: preexisting application rows prohibited.');
            }
        }
    }

    /** Shape only. Populated HTTP fixtures additionally require exact lease ownership. */
    public static function assertCatalog(PDO $pdo, bool $legacy = false, bool $previous = false): void
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
        if ($pdo->query('SELECT migration FROM migrations ORDER BY migration')->fetchAll(PDO::FETCH_COLUMN) !== self::migrations($legacy, $previous)) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: migration repository inventory mismatch.');
        }
        $columns = $pdo->query('SHOW COLUMNS FROM monitoring_events')->fetchAll(PDO::FETCH_ASSOC);
        $expected = ['id', 'device_id', 'schema_version', 'boot_id', 'event_id', 'linked_alarm_id',
            'source_id', 'source_mode', 'event_type', 'occurred_at_ms', 'received_at'];
        if (! $legacy && ! $previous) {
            $expected[] = 'alarm_metadata';
        }
        if (array_column($columns, 'Field') !== $expected) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: event column inventory mismatch.');
        }
        if (! $legacy && ! $previous) {
            $metadata = $columns[count($columns) - 1];
            if (! in_array($metadata['Type'], ['json', 'longtext'], true) || $metadata['Null'] !== 'YES') {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: alarm metadata column contract mismatch.');
            }
        }
        self::assertNoExtraObjects($pdo);
    }
}
