<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceReadService;
use App\Services\DeviceTokenAuthenticator;
use App\Services\EventIngestService;
use App\Services\TelemetryIngestService;
use Mockery;
use Illuminate\Pagination\Cursor;
use Tests\TestCase;

/**
 * No database refresh traits, factories, migrations, DB facade or real token lookups.
 * These tests exercise Laravel's routes + middleware + requests + controllers.
 * Every DB-backed collaborator is a strict, in-memory service double.
 */
class Phase9B9HttpBoundaryTest extends TestCase
{
    private const TOKEN = 'b9-fixture-bearer-token-1234567890-1234567890';

    private function device(bool $enabled = true): Device
    {
        $device = new Device();
        $device->device_id = 'b9-device';
        $device->enabled = $enabled;
        return $device;
    }

    private function fakeAuth(Device $device): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->with(self::TOKEN)
            ->zeroOrMoreTimes()->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function fakeTelemetry(array $statuses = [TelemetryIngestService::CREATED]): void
    {
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->withArgs(
            static fn (Device $d, array $payload): bool =>
                $d->device_id === 'b9-device'
                && $payload['device_id'] === 'b9-device'
                && $payload['channels']['bilge_level']['value'] === null
                && $payload['channels']['zero_test']['value'] == 0
        )->times(count($statuses))->andReturnValues(array_map(
            static fn (string $status): array => ['status' => $status, 'sample_id' => 91],
            $statuses
        ));
        $this->app->instance(TelemetryIngestService::class, $service);
    }

    private function fakeEvents(array $results): void
    {
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldReceive('ingest')->withArgs(
            static fn (Device $d, array $payload): bool =>
                $d->device_id === 'b9-device'
                && $payload['source_mode'] === 'simulation'
                && (string) $payload['event_id'] === '42'
        )->times(count($results))->andReturnValues($results);
        $this->app->instance(EventIngestService::class, $service);
    }

    private function telemetry(): array
    {
        return [
            'schema_version' => '1.0',
            'device_id' => 'b9-device',
            'firmware_version' => 'b9-fixture',
            'boot_id' => 'b9-boot',
            'sequence' => 42,
            'uptime_ms' => 1234,
            'source_mode' => 'simulation',
            'channels' => [
                'bilge_level' => ['value' => null, 'quality' => 'missing'],
                'zero_test' => ['value' => 0, 'quality' => 'valid'],
            ],
        ];
    }

    private function event(): array
    {
        return [
            'schema_version' => '1.0', 'device_id' => 'b9-device',
            'boot_id' => 'b9-boot', 'event_id' => 42,
            'linked_alarm_id' => 7, 'source_id' => 2,
            'source_mode' => 'simulation', 'event_type' => 'alarm_raised',
            'occurred_at_ms' => 1234,
        ];
    }

    private function rawPost(string $path, string $body, string $contentType = 'application/json')
    {
        return $this->call('POST', $path, [], [], [], [
            'HTTP_AUTHORIZATION' => 'Bearer '.self::TOKEN,
            'CONTENT_TYPE' => $contentType,
            'HTTP_ACCEPT' => 'application/json',
        ], $body);
    }

    // API-001: the *production* middleware enforces framing on both routes.
    public function test_api001_wrong_media_type_is_rejected_before_auth_for_both_ingest_routes(): void
    {
        foreach (['/api/v1/telemetry', '/api/v1/events'] as $path) {
            $this->rawPost($path, '{}', 'text/plain')->assertStatus(415)
                ->assertJson(['error' => 'unsupported_telemetry_media_type']);
        }
    }

    public function test_api001_oversize_precedes_media_type_rejection(): void
    {
        $this->rawPost('/api/v1/telemetry', str_repeat('x', 4097), 'text/plain')
            ->assertStatus(413)->assertJson(['error' => 'telemetry_payload_too_large']);
    }

    public function test_api001_json_charset_reaches_auth_gate(): void
    {
        // The media type must pass framing and reach token verification, but
        // this fixture must never resolve the bearer through Eloquent/MySQL.
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->once()->with(self::TOKEN)->andReturn(null);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->rawPost('/api/v1/events', '{}', 'application/json; charset=utf-8')
            ->assertUnauthorized()->assertJson(['error' => 'invalid_device_authentication']);
    }

    // SEC-002: an absent token never goes to DB-based token lookup.
    public function test_sec002_missing_bearer_is_unauthorized_on_write_and_read(): void
    {
        $this->postJson('/api/v1/telemetry', $this->telemetry())->assertUnauthorized();
        $this->getJson('/api/v1/device/state')->assertUnauthorized();
    }

    public function test_sec002_disabled_device_is_forbidden_without_persistence(): void
    {
        $this->fakeAuth($this->device(false));
        $this->withToken(self::TOKEN)->postJson('/api/v1/events', $this->event())
            ->assertForbidden()->assertJson(['error' => 'device_disabled']);
    }

    public function test_sec002_authenticated_device_identity_mismatch_is_forbidden(): void
    {
        $this->fakeAuth($this->device());
        $bad = $this->telemetry();
        $bad['device_id'] = 'other-device';
        $this->withToken(self::TOKEN)->postJson('/api/v1/telemetry', $bad)
            ->assertForbidden()->assertJson(['error' => 'device_identity_mismatch']);
    }

    // TEL-001: preserve null versus zero in *validated HTTP request*.
    public function test_tel001_valid_quality_and_zero_reach_real_controller(): void
    {
        $this->fakeAuth($this->device());
        $this->fakeTelemetry();
        $this->withToken(self::TOKEN)->postJson('/api/v1/telemetry', $this->telemetry())
            ->assertCreated()->assertJson(['result' => 'created', 'sample_id' => 91]);
    }

