<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceEventReadService;
use App\Services\DeviceTokenAuthenticator;
use Illuminate\Database\QueryException;
use Mockery;
use Tests\TestCase;

/** Failure injection supplements the real MariaDB tests; it is not a DB outage proof. */
class DeviceEventBoundaryTest extends TestCase
{
    private function authenticated(): string
    {
        $bearer = bin2hex(random_bytes(32));
        $device = new Device();
        $device->device_id = 'event-boundary';
        $device->enabled = true;
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->once()->with($bearer)->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);

        return $bearer;
    }

    public function test_event_connection_failure_returns_sanitized_uncacheable_retry(): void
    {
        $bearer = $this->authenticated();
        $service = Mockery::mock(DeviceEventReadService::class);
        $service->shouldReceive('history')->once()->andThrow(new QueryException(
            'mysql', 'SELECT synthetic_outage_marker', [], new \PDOException('synthetic outage detail', 2002)
        ));
        $this->app->instance(DeviceEventReadService::class, $service);
        $response = $this->withToken($bearer)->getJson('/api/v1/device/events')->assertStatus(503)
            ->assertExactJson(['error' => 'backend_temporarily_unavailable'])->assertHeader('Retry-After', '5');
        $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
        $this->assertStringContainsString('Authorization', (string) $response->headers->get('Vary'));
        $response->assertDontSee('synthetic_outage_marker')->assertDontSee('synthetic outage detail');
        $this->assertStringNotContainsString($bearer, $response->getContent());
    }

    public function test_programming_error_is_not_disguised_as_transient_outage(): void
    {
        $bearer = $this->authenticated();
        $service = Mockery::mock(DeviceEventReadService::class);
        $service->shouldReceive('history')->once()->andThrow(new QueryException(
            'mysql', 'SELECT synthetic_invalid_column', [], new \PDOException('synthetic query defect', 1054)
        ));
        $this->app->instance(DeviceEventReadService::class, $service);
        $this->withToken($bearer)->getJson('/api/v1/device/events')->assertStatus(500);
    }

    public function test_authentication_failure_precedes_query_validation_and_service(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $service = Mockery::mock(DeviceEventReadService::class);
        $service->shouldNotReceive('history');
        $this->app->instance(DeviceEventReadService::class, $service);
        $this->getJson('/api/v1/device/events?limit=invalid&cursor=invalid')
            ->assertUnauthorized()->assertJsonPath('error', 'invalid_device_authentication');
    }
}
