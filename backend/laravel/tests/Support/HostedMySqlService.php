<?php

namespace Tests\Support;

use RuntimeException;
use Symfony\Component\Process\Process;

/** Test-only runner/service proof. Environment selection is not authorization. */
final class HostedMySqlService
{
    public static function assertContext(array $env, string $os, array $event): void
    {
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
            || preg_match('~\Aahmadraihanfirdaus/vessel-monitoring-gateway/\.github/workflows/phase9-multi-context-ci\.yml@refs/(?:heads/main|pull/[1-9][0-9]*/merge)\z~', $env['GITHUB_WORKFLOW_REF'] ?? '') !== 1
            || preg_match('/\A[a-f0-9]{64}\z/', $env['VG_CI_MYSQL_CONTAINER_ID'] ?? '') !== 1) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: approved workflow and service context required.');
        }
    }

    public static function assertService(array $service, string $id, string $uuid): void
    {
        if (preg_match('/\A[a-f0-9]{64}\z/', $id) !== 1
            || ($service['id'] ?? null) !== $id || ($service['image'] ?? null) !== 'mysql:8.0'
            || ($service['running'] ?? null) !== true || ($service['binds'] ?? null) !== 0
            || ($service['privileged'] ?? null) !== false || ! is_string($service['network'] ?? null)
            || in_array($service['network'], ['', 'host', 'none'], true)
            || ($service['mounts'] ?? null) !== [['type' => 'volume', 'destination' => '/var/lib/mysql']]
            || ($service['ports']['3306/tcp'] ?? null) !== [['HostIp' => '127.0.0.1', 'HostPort' => '3306']]
            || preg_match('/\A[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\z/', $uuid) !== 1) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: ephemeral loopback MySQL service proof required.');
        }
        foreach ($service['ports'] as $port => $bindings) {
            if ($port !== '3306/tcp' && $bindings !== null) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: unexpected service publication.');
            }
        }
    }

    private static function command(array $command): string
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
            throw new RuntimeException('MYSQL_TEST_BLOCKED: service verification unavailable.');
        }
    }

    public static function verify(array $env): string
    {
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
        $id = $env['VG_CI_MYSQL_CONTAINER_ID'];
        // Select safe properties in Docker itself: never request Config.Env or mount source paths.
        $format = '{"id":{{json .Id}},"image":{{json .Config.Image}},"running":{{json .State.Running}},'
            .'"binds":{{len .HostConfig.Binds}},"privileged":{{json .HostConfig.Privileged}},'
            .'"network":{{json .HostConfig.NetworkMode}},"ports":{{json .NetworkSettings.Ports}},'
            .'"mounts":[{{range $i, $m := .Mounts}}{{if $i}},{{end}}{"type":{{json $m.Type}},"destination":{{json $m.Destination}}}{{end}}]}';
        try {
            $service = json_decode(self::command(['docker', '--host=unix:///var/run/docker.sock', 'inspect', '--format', $format, $id]), true, flags: JSON_THROW_ON_ERROR);
            // Read-only query inside this exact service; match it to the TCP connection later.
            $uuid = self::command(['docker', '--host=unix:///var/run/docker.sock', 'exec', $id, 'mysql', '--user=root', '--batch', '--skip-column-names',
                '--execute=SELECT @@server_uuid']);
            self::assertService(is_array($service) ? $service : [], $id, $uuid);

            return $uuid;
        } catch (\Throwable $exception) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: isolated service identity unavailable.');
        }
    }
}
