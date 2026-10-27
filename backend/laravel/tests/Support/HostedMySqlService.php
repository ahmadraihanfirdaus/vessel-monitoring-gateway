<?php

namespace Tests\Support;

use RuntimeException;
use Symfony\Component\Process\Process;

/** Test-only runner/service proof. Environment selection is not authorization. */
final class HostedMySqlService
{
    private static function blocked(string $reason, ?string $property = null): RuntimeException
    {
        // Closed diagnostic vocabulary. Never include supplied values or exception chains.
        if (! in_array($reason, ['SERVICE_CONTAINER_ID_MISSING', 'DOCKER_INSPECT_FAILED',
            'DOCKER_INSPECT_JSON_INVALID', 'SERVICE_PROPERTY_MISMATCH', 'MYSQL_UUID_QUERY_FAILED',
            'MYSQL_UUID_INVALID', 'SERVICE_IDENTITY_MISMATCH'], true)
            || ($property !== null && ($reason !== 'SERVICE_PROPERTY_MISMATCH'
                || ! in_array($property, ['IMAGE', 'RUNNING', 'BINDS', 'PRIVILEGED', 'NETWORK',
                    'MOUNTS', 'PORT_BINDING', 'EXTRA_PUBLICATION'], true)))) {
            return new RuntimeException('MYSQL_TEST_BLOCKED: SERVICE_IDENTITY_MISMATCH.');
        }

        return new RuntimeException('MYSQL_TEST_BLOCKED: '.$reason.($property === null ? '' : ' '.$property).'.');
    }

    private static function assertContainerId(mixed $id): void
    {
        if ($id === null || $id === '') {
            throw self::blocked('SERVICE_CONTAINER_ID_MISSING');
        }
        if (! is_string($id) || preg_match('/\A[a-f0-9]{64}\z/', $id) !== 1) {
            throw self::blocked('SERVICE_IDENTITY_MISMATCH');
        }
    }

