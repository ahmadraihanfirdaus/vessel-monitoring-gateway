<?php

namespace Tests\Unit;

use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;
use ReflectionMethod;
use RuntimeException;
use Symfony\Component\Process\Exception\ProcessStartFailedException;
use Symfony\Component\Process\Exception\ProcessTimedOutException;
use Symfony\Component\Process\Process;
use Tests\Support\HostedMySqlService;

/** Real isolated child boundaries; no Docker daemon or database credentials. */
class DockerInspectProcessTest extends TestCase
{
    private const MARKER = 'synthetic-sensitive-marker';

    private function child(array $command, array $options = []): array
    {
        $source = 'require '.var_export(dirname(__DIR__, 2).'/vendor/autoload.php', true).';'
            .'$m=new ReflectionMethod(Tests\\Support\\HostedMySqlService::class,"command");'
            .'try {$out=$m->invoke(null,'.var_export($command, true).',"DOCKER_INSPECT_FAILED");echo "SUCCESS ".strlen($out);}'
            .'catch(Throwable $e){echo $e->getMessage();exit(3);}';
        $process = new Process([PHP_BINARY, ...$options, '-r', $source]);
        $process->setTimeout(10);
        $exit = $process->run();
        $stderr = $process->getErrorOutput();
        $this->assertStringNotContainsString(self::MARKER, $stderr);
        $this->assertStringNotContainsString('vendor/autoload.php', $stderr);
        $this->assertStringNotContainsString('C:\\', $stderr);
        $lines = array_values(array_filter(explode("\n", trim($stderr))));
        if ($exit === 0) {
            $this->assertSame([], $lines);
            return [$exit, $process->getOutput(), null];
        }
        $this->assertSame(3, $exit, 'Runner refusal code is separate from the recorded child exit.');
        $this->assertSame('MYSQL_TEST_BLOCKED: DOCKER_INSPECT_FAILED.', $process->getOutput());
        $this->assertCount(1, $lines, 'Exactly one bounded structured record; no raw stderr.');
        $prefix = 'MYSQL_INSPECT_DIAGNOSTIC=';
        $this->assertStringStartsWith($prefix, $lines[0]);
        $this->assertLessThan(512, strlen($lines[0]));
        $data = json_decode(substr($lines[0], strlen($prefix)), true, flags: JSON_THROW_ON_ERROR);
        $this->assertSame(['phase','class','child_exit','elapsed_ms','elapsed_capped','stdout_bytes_observed','stdout_capped','stdout_limit_bytes'], array_keys($data));
        $this->assertSame('DOCKER_INSPECT_COMMAND', $data['phase']);
        $this->assertIsInt($data['elapsed_ms']);
        $this->assertGreaterThanOrEqual(0, $data['elapsed_ms']);
        $this->assertLessThanOrEqual(10000, $data['elapsed_ms']);
        $this->assertIsBool($data['elapsed_capped']);
        $this->assertIsBool($data['stdout_capped']);
        $this->assertLessThanOrEqual(8193, $data['stdout_bytes_observed']);
        $this->assertSame(8192, $data['stdout_limit_bytes']);

        return [$exit, $process->getOutput(), $data];
    }

    public static function stderrClasses(): iterable
    {
        yield 'nil_template' => ['template parsing error: error calling len: synthetic-sensitive-marker', 'TEMPLATE_NIL_LENGTH'];
        yield 'template_syntax_or_field' => ['template parsing error: synthetic-sensitive-marker', 'TEMPLATE_ERROR'];
        yield 'container' => ['No such container: synthetic-sensitive-marker', 'CONTAINER_NOT_FOUND'];
        yield 'object' => ['No such object: synthetic-sensitive-marker', 'CONTAINER_NOT_FOUND'];
        yield 'daemon' => ['Cannot connect to the Docker daemon synthetic-sensitive-marker', 'DAEMON_UNREACHABLE'];
        yield 'connect' => ['error during connect: synthetic-sensitive-marker', 'DAEMON_UNREACHABLE'];
        yield 'socket_permission' => ['permission denied while trying to connect synthetic-sensitive-marker', 'DAEMON_UNREACHABLE'];
        yield 'unrecognized_nonzero' => ['synthetic-sensitive-marker', 'CHILD_NONZERO'];
    }

