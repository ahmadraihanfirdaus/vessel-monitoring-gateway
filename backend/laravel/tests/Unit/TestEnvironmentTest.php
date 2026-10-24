<?php

namespace Tests\Unit;

use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use RuntimeException;
use Tests\Support\TestEnvironment;

class TestEnvironmentTest extends TestCase
{
    private static function values(): array
    {
        return ['APP_ENV' => 'testing', 'DB_CONNECTION' => 'mysql', 'DB_HOST' => '127.0.0.1',
            'DB_PORT' => '3307', 'DB_DATABASE' => 'vessel_gateway_codex_test',
            'DB_USERNAME' => 'vgw_codex', 'DB_PASSWORD' => ''];
    }

    public function test_exact_file_and_matching_override_layers_are_accepted(): void
    {
        $values = self::values();
        TestEnvironment::assertFileAndOverrides($values, [], $values, ['DB_URL' => '']);
        $this->addToAssertionCount(1);
    }

    public static function conflictingOverrides(): iterable
    {
        foreach (['APP_ENV' => 'production', 'DB_CONNECTION' => 'sqlite', 'DB_HOST' => 'other',
            'DB_PORT' => '3306', 'DB_DATABASE' => 'vessel_monitoring_gateway_test', 'DB_USERNAME' => 'vg_gateway_test',
            'DB_PASSWORD' => 'different-synthetic', 'DB_URL' => 'mysql://synthetic.invalid',
            'DATABASE_URL' => 'mysql://synthetic.invalid', 'DB_SOCKET' => '/tmp/mysql.sock',
            'VG_MYSQL_TEST_ACK' => 'other', 'GITHUB_ACTIONS' => 'true'] as $key => $value) {
            foreach ([0, 1, 2] as $layer) {
                yield $key.'_layer_'.$layer => [$key, $value, $layer];
            }
        }
    }

    #[DataProvider('conflictingOverrides')]
    public function test_every_environment_layer_conflict_is_rejected(string $key, string $value, int $layer): void
    {
        $layers = [[], [], []];
        $layers[$layer][$key] = $value;
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('MYSQL_TEST_BLOCKED: process environment conflicts');
        TestEnvironment::assertFileAndOverrides(self::values(), ...$layers);
    }

    public static function unsafeFiles(): iterable
    {
        foreach (self::values() as $key => $value) {
            yield 'missing_'.$key => [[$key => null]];
        }
        yield 'old_target' => [['DB_DATABASE' => 'vessel_monitoring_gateway_test']];
        yield 'url' => [['DB_URL' => 'mysql://synthetic.invalid']];
        yield 'socket' => [['DB_SOCKET' => '/tmp/mysql.sock']];
    }

    #[DataProvider('unsafeFiles')]
    public function test_unapproved_file_values_never_reach_connection(array $changes): void
    {
        $this->expectException(RuntimeException::class);
        TestEnvironment::assertFileAndOverrides(array_replace(self::values(), $changes));
    }
}
