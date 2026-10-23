<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceReadService;
use App\Services\DeviceTokenAuthenticator;
use Illuminate\Pagination\Cursor;
use Mockery;
use Tests\TestCase;

/** Real Laravel route and middleware, mocked service/token resolver, zero DB. */
class Phase9B13CursorContractTest extends TestCase
{
    private const TOKEN = 'b13-fixture-bearer-1234567890-12345678901234567890';

    private function authenticated(): void
    {
        $device = new Device();
        $device->device_id = 'b13-fixture-device';
        $device->enabled = true;
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->with(self::TOKEN)->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function rejectCursor(string $cursor): void
    {
        $this->authenticated();
        $service = Mockery::mock(DeviceReadService::class);
        $service->shouldNotReceive('history');
        $this->app->instance(DeviceReadService::class, $service);
        $response = $this->withToken(self::TOKEN)->getJson(
            '/api/v1/device/history?cursor='.urlencode($cursor)
        );
        $response->assertUnprocessable()
            ->assertJsonPath('errors.cursor.0', 'The cursor field is invalid.');
        $this->assertStringContainsString('no-store', $response->headers->get('Cache-Control'));
    }

    public function test_ui002_missing_received_at_does_not_reach_query_service(): void
    {
        $this->rejectCursor((new Cursor(['id' => 42]))->encode());
    }

    public function test_ui002_injected_parameter_does_not_reach_query_service(): void
    {
        $this->rejectCursor((new Cursor([
            'received_at' => '2026-10-23 10:00:00', 'id' => 42, 'ignored' => 'x',
        ]))->encode());
    }

    public function test_ui002_id_zero_is_rejected(): void
    {
        $this->rejectCursor((new Cursor(['received_at' => '2026-10-23 10:00:00', 'id' => 0]))->encode());
    }

    public function test_ui002_invalid_date_is_rejected(): void
    {
        $this->rejectCursor((new Cursor(['received_at' => '2026-02-30 10:00:00', 'id' => 42]))->encode());
    }

    public function test_api001_bad_id_type_is_rejected(): void
    {
        $this->rejectCursor((new Cursor(['received_at' => '2026-10-23 10:00:00', 'id' => ['42']]))->encode());
    }

    public function test_sec002_missing_auth_does_not_expose_cursor_validation(): void
    {
        $cursor = (new Cursor(['id' => 42]))->encode();
        $this->getJson('/api/v1/device/history?cursor='.urlencode($cursor))
            ->assertUnauthorized()->assertJsonPath('error', 'invalid_device_authentication');
    }

    public function test_ui002_full_cursor_is_forwarded_byte_identically(): void
    {
        $this->authenticated();
        $cursor = (new Cursor(['received_at' => '2026-10-23 10:00:00', 'id' => 42]))->encode();
        $service = Mockery::mock(DeviceReadService::class);
        $service->shouldReceive('history')->once()->withArgs(
            static fn (Device $device, int $limit, ?string $value): bool =>
                $device->device_id === 'b13-fixture-device' && $limit === 4 && $value === $cursor
        )->andReturn(['device_id' => 'b13-fixture-device', 'items' => [], 'next_cursor' => null]);
        $this->app->instance(DeviceReadService::class, $service);
        $this->withToken(self::TOKEN)->getJson(
            '/api/v1/device/history?limit=4&cursor='.urlencode($cursor)
        )->assertOk()->assertJsonPath('device_id', 'b13-fixture-device');
    }

    public function test_ui002_full_cursor_preserves_uint64_id_as_decimal(): void
    {
        $this->authenticated();
        $cursor = (new Cursor([
            'received_at' => '2026-10-23 10:00:00', 'id' => '18446744073709551615',
        ]))->encode();
        $service = Mockery::mock(DeviceReadService::class);
        $service->shouldReceive('history')->once()->withArgs(
            static fn (Device $device, int $limit, ?string $value): bool =>
                $device->device_id === 'b13-fixture-device' && $limit === 50 && $value === $cursor
        )->andReturn(['device_id' => 'b13-fixture-device', 'items' => [], 'next_cursor' => null]);
        $this->app->instance(DeviceReadService::class, $service);
        $this->withToken(self::TOKEN)->getJson(
            '/api/v1/device/history?cursor='.urlencode($cursor)
        )->assertOk()->assertJsonPath('device_id', 'b13-fixture-device');
    }
}
