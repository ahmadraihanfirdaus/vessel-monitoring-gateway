<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceTokenAuthenticator;
use App\Services\TelemetryIngestService;
use Mockery;
use Tests\TestCase;

/** Real host C99 JSON bytes enter the actual Laravel middleware/request/controller. No DB. */
class Phase9B14FirmwareWireHttpTest extends TestCase
{
    private const TOKEN = 'b14-host-fixture-token-123456789012345678901234';

    private function raw(int $index): string
    {
        $path = getenv('VG_B14_WIRE_JSONL');
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $lines = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertIsArray($lines);
        $this->assertCount(2, $lines);
        $this->assertLessThanOrEqual(4096, strlen($lines[$index]));
        return $lines[$index];
    }

    private function auth(string $deviceId = 'b14-demo-device', int $times = 1): void
    {
        $device = new Device();
        $device->device_id = $deviceId;
        $device->enabled = true;
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->times($times)->with(self::TOKEN)->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function postRaw(string $raw, bool $authorized = true, string $media = 'application/json')
    {
        $headers = ['CONTENT_TYPE' => $media, 'HTTP_ACCEPT' => 'application/json'];
        if ($authorized) {
            $headers['HTTP_AUTHORIZATION'] = 'Bearer '.self::TOKEN;
        }
        return $this->call('POST', '/api/v1/telemetry', [], [], [], $headers, $raw);
    }

    private function ingestResult(string $result, int $sampleId): array
    {
        return ['status' => $result, 'sample_id' => $sampleId];
    }

    public function test_tel001_c99_json_reaches_laravel_ingest(): void
    {
        $this->auth();
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->once()->withArgs(
            static fn (Device $d, array $p): bool => $d->device_id === 'b14-demo-device'
                && $p['schema_version'] === '1.0'
                && $p['device_id'] === $d->device_id
                && $p['source_mode'] === 'simulation'
                && (string) $p['sequence'] === '42'
        )->andReturn($this->ingestResult(TelemetryIngestService::CREATED, 140));
        $this->app->instance(TelemetryIngestService::class, $service);
        $r = $this->postRaw($this->raw(0));
        $r->assertCreated()->assertJson(['result' => 'created', 'sample_id' => 140]);
        $this->assertStringContainsString('no-store', (string) $r->headers->get('Cache-Control'));
    }

    public function test_tel002_null_and_zero_reach_service_unchanged(): void
    {
        $this->auth();
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->once()->withArgs(
            static fn (Device $d, array $p): bool =>
                $p['channels']['zero_test']['quality'] === 'valid'
                && $p['channels']['zero_test']['value'] == 0
                && $p['channels']['zero_test']['value'] !== null
                && $p['channels']['bilge_level']['quality'] === 'missing'
                && $p['channels']['bilge_level']['value'] === null
        )->andReturn($this->ingestResult(TelemetryIngestService::CREATED, 141));
        $this->app->instance(TelemetryIngestService::class, $service);
        $this->postRaw($this->raw(0))->assertCreated();
    }

    public function test_tel001_uint64_max_round_trips_without_float(): void
    {
        $this->auth();
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->once()->withArgs(
            static fn (Device $d, array $p): bool =>
                (string) $p['sequence'] === '18446744073709551615'
                && (string) $p['uptime_ms'] === '18446744073709551615'
        )->andReturn($this->ingestResult(TelemetryIngestService::CREATED, 142));
        $this->app->instance(TelemetryIngestService::class, $service);
        $this->postRaw($this->raw(1))->assertCreated();
    }

    public function test_net002_replayed_exact_wire_gets_receipt_from_service(): void
    {
        $this->auth(times: 2);
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->twice()->andReturnValues([
            $this->ingestResult(TelemetryIngestService::CREATED, 143),
            $this->ingestResult(TelemetryIngestService::IDENTICAL, 143),
        ]);
        $this->app->instance(TelemetryIngestService::class, $service);
        $wire = $this->raw(0);
        $this->postRaw($wire)->assertCreated();
        $this->postRaw($wire)->assertOk()->assertJson(['result' => 'identical_duplicate']);
    }

    public function test_tel003_conflicting_same_identity_returns_409_receipt(): void
    {
        $this->auth(times: 2);
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->twice()->andReturnValues([
            $this->ingestResult(TelemetryIngestService::CREATED, 144),
            $this->ingestResult(TelemetryIngestService::CONFLICTING, 144),
        ]);
        $this->app->instance(TelemetryIngestService::class, $service);
        $this->postRaw($this->raw(0))->assertCreated();
        // The altered wire has the same sample identity but a changed measurement.
        $changed = str_replace('"value":0', '"value":1', $this->raw(0));
        $this->assertNotSame($this->raw(0), $changed);
        $this->postRaw($changed)->assertStatus(409)->assertJson(['error' => 'conflicting_duplicate']);
    }

    public function test_sec002_unauthenticated_wire_is_rejected_before_db_lookup(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->postRaw($this->raw(0), false)->assertUnauthorized();
    }

    public function test_sec002_other_device_is_denied_before_ingest(): void
    {
        $this->auth(deviceId: 'other-device');
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldNotReceive('ingest');
        $this->app->instance(TelemetryIngestService::class, $service);
        $this->postRaw($this->raw(0))->assertForbidden()
            ->assertJson(['error' => 'device_identity_mismatch']);
    }

    public function test_api001_wrong_media_type_is_rejected_before_token(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->postRaw($this->raw(0), true, 'text/plain')->assertStatus(415);
    }
}
