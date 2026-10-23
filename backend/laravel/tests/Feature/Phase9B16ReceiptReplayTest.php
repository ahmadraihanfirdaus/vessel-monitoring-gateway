<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceTokenAuthenticator;
use App\Services\EventIngestService;
use App\Services\TelemetryIngestService;
use Mockery;
use Tests\TestCase;

/** DB-free actual Laravel route receipts. C99 ACK policy tested separately; no TLS is implied. */
class Phase9B16ReceiptReplayTest extends TestCase
{
    private const TOKEN = 'b16-fixture-bearer-1234567890123456789012345';

    private function wire(string $variable, int $i): string
    {
        $path = getenv($variable);
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $lines = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertIsArray($lines);
        $this->assertCount($variable === 'VG_B14_WIRE_JSONL' ? 2 : 4, $lines);
        return $lines[$i];
    }

    private function auth(int $times = 1, string $id = 'b14-demo-device'): void
    {
        $device = new Device();
        $device->device_id = $id;
        $device->enabled = true;
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->times($times)->with(self::TOKEN)->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function postWire(string $route, string $wire, bool $bearer = true)
    {
        $headers = ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'];
        if ($bearer) {
            $headers['HTTP_AUTHORIZATION'] = 'Bearer '.self::TOKEN;
        }
        return $this->call('POST', $route, [], [], [], $headers, $wire);
    }

    public function test_tel003_created_then_identical_replay_is_successful(): void
    {
        $this->auth(2);
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->twice()->andReturnValues([
            ['status' => TelemetryIngestService::CREATED, 'sample_id' => 16],
            ['status' => TelemetryIngestService::IDENTICAL, 'sample_id' => 16],
        ]);
        $this->app->instance(TelemetryIngestService::class, $service);
        $raw = $this->wire('VG_B14_WIRE_JSONL', 0);
        $this->postWire('/api/v1/telemetry', $raw)->assertCreated()->assertJson(['result' => 'created']);
        $this->postWire('/api/v1/telemetry', $raw)->assertOk()->assertJson(['result' => 'identical_duplicate']);
    }

    public function test_tel003_conflict_is_not_ack_receipt(): void
    {
        $this->auth();
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->once()->andReturn([
            'status' => TelemetryIngestService::CONFLICTING, 'sample_id' => 16,
        ]);
        $this->app->instance(TelemetryIngestService::class, $service);
        $this->postWire('/api/v1/telemetry', $this->wire('VG_B14_WIRE_JSONL', 0))
            ->assertStatus(409)->assertJson(['error' => 'conflicting_duplicate']);
    }

    public function test_net002_event_created_then_identical_replay(): void
    {
        $this->auth(2, 'b15-demo-device');
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldReceive('ingest')->twice()->andReturnValues([
            ['status' => 201, 'body' => ['result' => 'event_persisted']],
            ['status' => 200, 'body' => ['result' => 'identical_event_duplicate']],
        ]);
        $this->app->instance(EventIngestService::class, $service);
        $raw = $this->wire('VG_B15_EVENT_JSONL', 0);
        $this->postWire('/api/v1/events', $raw)->assertCreated()->assertJson(['result' => 'event_persisted']);
        $this->postWire('/api/v1/events', $raw)->assertOk()->assertJson(['result' => 'identical_event_duplicate']);
    }

    public function test_net002_event_conflict_is_409(): void
    {
        $this->auth(id: 'b15-demo-device');
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldReceive('ingest')->once()->andReturn([
            'status' => 409, 'body' => ['error' => 'conflicting_event_duplicate'],
        ]);
        $this->app->instance(EventIngestService::class, $service);
        $this->postWire('/api/v1/events', $this->wire('VG_B15_EVENT_JSONL', 0))
            ->assertStatus(409)->assertJson(['error' => 'conflicting_event_duplicate']);
    }

    public function test_sec002_missing_auth_denies_telemetry_without_lookup(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->postWire('/api/v1/telemetry', $this->wire('VG_B14_WIRE_JSONL', 0), false)->assertUnauthorized();
    }

    public function test_sec002_missing_auth_denies_events_without_lookup(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->postWire('/api/v1/events', $this->wire('VG_B15_EVENT_JSONL', 0), false)->assertUnauthorized();
    }

    public function test_api001_cross_device_telemetry_denied_before_ingest(): void
    {
        $this->auth(id: 'other-device');
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldNotReceive('ingest');
        $this->app->instance(TelemetryIngestService::class, $service);
        $this->postWire('/api/v1/telemetry', $this->wire('VG_B14_WIRE_JSONL', 0))->assertForbidden();
    }

    public function test_api001_cross_device_events_denied_before_ingest(): void
    {
        $this->auth(id: 'other-device');
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldNotReceive('ingest');
        $this->app->instance(EventIngestService::class, $service);
        $this->postWire('/api/v1/events', $this->wire('VG_B15_EVENT_JSONL', 0))->assertForbidden();
    }
}
