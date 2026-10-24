<?php

namespace Tests\Unit;

use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use RuntimeException;
use Tests\Support\MySqlIsolation;

class MySqlIsolationTest extends TestCase
{
    private static function local(): array
    {
        return ['APP_ENV' => 'testing', 'DB_CONNECTION' => 'mysql', 'DB_HOST' => '127.0.0.1',
            'DB_PORT' => '3307', 'DB_DATABASE' => 'vessel_gateway_codex_test',
            'DB_USERNAME' => 'vgw_codex', 'DB_PASSWORD' => '',
            'VG_MYSQL_TEST_ACK' => 'vessel_gateway_codex_test'];
    }

    public function test_local_and_ephemeral_ci_targets_are_admitted(): void
    {
        MySqlIsolation::assertServer(self::local(), '10.4.32-MariaDB', 'vessel_gateway_codex_test',
            ['information_schema', 'vessel_gateway_codex_test']);
        $ci = array_replace(self::local(), ['GITHUB_ACTIONS' => 'true', 'DB_PORT' => '3306',
            'DB_DATABASE' => 'vessel_gateway_ci', 'VG_MYSQL_TEST_ACK' => 'vessel_gateway_ci', 'DB_USERNAME' => 'root']);
        MySqlIsolation::assertServer($ci, '8.4.6', 'vessel_gateway_ci', ['mysql', 'sys',
            'information_schema', 'performance_schema', 'vessel_gateway_ci']);
        $this->addToAssertionCount(2);
    }

    public function test_mariadb_default_catalog_requires_scoped_grants(): void
    {
        MySqlIsolation::assertServer(self::local(), '10.4.32-MariaDB', 'vessel_gateway_codex_test',
            ['information_schema', 'test', 'vessel_gateway_codex_test']);
        MySqlIsolation::assertLocalGrants([
            "GRANT USAGE ON *.* TO 'synthetic'@'localhost'",
            "GRANT ALL PRIVILEGES ON `vessel_gateway_codex_test`.* TO 'synthetic'@'localhost'",
        ]);
        $this->addToAssertionCount(2);
    }

    public static function unsafeGrants(): iterable
    {
        yield 'global_privilege' => [["GRANT SELECT ON *.* TO 'synthetic'@'localhost'"]];
        yield 'other_catalog' => [["GRANT ALL PRIVILEGES ON `other`.* TO 'synthetic'@'localhost'"]];
        yield 'default_test_write' => [["GRANT ALL PRIVILEGES ON `test`.* TO 'synthetic'@'localhost'"]];
        yield 'grant_option' => [["GRANT ALL PRIVILEGES ON `vessel_gateway_codex_test`.* TO 'synthetic'@'localhost' WITH GRANT OPTION"]];
        yield 'role' => [["GRANT synthetic_role TO 'synthetic'@'localhost'"]];
        yield 'usage_only' => [["GRANT USAGE ON *.* TO 'synthetic'@'localhost'"]];
        yield 'empty' => [[]];
    }

    #[DataProvider('unsafeGrants')]
    public function test_overprivileged_or_unrecognized_grants_are_denied(array $grants): void
    {
        $this->expectException(RuntimeException::class);
        MySqlIsolation::assertLocalGrants($grants);
    }

    public static function unsafeEnvironment(): iterable
    {
        foreach (['APP_ENV' => 'production', 'DB_CONNECTION' => 'sqlite', 'DB_HOST' => 'localhost',
            'DB_PORT' => '3306', 'DB_DATABASE' => 'vessel_gateway', 'DB_USERNAME' => 'root',
            'DB_PASSWORD' => null, 'VG_MYSQL_TEST_ACK' => '', 'DB_URL' => 'mysql://synthetic.invalid',
            'DATABASE_URL' => 'mysql://synthetic.invalid', 'DB_SOCKET' => '/tmp/mysql.sock'] as $key => $value) {
            yield $key => [[$key => $value]];
        }
        foreach (array_keys(self::local()) as $key) {
            yield 'missing_'.$key => [[$key => null]];
        }
        yield 'port_suffix' => [['DB_PORT' => '3307;unsafe']];
        yield 'database_suffix' => [['DB_DATABASE' => 'vessel_gateway_codex_test_extra']];
        yield 'ack_mismatch' => [['VG_MYSQL_TEST_ACK' => 'vessel_gateway_ci']];
    }

    #[DataProvider('unsafeEnvironment')]
    public function test_unsafe_environment_is_denied_before_connect(array $changes): void
    {
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('MYSQL_TEST_BLOCKED:');
        MySqlIsolation::assertEnvironment(array_replace(self::local(), $changes));
    }

    public static function unsafeServer(): iterable
    {
        yield 'wrong_mariadb_version' => ['10.4.31-MariaDB', 'vessel_gateway_codex_test', ['vessel_gateway_codex_test']];
        yield 'mysql5' => ['5.7.44', 'vessel_gateway_codex_test', ['vessel_gateway_codex_test']];
        yield 'maria_with_8_prefix' => ['8.0.44-MariaDB', 'vessel_gateway_codex_test', ['vessel_gateway_codex_test']];
        yield 'wrong_catalog' => ['8.0.44', 'other', ['vessel_gateway_codex_test']];
        yield 'unselected_catalog' => ['8.0.44', null, ['vessel_gateway_codex_test']];
        yield 'unrelated_visible_catalog' => ['8.0.44', 'vessel_gateway_codex_test', ['vessel_gateway_codex_test', 'other']];
        yield 'missing_catalog' => ['8.0.44', 'vessel_gateway_codex_test', ['information_schema']];
    }

    #[DataProvider('unsafeServer')]
    public function test_unsafe_server_is_denied(string $version, ?string $db, array $catalogs): void
    {
        $this->expectException(RuntimeException::class);
        MySqlIsolation::assertServer(self::local(), $version, $db, $catalogs);
    }

    public function test_denial_messages_do_not_echo_supplied_values(): void
    {
        try {
            MySqlIsolation::assertEnvironment(array_replace(self::local(), ['DB_DATABASE' => 'synthetic-sensitive-marker']));
            $this->fail('Unsafe catalog admitted.');
        } catch (RuntimeException $exception) {
            $this->assertStringNotContainsString('synthetic-sensitive-marker', $exception->getMessage());
        }
    }

    public function test_effective_configuration_must_match_admitted_target(): void
    {
        $env = self::local();
        $connection = ['driver' => 'mysql', 'host' => $env['DB_HOST'], 'port' => $env['DB_PORT'],
            'database' => $env['DB_DATABASE'], 'username' => $env['DB_USERNAME'], 'password' => ''];
        MySqlIsolation::assertEffectiveConfiguration($env, $connection, 'mysql');
        $this->addToAssertionCount(1);
        foreach (['driver' => 'sqlite', 'host' => 'other', 'port' => '3306', 'database' => 'other',
            'username' => 'root', 'password' => 'different', 'url' => 'mysql://synthetic.invalid',
            'unix_socket' => '/tmp/mysql.sock', 'read' => ['host' => 'other'],
            'write' => ['host' => 'other'], 'prefix' => 'other_'] as $key => $value) {
            try {
                MySqlIsolation::assertEffectiveConfiguration($env, array_replace($connection, [$key => $value]), 'mysql');
                $this->fail('Effective override admitted: '.$key);
            } catch (RuntimeException $exception) {
                $this->assertStringStartsWith('MYSQL_TEST_BLOCKED:', $exception->getMessage());
            }
        }
    }
}
