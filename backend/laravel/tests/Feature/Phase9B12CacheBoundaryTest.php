<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceReadService;
use App\Services\DeviceTokenAuthenticator;
use App\Services\EventIngestService;
use App\Services\TelemetryIngestService;
use Illuminate\Database\QueryException;
use Mockery;
use Tests\TestCase;

/** Actual Laravel route/middleware/controller dispatch, with no database access. */
class Phase9B12CacheBoundaryTest extends TestCase
{
    private const TOKEN = 'b12-fixture-token-1234567890-12345678901234567890';

    private function fakeAuth(bool $enabled = true): void
    {
        $device = new Device();
        $device->device_id = 'b12-device';
        $device->enabled = $enabled;
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->with(self::TOKEN)->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function checkNoStore($response, int $status): void
    {
        $response->assertStatus($status);
        $cache = (string) $response->headers->get('Cache-Control');
        $this->assertStringContainsString('no-store', $cache);
        $this->assertStringContainsString('private', $cache);
        $this->assertSame('no-cache', $response->headers->get('Pragma'));
        $this->assertContains('Authorization', $response->getVary());
    }

    private function telemetry(): array
    {
        return [
            'schema_version' => '1.0', 'device_id' => 'b12-device',
            'firmware_version' => 'b12-fixture', 'boot_id' => 'b12-boot',
            'sequence' => 2, 'uptime_ms' => 2000,
            'source_mode' => 'simulation',
            'channels' => ['temperature_c' => ['value' => 0, 'quality' => 'valid']],
        ];
    }

    private function event(): array
    {
        return [
            'schema_version' => '1.0', 'device_id' => 'b12-device',
            'boot_id' => 'b12-boot', 'event_id' => 2,
            'linked_alarm_id' => 0, 'source_id' => 2,
            'source_mode' => 'simulation', 'event_type' => 'alarm_raised',
            'occurred_at_ms' => 2000,
        ];
    }

    public function test_api001_wrong_content_type_receipts_are_never_cacheable(): void
    {
        foreach (['/api/v1/telemetry', '/api/v1/events'] as $route) {
            $response = $this->call('POST', $route, [], [], [], [
                'CONTENT_TYPE' => 'text/plain', 'HTTP_ACCEPT' => 'application/json',
            ], '{}');
            $this->checkNoStore($response, 415);
        }
    }

    public function test_api001_oversize_receipts_are_never_cacheable(): void
    {
        foreach (['/api/v1/telemetry', '/api/v1/events'] as $route) {
            $response = $this->call('POST', $route, [], [], [], [
                'CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json',
            ], str_repeat('x', 4097));
            $this->checkNoStore($response, 413);
        }
    }

    public function test_sec002_unauthorized_receipts_cover_all_five_routes(): void
    {
        foreach (['/api/v1/telemetry', '/api/v1/events'] as $route) {
            $this->checkNoStore($this->postJson($route, []), 401);
        }
        foreach (['state', 'history', 'health'] as $type) {
            $this->checkNoStore($this->getJson('/api/v1/device/'.$type), 401);
        }
    }

    public function test_sec002_disabled_device_receipt_is_never_cacheable(): void
    {
        $this->fakeAuth(false);
        $this->checkNoStore($this->withToken(self::TOKEN)
            ->getJson('/api/v1/device/health'), 403);
    }

    public function test_tel001_created_receipt_is_never_cacheable(): void
    {
        $this->fakeAuth();
        $mock = Mockery::mock(TelemetryIngestService::class);
        $mock->shouldReceive('ingest')->once()->andReturn([
            'status' => TelemetryIngestService::CREATED, 'sample_id' => 122,
        ]);
        $this->app->instance(TelemetryIngestService::class, $mock);
        $this->checkNoStore($this->withToken(self::TOKEN)
            ->postJson('/api/v1/telemetry', $this->telemetry()), 201);
    }

    public function test_net002_replay_duplicate_and_conflict_are_never_cacheable(): void
    {
        $this->fakeAuth();
        $mock = Mockery::mock(EventIngestService::class);
        $mock->shouldReceive('ingest')->twice()->andReturnValues([
            ['status' => 200, 'body' => ['result' => 'identical_event_duplicate']],
            ['status' => 409, 'body' => ['error' => 'conflicting_event_duplicate']],
        ]);
        $this->app->instance(EventIngestService::class, $mock);
        $this->checkNoStore($this->withToken(self::TOKEN)
            ->postJson('/api/v1/events', $this->event()), 200);
        $this->checkNoStore($this->withToken(self::TOKEN)
            ->postJson('/api/v1/events', $this->event()), 409);
    }

    public function test_ui002_authenticated_read_path_never_caches_state_history_health(): void
    {
        $this->fakeAuth();
        $mock = Mockery::mock(DeviceReadService::class);
        $mock->shouldReceive('state')->once()->andReturn(['device_id'=>'b12-device','state'=>null]);
        $mock->shouldReceive('history')->once()->andReturn(['device_id'=>'b12-device','items'=>[],'next_cursor'=>null]);
        $mock->shouldReceive('health')->once()->andReturn(['device_id'=>'b12-device','seen'=>false]);
        $this->app->instance(DeviceReadService::class, $mock);
        foreach (['state','history','health'] as $type) {
            $this->checkNoStore($this->withToken(self::TOKEN)
                ->getJson('/api/v1/device/'.$type), 200);
        }
    }

    public function test_sys003_unavailable_auth_receipt_preserves_retry_and_no_store(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->once()->with(self::TOKEN)
            ->andThrow(new QueryException('mysql', 'SELECT synthetic-only', [],
                new \PDOException('synthetic outage', 2002)));
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $response = $this->withToken(self::TOKEN)->getJson('/api/v1/device/state');
        $this->checkNoStore($response, 503);
        $response->assertHeader('Retry-After', '5');
        $this->assertStringNotContainsString('SELECT', (string) $response->getContent());
    }
}
