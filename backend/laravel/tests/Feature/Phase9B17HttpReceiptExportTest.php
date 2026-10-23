<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceTokenAuthenticator;
use App\Services\EventIngestService;
use App\Services\TelemetryIngestService;
use Illuminate\Database\QueryException;
use Mockery;
use Tests\TestCase;

/** Source of B17 receipts: actual in-process Laravel HTTP route, DB-free doubles. */
class Phase9B17HttpReceiptExportTest extends TestCase
{
    private const TOKEN = 'b17-host-fixture-bearer-token-1234567890123456789';

    private function fixture(string $key): string
    {
        $name = $key === 'telemetry' ? 'VG_B14_WIRE_JSONL' : 'VG_B15_EVENT_JSONL';
        $file = getenv($name);
        $this->assertIsString($file);
        $this->assertFileExists($file);
        $lines = file($file, FILE_IGNORE_NEW_LINES);
        $this->assertIsArray($lines);
        $this->assertCount($key === 'telemetry' ? 2 : 4, $lines);
        return $lines[0];
    }

    private function auth(string $deviceId): void
    {
        $device = new Device();
        $device->device_id = $deviceId;
        $device->enabled = true;
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->once()->with(self::TOKEN)->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function b17Request(string $path, string $wire, bool $bearer = true, string $contentType = 'application/json')
    {
        $server = ['CONTENT_TYPE' => $contentType, 'HTTP_ACCEPT' => 'application/json'];
        if ($bearer) {
            $server['HTTP_AUTHORIZATION'] = 'Bearer '.self::TOKEN;
        }
        return $this->call('POST', $path, [], [], [], $server, $wire);
    }

    private function mockTelemetry(string $status): void
    {
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldReceive('ingest')->once()->andReturn(['status' => $status, 'sample_id' => 17]);
        $this->app->instance(TelemetryIngestService::class, $service);
    }

    private function mockEventSequence(): void
    {
        // EventIngestController receives its service in the constructor. A single
        // mock survives repeated requests through the same cached route controller.
        $index = 0;
        $outage = new QueryException('mysql', 'SELECT fixture', [],
            new \PDOException('synthetic connection refused', 2002));
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldReceive('ingest')->times(4)
            ->andReturnUsing(static function (Device $device, array $payload) use (&$index, $outage): array {
                if ($device->device_id !== 'b15-demo-device'
                    || (string) $payload['device_id'] !== $device->device_id) {
                    throw new \LogicException('B17 event fixture identity drift');
                }
                return match (++$index) {
                    1 => ['status' => 201, 'body' => ['result' => 'event_persisted']],
                    2 => ['status' => 200, 'body' => ['result' => 'identical_event_duplicate']],
                    3 => ['status' => 409, 'body' => ['error' => 'conflicting_event_duplicate']],
                    4 => throw $outage,
                    default => throw new \LogicException('B17 unexpected event request'),
                };
            });
        $this->app->instance(EventIngestService::class, $service);
    }

    public function test_tst001_export_eight_real_http_responses_without_database(): void
    {
        $file = getenv('VG_B17_RECEIPTS_JSONL');
        $this->assertIsString($file);
        $this->assertNotSame('', $file);
        $this->assertFileDoesNotExist($file);
        $tele = $this->fixture('telemetry');
        $event = $this->fixture('event');
        $records = [];
        $put = function (string $name, string $route, $response, int $expected) use (&$records): void {
            $response->assertStatus($expected);
            $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
            $this->assertIsString($response->getContent());
            $records[] = [
                'case' => $name,
                'route' => $route,
                'status' => $response->getStatusCode(),
                'body_json' => $response->getContent(),
                'origin_verified' => false,
            ];
        };
        $routeT = '/api/v1/telemetry';
        $routeE = '/api/v1/events';
        $this->auth('b14-demo-device');
        $this->mockTelemetry(TelemetryIngestService::CREATED);
        $put('telemetry_created', $routeT, $this->b17Request($routeT, $tele), 201);
        $this->auth('b14-demo-device');
        $this->mockTelemetry(TelemetryIngestService::IDENTICAL);
        $put('telemetry_identical', $routeT, $this->b17Request($routeT, $tele), 200);
        $this->auth('b14-demo-device');
        $this->mockTelemetry(TelemetryIngestService::CONFLICTING);
        $put('telemetry_conflict', $routeT, $this->b17Request($routeT, $tele), 409);
        $this->auth('b15-demo-device');
        $this->mockEventSequence();
        $put('event_created', $routeE, $this->b17Request($routeE, $event), 201);
        $this->auth('b15-demo-device');
        $put('event_identical', $routeE, $this->b17Request($routeE, $event), 200);
        $this->auth('b15-demo-device');
        $put('event_conflict', $routeE, $this->b17Request($routeE, $event), 409);
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $put('unauthorized', $routeT, $this->b17Request($routeT, $tele, false), 401);
        $this->auth('b15-demo-device');
        $put('dependency_unavailable', $routeE, $this->b17Request($routeE, $event), 503);
        $this->assertCount(8, $records);
        $jsonl = implode("\n", array_map(fn (array $v): string => json_encode($v, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES), $records))."\n";
        $this->assertLessThan(8192, strlen($jsonl));
        $this->assertSame(strlen($jsonl), file_put_contents($file, $jsonl, LOCK_EX));
    }

    public function test_api001_invalid_mime_rejected_before_auth_lookup(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->b17Request('/api/v1/telemetry', '{}', false, 'application/jsonp')->assertStatus(415);
    }

    public function test_sec002_no_token_rejected_without_lookup(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->b17Request('/api/v1/events', $this->fixture('event'), false)->assertUnauthorized();
    }

    public function test_sec002_unknown_token_is_unauthorized(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->once()->with(self::TOKEN)->andReturn(null);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->b17Request('/api/v1/telemetry', '{}')->assertUnauthorized();
    }

    public function test_api001_telemetry_wrong_device_is_forbidden(): void
    {
        $this->auth('different-device');
        $service = Mockery::mock(TelemetryIngestService::class);
        $service->shouldNotReceive('ingest');
        $this->app->instance(TelemetryIngestService::class, $service);
        $this->b17Request('/api/v1/telemetry', $this->fixture('telemetry'))->assertForbidden();
    }

    public function test_api001_event_wrong_device_is_forbidden(): void
    {
        $this->auth('different-device');
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldNotReceive('ingest');
        $this->app->instance(EventIngestService::class, $service);
        $this->b17Request('/api/v1/events', $this->fixture('event'))->assertForbidden();
    }

    public function test_sys003_cache_control_present_on_auth_denial(): void
    {
        $response = $this->b17Request('/api/v1/telemetry', $this->fixture('telemetry'), false);
        $response->assertUnauthorized();
        // Laravel can legally append 'private'; require the exact no-store directive.
        $directives = array_map('trim', explode(',', strtolower((string) $response->headers->get('Cache-Control'))));
        $this->assertContains('no-store', $directives);
    }

    public function test_tst001_no_real_database_dependency_in_fixture(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->b17Request('/api/v1/events', $this->fixture('event'), false)
            ->assertUnauthorized()->assertJson(['error' => 'invalid_device_authentication']);
    }
}