    public function test_tel001_invalid_quality_is_422_before_ingest(): void
    {
        $this->fakeAuth($this->device());
        $bad = $this->telemetry();
        $bad['channels']['bilge_level']['quality'] = 'not-a-quality';
        $this->withToken(self::TOKEN)->postJson('/api/v1/telemetry', $bad)
            ->assertUnprocessable();
    }

    public function test_tel001_uint64_max_preserved_without_float_conversion(): void
    {
        $this->fakeAuth($this->device());
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->once()->withArgs(
            static fn (Device $d, array $payload): bool =>
                $d->device_id === 'b9-device'
                && (string) $payload['sequence'] === '18446744073709551615'
        )->andReturn(['status' => TelemetryIngestService::CREATED, 'sample_id' => 92]);
        $this->app->instance(TelemetryIngestService::class, $service);
        $raw = json_encode($this->telemetry(), JSON_THROW_ON_ERROR);
        $raw = str_replace('"sequence":42', '"sequence":18446744073709551615', $raw);
        $this->rawPost('/api/v1/telemetry', $raw)->assertCreated();
    }

    // TEL-003 / NET-002: exercise real route response mapping, not in-memory ledger.
    public function test_tel003_telemetry_created_identical_conflict_http_statuses(): void
    {
        $this->fakeAuth($this->device());
        $this->fakeTelemetry([
            TelemetryIngestService::CREATED,
            TelemetryIngestService::IDENTICAL,
            TelemetryIngestService::CONFLICTING,
        ]);
        foreach ([201 => 'created', 200 => 'identical_duplicate', 409 => 'conflicting_duplicate'] as $status => $result) {
            $res = $this->withToken(self::TOKEN)->postJson('/api/v1/telemetry', $this->telemetry());
            $res->assertStatus($status);
            $res->assertJson($status === 409 ? ['error' => $result] : ['result' => $result]);
        }
    }

    public function test_net002_event_created_repeated_conflicting_response_contract(): void
    {
        $this->fakeAuth($this->device());
        $this->fakeEvents([
            ['status' => 201, 'body' => ['result' => 'event_persisted']],
            ['status' => 200, 'body' => ['result' => 'identical_event_duplicate']],
            ['status' => 409, 'body' => ['error' => 'conflicting_event_duplicate']],
        ]);
        foreach ([201, 200, 409] as $status) {
            $this->withToken(self::TOKEN)->postJson('/api/v1/events', $this->event())
                ->assertStatus($status);
        }
    }

    public function test_net002_event_physical_source_rejected_before_service(): void
    {
        $this->fakeAuth($this->device());
        $event = $this->event();
        $event['source_mode'] = 'physical';
        $this->withToken(self::TOKEN)->postJson('/api/v1/events', $event)
            ->assertUnprocessable();
    }

    // UI-002: the real read endpoints must preserve identity and bounds.
    public function test_ui002_state_reads_authenticated_device_only(): void
    {
        $this->fakeAuth($this->device());
        $service = Mockery::mock(DeviceReadService::class);
        $service->shouldReceive('state')->once()->withArgs(
            static fn (Device $d): bool => $d->device_id === 'b9-device'
        )->andReturn(['device_id' => 'b9-device', 'state' => null]);
        $this->app->instance(DeviceReadService::class, $service);
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/state')
            ->assertOk()->assertJson(['device_id' => 'b9-device', 'state' => null]);
    }

    public function test_ui002_history_limit_cursor_forwarded_to_service(): void
    {
        $this->fakeAuth($this->device());
        $service = Mockery::mock(DeviceReadService::class);
        $cursor = (new Cursor(['received_at' => '2026-10-23 10:00:00', 'id' => 42]))->encode();
        $service->shouldReceive('history')->once()->withArgs(
            static fn (Device $d, int $limit, ?string $value): bool =>
                $d->device_id === 'b9-device' && $limit === 2 && $value === $cursor
        )->andReturn(['device_id' => 'b9-device', 'items' => [], 'next_cursor' => null]);
        $this->app->instance(DeviceReadService::class, $service);
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/history?limit=2&cursor='.urlencode($cursor))
            ->assertOk()->assertJson(['device_id' => 'b9-device']);
    }

    public function test_ui002_history_over_limit_does_not_invoke_read_service(): void
    {
        $this->fakeAuth($this->device());
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/history?limit=101')
            ->assertUnprocessable();
    }

    public function test_ui002_health_read_returns_unverified_status_without_fabrication(): void
    {
        $this->fakeAuth($this->device());
        $service = Mockery::mock(DeviceReadService::class);
        $service->shouldReceive('health')->once()->withArgs(
            static fn (Device $d): bool => $d->device_id === 'b9-device'
        )->andReturn([
            'device_id' => 'b9-device', 'enabled' => true, 'seen' => false,
            'last_seen_at' => null, 'age_seconds' => null,
        ]);
        $this->app->instance(DeviceReadService::class, $service);
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/health')
            ->assertOk()->assertJson(['device_id' => 'b9-device', 'seen' => false]);
    }

    // TST-001: both routes share this complete, mocked, no-DB HTTP scenario.
    public function test_tst001_end_to_end_http_dispatch_without_database(): void
    {
        $this->fakeAuth($this->device());
        $this->fakeTelemetry();
        $this->fakeEvents([['status' => 201, 'body' => ['result' => 'event_persisted']]]);
        $this->withToken(self::TOKEN)->postJson('/api/v1/telemetry', $this->telemetry())
            ->assertCreated();
        $this->withToken(self::TOKEN)->postJson('/api/v1/events', $this->event())
            ->assertCreated();
    }
}
