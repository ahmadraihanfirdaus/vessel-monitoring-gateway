<?php

namespace Tests\Unit;

use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use ReflectionMethod;
use RuntimeException;
use Symfony\Component\Process\Process;
use Tests\Support\HostedMySqlService;
use Tests\Support\MySqlIsolation;

/** Injected IO policy tests, not evidence of Linux/Docker or hosted execution. */
class HostedMySqlDiagnosticsTest extends TestCase
{
    private const ID = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
    private const UUID = '12345678-abcd-abcd-abcd-123456789abc';

    private static function service(): array
    {
        return ['id' => self::ID, 'image' => 'mysql:8.0', 'running' => true, 'binds' => 0,
            'privileged' => false, 'network' => 'owned-ci-network',
            'ports' => ['3306/tcp' => [['HostIp' => '127.0.0.1', 'HostPort' => '3306']], '33060/tcp' => null],
            'mounts' => [['type' => 'volume', 'destination' => '/var/lib/mysql']]];
    }

    private function invoke(string $method, mixed ...$args): mixed
    {
        $reflection = new ReflectionMethod(HostedMySqlService::class, $method);
        $this->assertTrue($reflection->isPrivate(), 'No runtime injection or authorization bypass API.');

        return $reflection->invoke(null, ...$args);
    }

    private function denied(string $code, callable $operation): void
    {
        try {
            $operation();
            $this->fail('Unsafe proof admitted.');
        } catch (RuntimeException $exception) {
            $this->assertSame('MYSQL_TEST_BLOCKED: '.$code.'.', $exception->getMessage());
            $this->assertNull($exception->getPrevious(), 'Do not attach raw command errors.');
            $this->assertStringNotContainsString('synthetic-sensitive-marker', $exception->getMessage());
        }
    }

    public function test_success_preserves_fixed_socket_commands_query_and_template(): void
    {
        $calls = [];
        $uuid = $this->invoke('serviceProof', self::ID, static function ($command, $reason) use (&$calls) {
            $calls[] = [$command, $reason];

            return count($calls) === 1 ? json_encode(self::service(), JSON_THROW_ON_ERROR) : self::UUID;
        });
        $this->assertSame(self::UUID, $uuid);
        $this->assertCount(2, $calls);
        $this->assertSame(['docker', '--host=unix:///var/run/docker.sock', 'inspect', '--format'], array_slice($calls[0][0], 0, 4));
        $this->assertSame(self::ID, $calls[0][0][5]);
        $this->assertSame('DOCKER_INSPECT_FAILED', $calls[0][1]);
        $this->assertSame(['docker', '--host=unix:///var/run/docker.sock', 'exec', self::ID,
            'mysql', '--user=root', '--batch', '--skip-column-names', '--execute=SELECT @@server_uuid'], $calls[1][0]);
        $this->assertSame('MYSQL_UUID_QUERY_FAILED', $calls[1][1]);
        $this->assertStringNotContainsString('Config.Env', $calls[0][0][4]);
        $this->assertStringNotContainsString('$m.Source', $calls[0][0][4]);
    }

    public static function ids(): iterable
    {
        yield 'absent' => [null, 'SERVICE_CONTAINER_ID_MISSING'];
        yield 'empty' => ['', 'SERVICE_CONTAINER_ID_MISSING'];
        foreach (['short', str_repeat('A', 64), str_repeat('a', 65), 'synthetic-sensitive-marker', [], 1] as $i => $bad) {
            yield 'invalid_'.$i => [$bad, 'SERVICE_IDENTITY_MISMATCH'];
        }
    }

    #[DataProvider('ids')]
    public function test_missing_and_invalid_id_denied_before_event_or_command(mixed $id, string $code): void
    {
        $this->denied($code, fn () => HostedMySqlService::verify(['VG_CI_MYSQL_CONTAINER_ID' => $id]));
    }

    public static function inspectJson(): iterable
    {
        foreach (['', '{', 'null', 'false', '1', '"synthetic-sensitive-marker"', '[]', '[{}]'] as $i => $raw) {
            yield 'malformed_or_nonobject_'.$i => [$raw];
        }
    }

