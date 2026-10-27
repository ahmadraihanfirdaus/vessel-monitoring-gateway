<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use RuntimeException;
use Tests\Support\HostedMySqlService;
use Tests\Support\MySqlIsolation;

class HostedMySqlServiceTest extends TestCase
{
    private function context(): array
    {
        return ['GITHUB_ACTIONS' => 'true', 'CI' => 'true', 'RUNNER_ENVIRONMENT' => 'github-hosted',
            'RUNNER_OS' => 'Linux', 'GITHUB_REPOSITORY' => 'ahmadraihanfirdaus/vessel-monitoring-gateway',
            'GITHUB_JOB' => 'backend-mysql-isolated', 'GITHUB_WORKFLOW' => 'Phase 9 scoped host and Laravel CI',
            'GITHUB_WORKFLOW_REF' => 'ahmadraihanfirdaus/vessel-monitoring-gateway/.github/workflows/phase9-multi-context-ci.yml@refs/heads/main',
            'GITHUB_EVENT_NAME' => 'workflow_dispatch', 'VG_CI_MYSQL_CONTAINER_ID' => str_repeat('a', 64)];
    }

    private function event(): array
    {
        return ['repository' => ['full_name' => 'ahmadraihanfirdaus/vessel-monitoring-gateway']];
    }

    private function service(): array
    {
        return ['id' => str_repeat('a', 64), 'image' => 'mysql:8.0', 'running' => true, 'binds' => 0,
            'privileged' => false, 'network' => 'owned-ci-network',
            'ports' => ['3306/tcp' => [['HostIp' => '127.0.0.1', 'HostPort' => '3306']], '33060/tcp' => null],
            'mounts' => [['type' => 'volume', 'destination' => '/var/lib/mysql']]];
    }

    private function denied(callable $action): void
    {
        try {
            $action();
            $this->fail('Unsafe hosted profile admitted.');
        } catch (RuntimeException $exception) {
            $this->assertStringStartsWith('MYSQL_TEST_BLOCKED:', $exception->getMessage());
            $this->assertStringNotContainsString('synthetic-sensitive-marker', $exception->getMessage());
        }
    }

    public function test_synthetic_approved_context_and_ephemeral_service_proof(): void
    {
        HostedMySqlService::assertContext($this->context(), 'Linux', $this->event());
        HostedMySqlService::assertService($this->service(), str_repeat('a', 64), '12345678-abcd-abcd-abcd-123456789abc');
        $this->addToAssertionCount(2);
    }

    public function test_ci_flag_alone_laptop_self_hosted_and_wrong_workflows_are_denied(): void
    {
        $this->denied(fn () => HostedMySqlService::assertContext(['GITHUB_ACTIONS' => 'true'], 'Linux', $this->event()));
        $this->denied(fn () => HostedMySqlService::assertContext($this->context(), 'Windows', $this->event()));
        $this->denied(fn () => HostedMySqlService::assertContext($this->context(), 'Linux', []));
        foreach (array_keys($this->context()) as $key) {
            $this->denied(fn () => HostedMySqlService::assertContext(array_replace($this->context(), [$key => 'synthetic-sensitive-marker']), 'Linux', $this->event()));
        }
        foreach (['DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH'] as $key) {
            $this->denied(fn () => HostedMySqlService::assertContext($this->context() + [$key => 'synthetic-sensitive-marker'], 'Linux', $this->event()));
        }
    }

    public function test_wrong_or_persistent_or_public_services_are_denied(): void
    {
        foreach (['id' => str_repeat('b', 64), 'image' => 'mariadb:10', 'running' => false, 'binds' => 1,
            'privileged' => true, 'network' => 'host', 'mounts' => [],
            'ports' => ['3306/tcp' => [['HostIp' => '0.0.0.0', 'HostPort' => '3306']]]] as $key => $value) {
            $this->denied(fn () => HostedMySqlService::assertService(array_replace($this->service(), [$key => $value]),
                str_repeat('a', 64), '12345678-abcd-abcd-abcd-123456789abc'));
        }
        $service = $this->service();
        $service['ports']['33060/tcp'] = [['HostIp' => '127.0.0.1', 'HostPort' => '33060']];
        $this->denied(fn () => HostedMySqlService::assertService($service, str_repeat('a', 64), '12345678-abcd-abcd-abcd-123456789abc'));
        $this->denied(fn () => HostedMySqlService::assertService($this->service(), str_repeat('a', 64), 'invalid'));
    }

    public function test_ci_account_is_exact_root_and_no_other_database_is_admitted(): void
    {
        $env = ['GITHUB_ACTIONS' => 'true', 'APP_ENV' => 'testing', 'DB_CONNECTION' => 'mysql',
            'DB_HOST' => '127.0.0.1', 'DB_PORT' => '3306', 'DB_DATABASE' => 'vessel_gateway_ci',
            'DB_USERNAME' => 'root', 'DB_PASSWORD' => '', 'VG_MYSQL_TEST_ACK' => 'vessel_gateway_ci'];
        MySqlIsolation::assertEnvironment($env);
        $this->addToAssertionCount(1);
        foreach (['DB_HOST' => 'localhost', 'DB_PORT' => '3307', 'DB_DATABASE' => 'vessel_gateway',
            'DB_USERNAME' => 'vgw_codex', 'VG_MYSQL_TEST_ACK' => 'vessel_gateway_codex_test'] as $key => $value) {
            $this->denied(fn () => MySqlIsolation::assertEnvironment(array_replace($env, [$key => $value])));
        }
    }

    public function test_real_runtime_does_not_authorize_from_environment_only(): void
    {
        $this->denied(fn () => HostedMySqlService::verify($this->context() + ['GITHUB_EVENT_PATH' => '']));
    }

    public function test_connected_server_and_preflight_identity_cannot_drift(): void
    {
        $a = '12345678-abcd-abcd-abcd-123456789abc';
        $b = '12345678-abcd-abcd-abcd-123456789abd';
        MySqlIsolation::assertConnectedService(['_verified_ci_uuid' => $a], $a, $a);
        $this->addToAssertionCount(1);
        $this->denied(fn () => MySqlIsolation::assertConnectedService(['_verified_ci_uuid' => $a], $a, $b));
        $this->denied(fn () => MySqlIsolation::assertConnectedService(['_verified_ci_uuid' => $a], $b, $a));
        $this->denied(fn () => MySqlIsolation::assertConnectedService([], $a, $a));
        $this->denied(fn () => MySqlIsolation::assertConnectedService(['_verified_ci_uuid' => $a], $a, null));
    }
}