    public static function assertContext(array $env, string $os, array $event): void
    {
        self::assertContainerId($env['VG_CI_MYSQL_CONTAINER_ID'] ?? null);
        foreach (['GITHUB_ACTIONS' => 'true', 'CI' => 'true', 'RUNNER_ENVIRONMENT' => 'github-hosted',
            'RUNNER_OS' => 'Linux', 'GITHUB_REPOSITORY' => 'ahmadraihanfirdaus/vessel-monitoring-gateway',
            'GITHUB_JOB' => 'backend-mysql-isolated', 'GITHUB_WORKFLOW' => 'Phase 9 scoped host and Laravel CI'] as $name => $value) {
            if (($env[$name] ?? null) !== $value) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: hosted runner context required.');
            }
        }
        foreach (['DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH'] as $name) {
            if (! in_array($env[$name] ?? null, [null, ''], true)) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: Docker endpoint overrides prohibited.');
            }
        }
        if ($os !== 'Linux'
            || ! in_array($env['GITHUB_EVENT_NAME'] ?? null, ['workflow_dispatch', 'pull_request'], true)
            || ($event['repository']['full_name'] ?? null) !== 'ahmadraihanfirdaus/vessel-monitoring-gateway'
            || preg_match('~\Aahmadraihanfirdaus/vessel-monitoring-gateway/\.github/workflows/phase9-multi-context-ci\.yml@refs/(?:heads/main|pull/[1-9][0-9]*/merge)\z~', $env['GITHUB_WORKFLOW_REF'] ?? '') !== 1) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: approved workflow and service context required.');
        }
    }

    public static function assertService(array $service, string $id, string $uuid): void
    {
        self::assertContainerId($id);
        if (($service['id'] ?? null) !== $id) {
            throw self::blocked('SERVICE_IDENTITY_MISMATCH');
        }
        if (preg_match('/\A[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\z/', $uuid) !== 1) {
            throw self::blocked('MYSQL_UUID_INVALID');
        }
        $properties = [
            'IMAGE' => ($service['image'] ?? null) === 'mysql:8.0',
            'RUNNING' => ($service['running'] ?? null) === true,
            'BINDS' => ($service['binds'] ?? null) === 0,
            'PRIVILEGED' => ($service['privileged'] ?? null) === false,
            'NETWORK' => is_string($service['network'] ?? null) && ! in_array($service['network'], ['', 'host', 'none'], true),
            'MOUNTS' => ($service['mounts'] ?? null) === [['type' => 'volume', 'destination' => '/var/lib/mysql']],
            'PORT_BINDING' => is_array($service['ports'] ?? null)
                && ($service['ports']['3306/tcp'] ?? null) === [['HostIp' => '127.0.0.1', 'HostPort' => '3306']],
        ];
        foreach ($properties as $property => $matches) {
            if (! $matches) {
                throw self::blocked('SERVICE_PROPERTY_MISMATCH', $property);
            }
        }
        foreach ($service['ports'] as $port => $bindings) {
            if ($port !== '3306/tcp' && $bindings !== null) {
                throw self::blocked('SERVICE_PROPERTY_MISMATCH', 'EXTRA_PUBLICATION');
            }
        }
    }

    private static function command(array $command, string $reason): string
    {
        try {
            $process = new Process($command);
            $process->setTimeout(5);
            $process->run();
            $out = $process->getOutput();
            if (! $process->isSuccessful() || strlen($out) > 8192) {
                throw new RuntimeException();
            }

            return trim($out);
        } catch (\Throwable $exception) {
            // Never expose command failure output, environment, paths or Docker metadata.
            throw self::blocked($reason);
        }
    }

    public static function verify(array $env): string
    {
        self::assertContainerId($env['VG_CI_MYSQL_CONTAINER_ID'] ?? null);
        // Read only the public event identity; no environment file or runner credentials.
        $path = $env['GITHUB_EVENT_PATH'] ?? '';
        if (! is_string($path) || ! is_file($path) || is_link($path) || filesize($path) > 1048576) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: runner event proof unavailable.');
        }
        try {
            $event = json_decode(file_get_contents($path), true, flags: JSON_THROW_ON_ERROR);
        } catch (\Throwable $exception) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: runner event proof invalid.');
        }
        self::assertContext($env, PHP_OS_FAMILY, is_array($event) ? $event : []);

        return self::serviceProof($env['VG_CI_MYSQL_CONTAINER_ID'], self::command(...));
    }

    /** Private test seam; real admission always uses the actual command above. */
    private static function serviceProof(string $id, callable $command): string
    {
        self::assertContainerId($id);
        // Select safe properties in Docker itself: never request Config.Env or mount source paths.
        $format = '{"id":{{json .Id}},"image":{{json .Config.Image}},"running":{{json .State.Running}},'
            .'"binds":{{len .HostConfig.Binds}},"privileged":{{json .HostConfig.Privileged}},'
            .'"network":{{json .HostConfig.NetworkMode}},"ports":{{json .NetworkSettings.Ports}},'
            .'"mounts":[{{range $i, $m := .Mounts}}{{if $i}},{{end}}{"type":{{json $m.Type}},"destination":{{json $m.Destination}}}{{end}}]}';
        try {
            $raw = $command(['docker', '--host=unix:///var/run/docker.sock', 'inspect', '--format', $format, $id], 'DOCKER_INSPECT_FAILED');
        } catch (\Throwable $exception) {
            throw self::blocked('DOCKER_INSPECT_FAILED');
        }
        try {
            $service = json_decode($raw, true, flags: JSON_THROW_ON_ERROR);
        } catch (\Throwable $exception) {
            throw self::blocked('DOCKER_INSPECT_JSON_INVALID');
        }
        if (! is_array($service) || array_is_list($service)) {
            throw self::blocked('DOCKER_INSPECT_JSON_INVALID');
        }
        try {
            // Read-only query inside this exact service; match it to the TCP connection later.
            $uuid = $command(['docker', '--host=unix:///var/run/docker.sock', 'exec', $id, 'mysql', '--user=root', '--batch', '--skip-column-names',
                '--execute=SELECT @@server_uuid'], 'MYSQL_UUID_QUERY_FAILED');
        } catch (\Throwable $exception) {
            throw self::blocked('MYSQL_UUID_QUERY_FAILED');
        }
        if (! is_string($uuid)) {
            throw self::blocked('MYSQL_UUID_INVALID');
        }
        self::assertService($service, $id, $uuid);

        return $uuid;
    }
}