    #[DataProvider('stderrClasses')]
    public function test_real_nonzero_child_is_classified_without_raw_output(string $stderr, string $expected): void
    {
        [, , $data] = $this->child([PHP_BINARY, '-r', 'echo "'.self::MARKER.'";fwrite(STDERR,'.var_export($stderr, true).');exit(7);']);
        $this->assertSame($expected, $data['class']);
        $this->assertSame(7, $data['child_exit']);
        $this->assertSame(strlen(self::MARKER), $data['stdout_bytes_observed']);
    }

    public function test_missing_executable_is_distinct_from_exit_of_existing_executable(): void
    {
        [, , $data] = $this->child(['vg-owned-fixture-executable-not-present-20261028']);
        $this->assertSame('EXECUTABLE_NOT_FOUND', $data['class']);
    }

    public function test_proc_open_unavailable_is_distinct_from_start_or_child_failure(): void
    {
        [, , $data] = $this->child([PHP_BINARY, '-r', 'exit(0);'], ['-d', 'disable_functions=proc_open']);
        $this->assertSame('PROC_OPEN_UNAVAILABLE', $data['class']);
        $this->assertNull($data['child_exit']);
    }

    public function test_real_five_second_timeout_still_fails_closed(): void
    {
        // Exceeds the real 5s policy, fits the unchanged 10s outer test supervisor
        // even when Windows waits for inherited child pipe handles to close.
        [, , $data] = $this->child([PHP_BINARY, '-r', 'sleep(7);']);
        $this->assertSame('TIMEOUT', $data['class']);
        $this->assertGreaterThanOrEqual(4900, $data['elapsed_ms']);
    }

    public static function sizes(): iterable
    {
        yield 'first_disallowed_byte' => [8193, false];
        yield 'bounded_count' => [32768, true];
    }

    #[DataProvider('sizes')]
    public function test_output_bound_is_retained_and_observed_count_is_capped(int $size, bool $capped): void
    {
        [, , $data] = $this->child([PHP_BINARY, '-r', 'echo str_repeat("x",'.$size.');']);
        $this->assertSame('OUTPUT_LIMIT', $data['class']);
        $this->assertSame(0, $data['child_exit']);
        $this->assertSame(8193, $data['stdout_bytes_observed']);
        $this->assertSame($capped, $data['stdout_capped']);
    }

    public function test_success_at_bound_and_empty_success_are_not_reclassified_as_child_failures(): void
    {
        foreach ([0, 8192] as $size) {
            [$exit, $out, $diagnostic] = $this->child([PHP_BINARY, '-r', 'echo str_repeat("x",'.$size.');']);
            $this->assertSame(0, $exit);
            $this->assertSame('SUCCESS '.$size, $out);
            $this->assertNull($diagnostic);
        }
    }

    public function test_exception_classification_uses_types_and_never_exception_messages(): void
    {
        $method = new ReflectionMethod(HostedMySqlService::class, 'inspectFailureClass');
        $this->assertTrue($method->isPrivate());
        $process = new Process([PHP_BINARY, '-r', 'exit(0);']);
        foreach ([
            [new ProcessStartFailedException($process, self::MARKER), 'PROCESS_START_EXCEPTION'],
            [new RuntimeException(self::MARKER), 'PROCESS_RUNTIME_EXCEPTION'],
            [new ProcessTimedOutException($process, ProcessTimedOutException::TYPE_GENERAL), 'TIMEOUT'],
        ] as [$exception, $expected]) {
            $this->assertSame($expected, $method->invoke(null, $exception, true, true, null, false, self::MARKER));
        }
    }

    public function test_formatter_fix_does_not_change_inspect_arguments_or_identity_policy(): void
    {
        $calls = [];
        $method = new ReflectionMethod(HostedMySqlService::class, 'serviceProof');
        try {
            $method->invoke(null, str_repeat('a', 64), static function ($command) use (&$calls) {
                $calls[] = $command;
                throw new RuntimeException(self::MARKER);
            });
            $this->fail('Inspect refusal must stop UUID and all subsequent access.');
        } catch (RuntimeException $error) {
            $this->assertSame('MYSQL_TEST_BLOCKED: DOCKER_INSPECT_FAILED.', $error->getMessage());
        }
        $this->assertCount(1, $calls);
        $this->assertSame(['docker', '--host=unix:///var/run/docker.sock', 'inspect', '--format'], array_slice($calls[0], 0, 4));
        $this->assertCount(6, $calls[0]);
        $this->assertStringContainsString('{{if .HostConfig.Binds}}{{len .HostConfig.Binds}}{{else}}0{{end}}', $calls[0][4]);
    }
}