    #[DataProvider('inspectJson')]
    public function test_invalid_json_stops_before_uuid_query(string $raw): void
    {
        $count = 0;
        $command = static function () use (&$count, $raw) { $count++; return $raw; };
        $this->denied('DOCKER_INSPECT_JSON_INVALID', fn () => $this->invoke('serviceProof', self::ID, $command));
        $this->assertSame(1, $count);
    }

    public function test_inspect_failure_is_static_and_stops_later_io(): void
    {
        $count = 0;
        $command = static function () use (&$count) { $count++; throw new \Error('synthetic-sensitive-marker'); };
        $this->denied('DOCKER_INSPECT_FAILED', fn () => $this->invoke('serviceProof', self::ID, $command));
        $this->assertSame(1, $count);
    }

    public function test_uuid_command_failure_is_distinct_from_invalid_uuid(): void
    {
        $count = 0;
        $command = static function () use (&$count) {
            if (++$count === 1) { return json_encode(self::service(), JSON_THROW_ON_ERROR); }
            throw new RuntimeException('synthetic-sensitive-marker');
        };
        $this->denied('MYSQL_UUID_QUERY_FAILED', fn () => $this->invoke('serviceProof', self::ID, $command));
        $this->assertSame(2, $count);
    }

    public static function uuids(): iterable
    {
        foreach (['', 'not-a-uuid', strtoupper(self::UUID), self::UUID."\n", [], 123, null] as $i => $bad) {
            yield 'invalid_'.$i => [$bad];
        }
    }

    #[DataProvider('uuids')]
    public function test_invalid_uuid_has_its_own_code(mixed $bad): void
    {
        $count = 0;
        $command = static function () use (&$count, $bad) {
            return ++$count === 1 ? json_encode(self::service(), JSON_THROW_ON_ERROR) : $bad;
        };
        $this->denied('MYSQL_UUID_INVALID', fn () => $this->invoke('serviceProof', self::ID, $command));
        $this->assertSame(2, $count);
    }

    public static function properties(): iterable
    {
        yield 'image' => ['image', 'other', 'IMAGE'];
        yield 'running' => ['running', false, 'RUNNING'];
        yield 'bind_mounts' => ['binds', 1, 'BINDS'];
        yield 'null_binds' => ['binds', null, 'BINDS'];
        yield 'string_zero_not_integer' => ['binds', '0', 'BINDS'];
        yield 'privileged' => ['privileged', true, 'PRIVILEGED'];
        yield 'missing_network' => ['network', null, 'NETWORK'];
        yield 'host_network' => ['network', 'host', 'NETWORK'];
        yield 'no_network' => ['network', 'none', 'NETWORK'];
        yield 'wrong_mounts' => ['mounts', [], 'MOUNTS'];
        yield 'wrong_binding' => ['ports', ['3306/tcp' => [['HostIp' => '0.0.0.0', 'HostPort' => '3306']]], 'PORT_BINDING'];
        yield 'malformed_binding' => ['ports', 'synthetic-sensitive-marker', 'PORT_BINDING'];
        yield 'additional_binding' => ['ports', ['3306/tcp' => [['HostIp' => '127.0.0.1', 'HostPort' => '3306']],
            '33060/tcp' => [['HostIp' => '127.0.0.1', 'HostPort' => '33060']]], 'EXTRA_PUBLICATION'];
    }

    #[DataProvider('properties')]
    public function test_each_property_fails_with_fixed_category(string $key, mixed $value, string $category): void
    {
        $service = array_replace(self::service(), [$key => $value]);
        $count = 0;
        $this->denied('SERVICE_PROPERTY_MISMATCH '.$category, fn () => $this->invoke('serviceProof', self::ID,
            static function () use (&$count, $service) {
                return ++$count === 1 ? json_encode($service, JSON_THROW_ON_ERROR) : self::UUID;
            }));
    }

