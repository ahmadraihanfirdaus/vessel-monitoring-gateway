<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Support\DependencyUnavailableResponse;
use App\Services\DeviceReadService;
use App\Services\DeviceTokenAuthenticator;
use App\Services\EventIngestService;
use App\Services\TelemetryIngestService;
use Illuminate\Database\QueryException;
use Mockery;
use RuntimeException;
use Tests\TestCase;

/** Laravel dispatch with service doubles; the DB port is unreachable on purpose. */
class Phase9B11DependencyUnavailableTest extends TestCase
{
    private const TOKEN = 'b11-fixture-bearer-token-12345678901234567890123';

    private function device(): Device
    {
        $device = new Device();
        $device->device_id = 'b11-device';
        $device->enabled = true;
        return $device;
    }

    private function fakeAuth(?\Throwable $error = null): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $call = $auth->shouldReceive('resolve')->once()->with(self::TOKEN);
        if ($error !== null) {
            $call->andThrow($error);
        } else {
            $call->andReturn($this->device());
        }
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function outage(): QueryException
    {
        // Construction only, never a query or PDO connection.
        return new QueryException(
            'mysql',
            'SELECT <fixture-only>',
            [],
            new \PDOException('synthetic b11 storage failure', 2002)
        );
    }

    private function assertUnavailable($response): void
    {
        $response->assertStatus(503)
            ->assertJson(['error' => 'backend_temporarily_unavailable'])
            ->assertHeader('Retry-After', '5');
        $body = json_encode($response->json(), JSON_THROW_ON_ERROR);
        $this->assertStringNotContainsString('SELECT', $body);
        $this->assertStringNotContainsString('PDO', $body);
        $this->assertStringNotContainsString(self::TOKEN, $body);
    }

    private function telemetry(): array
    {
        return [
            'schema_version' => '1.0', 'device_id' => 'b11-device',
            'firmware_version' => 'b11-fw', 'boot_id' => 'b11-boot',
            'sequence' => 1, 'uptime_ms' => 1000,
            'source_mode' => 'simulation',
            'channels' => ['temperature_c' => ['value' => 25.0, 'quality' => 'valid']],
        ];
    }

    private function event(): array
    {
        return [
            'schema_version' => '1.0', 'device_id' => 'b11-device',
            'boot_id' => 'b11-boot', 'event_id' => 1,
            'linked_alarm_id' => 1, 'source_id' => 1,
            'source_mode' => 'simulation', 'event_type' => 'alarm_raised',
            'occurred_at_ms' => 1000,
        ];
    }

    public function test_sec002_storage_outage_during_auth_returns_503_not_401(): void
    {
        $this->fakeAuth($this->outage());
        $this->assertUnavailable(
            $this->withToken(self::TOKEN)->getJson('/api/v1/device/state')
        );
    }

    public function test_sec002_invalid_token_still_returns_401(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->once()->with(self::TOKEN)->andReturn(null);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/health')
            ->assertUnauthorized()->assertJson(['error' => 'invalid_device_authentication']);
    }

    public function test_net001_telemetry_storage_outage_returns_503_without_sql(): void
    {
        $this->fakeAuth();
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->once()->andThrow($this->outage());
        $this->app->instance(TelemetryIngestService::class, $service);
        $this->assertUnavailable($this->withToken(self::TOKEN)
            ->postJson('/api/v1/telemetry', $this->telemetry()));
    }

    public function test_net002_event_storage_outage_returns_503(): void
    {
        $this->fakeAuth();
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldReceive('ingest')->once()->andThrow($this->outage());
        $this->app->instance(EventIngestService::class, $service);
        $this->assertUnavailable($this->withToken(self::TOKEN)
            ->postJson('/api/v1/events', $this->event()));
    }

    public function test_ui002_state_storage_outage_returns_503(): void
    {
        $this->fakeAuth();
        $read = Mockery::mock(DeviceReadService::class);
        $read->shouldReceive('state')->once()->andThrow($this->outage());
        $this->app->instance(DeviceReadService::class, $read);
        $this->assertUnavailable($this->withToken(self::TOKEN)
            ->getJson('/api/v1/device/state'));
    }

    public function test_ui002_history_storage_outage_returns_503(): void
    {
        $this->fakeAuth();
        $read = Mockery::mock(DeviceReadService::class);
        $read->shouldReceive('history')->once()->andThrow($this->outage());
        $this->app->instance(DeviceReadService::class, $read);
        $this->assertUnavailable($this->withToken(self::TOKEN)
            ->getJson('/api/v1/device/history?limit=2'));
    }

    public function test_ui002_health_storage_outage_returns_503(): void
    {
        $this->fakeAuth();
        $read = Mockery::mock(DeviceReadService::class);
        $read->shouldReceive('health')->once()->andThrow($this->outage());
        $this->app->instance(DeviceReadService::class, $read);
        $this->assertUnavailable($this->withToken(self::TOKEN)
            ->getJson('/api/v1/device/health'));
    }

    public function test_sys003_programming_exception_is_not_silently_503(): void
    {
        $this->fakeAuth();
        $read = Mockery::mock(DeviceReadService::class);
        $read->shouldReceive('state')->once()->andThrow(new RuntimeException('b11-programming-defect'));
        $this->app->instance(DeviceReadService::class, $read);
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/state')->assertStatus(500);
    }

    public function test_api001_sql_syntax_exception_not_disguised_as_503(): void
    {
        $syntaxError = new QueryException(
            'mysql',
            'SELECT invalid fixture only',
            [],
            new \PDOException('synthetic invalid query', 1064)
        );
        $this->assertNull(DependencyUnavailableResponse::forConnectionFailure($syntaxError));
    }

}
