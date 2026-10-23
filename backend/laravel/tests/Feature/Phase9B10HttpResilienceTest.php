<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceReadService;
use App\Services\DeviceTokenAuthenticator;
use Illuminate\Pagination\Cursor;
use Mockery;
use RuntimeException;
use Tests\TestCase;

/** B10: Laravel request dispatch with strict service doubles; no DB, migrations or network. */
class Phase9B10HttpResilienceTest extends TestCase
{
    private const TOKEN = 'b10-fixture-bearer-token-1234567890-1234567890';

    private function tokenRejected(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->once()->with(self::TOKEN)->andReturn(null);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function authenticated(): void
    {
        $device = new Device();
        $device->device_id = 'b10-device';
        $device->enabled = true;
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->with(self::TOKEN)->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function postRaw(string $type, string $payload = '{}')
    {
        return $this->call('POST', '/api/v1/events', [], [], [], [
            'HTTP_AUTHORIZATION' => 'Bearer '.self::TOKEN,
            'CONTENT_TYPE' => $type,
            'HTTP_ACCEPT' => 'application/json',
        ], $payload);
    }

    public function test_api001_jsonp_and_text_json_are_rejected_before_auth(): void
    {
        foreach (['application/jsonp', 'text/json', 'application/x-json'] as $type) {
            $this->postRaw($type)->assertStatus(415)
                ->assertJson(['error' => 'unsupported_telemetry_media_type']);
        }
    }

    public function test_api001_structured_json_suffix_passes_media_gate(): void
    {
        $this->tokenRejected();
        $this->postRaw('application/vnd.vessel-gateway+json')->assertUnauthorized()
            ->assertJson(['error' => 'invalid_device_authentication']);
    }

    public function test_api001_json_charset_passes_media_gate(): void
    {
        $this->tokenRejected();
        $this->postRaw('application/json; charset=utf-8')->assertUnauthorized()
            ->assertJson(['error' => 'invalid_device_authentication']);
    }

    public function test_api001_overlong_body_still_rejected_before_mime_check(): void
    {
        $this->postRaw('application/jsonp', str_repeat('a', 4097))
            ->assertStatus(413)->assertJson(['error' => 'telemetry_payload_too_large']);
    }

    public function test_sec002_short_bearer_never_reaches_device_service(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->withToken('short')->getJson('/api/v1/device/history')
            ->assertUnauthorized();
    }

    public function test_ui002_malformed_history_cursor_is_rejected_before_read_service(): void
    {
        $this->authenticated();
        $read = Mockery::mock(DeviceReadService::class);
        $read->shouldNotReceive('history');
        $this->app->instance(DeviceReadService::class, $read);
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/history?cursor=not-a-cursor')
            ->assertUnprocessable()->assertJsonPath('errors.cursor.0', 'The cursor field is invalid.');
    }

    public function test_ui002_valid_cursor_is_forwarded_without_db_access(): void
    {
        $this->authenticated();
        $cursor = (new Cursor(['id' => 42]))->encode();
        $read = Mockery::mock(DeviceReadService::class);
        $read->shouldReceive('history')->once()->withArgs(
            static fn (Device $device, int $limit, ?string $value): bool =>
                $device->device_id === 'b10-device' && $limit === 8 && $value === $cursor
        )->andReturn(['device_id' => 'b10-device', 'items' => [], 'next_cursor' => null]);
        $this->app->instance(DeviceReadService::class, $read);
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/history?limit=8&cursor='.urlencode($cursor))
            ->assertOk()->assertJsonPath('device_id', 'b10-device');
    }

    public function test_sys003_read_service_failure_is_not_misreported_as_bad_cursor(): void
    {
        $this->authenticated();
        $read = Mockery::mock(DeviceReadService::class);
        $read->shouldReceive('history')->once()->andThrow(new RuntimeException('B10 synthetic outage'));
        $this->app->instance(DeviceReadService::class, $read);
        // A server-side failure must never appear as a client cursor error (422).
        $this->withToken(self::TOKEN)->getJson('/api/v1/device/history')->assertStatus(500);
    }
}
