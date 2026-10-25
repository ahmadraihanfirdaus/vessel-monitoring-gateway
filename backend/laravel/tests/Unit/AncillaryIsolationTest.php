<?php

namespace Tests\Unit;

use App\Models\User;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use Tests\Support\MySqlIsolation;

class AncillaryIsolationTest extends TestCase
{
    private static function configuration(): array
    {
        return ['session' => ['connection' => null, 'table' => 'sessions'],
            'cache' => ['connection' => null, 'lock_connection' => null, 'table' => 'cache', 'lock_table' => null],
            'auth' => ['defaults' => ['guard' => 'web'], 'guards' => ['web' => ['driver' => 'session', 'provider' => 'users']],
                'providers' => ['users' => ['model' => User::class]]]];
    }

    public function test_only_same_mysql_secondary_connections_and_canonical_tables_are_admitted(): void
    {
        $good = self::configuration();
        MySqlIsolation::assertAncillaryConfiguration(...array_values($good));
        $good['session']['connection'] = 'mysql';
        $good['cache']['connection'] = 'mysql';
        $good['cache']['lock_connection'] = 'mysql';
        $good['cache']['lock_table'] = 'cache_locks';
        MySqlIsolation::assertAncillaryConfiguration(...array_values($good));
        $this->addToAssertionCount(2);
    }

    #[DataProvider('overrides')]
    public function test_effective_secondary_or_auth_override_is_rejected(string $section, string $field, mixed $value): void
    {
        $config = self::configuration();
        $keys = explode('.', $field);
        $target = &$config[$section];
        foreach ($keys as $key) { $target = &$target[$key]; }
        $target = $value;
        $this->expectException(\RuntimeException::class);
        MySqlIsolation::assertAncillaryConfiguration(...array_values($config));
    }

    public static function overrides(): array
    {
        return [['session', 'connection', 'sqlite'], ['session', 'table', 'other_sessions'],
            ['cache', 'connection', 'other'], ['cache', 'lock_connection', 'other'],
            ['cache', 'table', 'other_cache'], ['cache', 'lock_table', 'other_locks'],
            ['auth', 'defaults.guard', 'other'], ['auth', 'guards.web.driver', 'other'],
            ['auth', 'guards.web.provider', 'other'], ['auth', 'providers.users.model', 'OtherModel']];
    }

    #[DataProvider('environmentNames')]
    public function test_secondary_environment_override_is_rejected_before_any_connection(string $name): void
    {
        $env = ['APP_ENV' => 'testing', 'DB_CONNECTION' => 'mysql', 'DB_HOST' => '127.0.0.1',
            'DB_PORT' => '3307', 'DB_DATABASE' => 'vessel_gateway_codex_test', 'DB_USERNAME' => 'vgw_codex',
            'DB_PASSWORD' => '', 'VG_MYSQL_TEST_ACK' => 'vessel_gateway_codex_test', $name => 'unapproved-secondary'];
        $this->expectException(\RuntimeException::class);
        MySqlIsolation::assertEnvironment($env);
    }

    public static function environmentNames(): array
    {
        return array_map(static fn ($name) => [$name], ['SESSION_CONNECTION', 'SESSION_TABLE', 'DB_CACHE_CONNECTION',
            'DB_CACHE_LOCK_CONNECTION', 'DB_CACHE_TABLE', 'DB_CACHE_LOCK_TABLE']);
    }
}