    public function test_mismatched_inspected_and_connected_identities_are_denied(): void
    {
        $service = array_replace(self::service(), ['id' => str_repeat('b', 64)]);
        $count = 0;
        $this->denied('SERVICE_IDENTITY_MISMATCH', fn () => $this->invoke('serviceProof', self::ID,
            static function () use (&$count, $service) {
                return ++$count === 1 ? json_encode($service, JSON_THROW_ON_ERROR) : self::UUID;
            }));
        $this->denied('SERVICE_IDENTITY_MISMATCH', fn () => MySqlIsolation::assertConnectedService(
            ['_verified_ci_uuid' => self::UUID], self::UUID, '12345678-abcd-abcd-abcd-123456789abd'));
    }

    public function test_command_bound_success_and_failures_never_echo_stdout_or_stderr(): void
    {
        $this->assertSame(8192, strlen($this->invoke('command', [PHP_BINARY, '-r', 'echo str_repeat("x",8192);'], 'DOCKER_INSPECT_FAILED')));
        foreach (['DOCKER_INSPECT_FAILED', 'MYSQL_UUID_QUERY_FAILED'] as $code) {
            $this->denied($code, fn () => $this->invoke('command', [PHP_BINARY, '-r',
                'fwrite(STDERR,"synthetic-sensitive-marker");exit(2);'], $code));
            $this->denied($code, fn () => $this->invoke('command', [PHP_BINARY, '-r', 'echo str_repeat("x",8193);'], $code));
        }
    }

    public function test_existing_five_second_command_timeout_remains_fail_closed(): void
    {
        $this->denied('DOCKER_INSPECT_FAILED', fn () => $this->invoke('command', [PHP_BINARY, '-r', 'sleep(15);'], 'DOCKER_INSPECT_FAILED'));
    }

    public static function codes(): iterable
    {
        foreach (['SERVICE_CONTAINER_ID_MISSING', 'DOCKER_INSPECT_FAILED', 'DOCKER_INSPECT_JSON_INVALID',
            'SERVICE_PROPERTY_MISMATCH', 'MYSQL_UUID_QUERY_FAILED', 'MYSQL_UUID_INVALID', 'SERVICE_IDENTITY_MISMATCH'] as $code) {
            yield $code => [$code];
        }
    }

    #[DataProvider('codes')]
    public function test_real_cli_gates_preserve_static_reason_without_any_database(string $code): void
    {
        $root = dirname(__DIR__, 4);
        $message = var_export('MYSQL_TEST_BLOCKED: '.$code.'.', true);
        foreach (['mysql_test_gate.php', 'live_http_fixture.php'] as $script) {
            // Definitions live only in this ephemeral child. The actual gate catch runs;
            // admission throws before any app, connection, migration or fixture exists.
            $fake = $script === 'mysql_test_gate.php'
                ? 'final class TestEnvironment {public static function prepare($x){return [];}} final class MySqlIsolation {public static function processEnvironment(){throw new \\RuntimeException('.$message.');}}'
                : 'final class LiveHttpSafety {public static function fromEnvironment(){return [];} public static function application($p){throw new \\RuntimeException('.$message.');}}';
            $source = 'namespace Tests\\Support {'.$fake.'} namespace {require '.var_export($root.'/scripts/'.$script, true).';}';
            $process = new Process([PHP_BINARY, '-r', $source]);
            $process->setTimeout(10);
            $this->assertSame(3, $process->run());
            $this->assertSame('', $process->getOutput());
            $this->assertStringContainsString('MYSQL_TEST_BLOCKED: '.$code.'.', $process->getErrorOutput());
        }
    }

    public function test_diagnostic_vocabulary_cannot_echo_unapproved_values(): void
    {
        $exception = $this->invoke('blocked', 'synthetic-sensitive-marker', 'synthetic-sensitive-marker');
        $this->assertSame('MYSQL_TEST_BLOCKED: SERVICE_IDENTITY_MISMATCH.', $exception->getMessage());
        $verify = new ReflectionMethod(HostedMySqlService::class, 'verify');
        $this->assertTrue($verify->isPublic());
        $this->assertSame(1, $verify->getNumberOfParameters());
    }
}
