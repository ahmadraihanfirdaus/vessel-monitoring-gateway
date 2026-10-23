<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Services\DeviceTokenAuthenticator;
use App\Services\EventIngestService;
use Mockery;
use Tests\TestCase;

/** Actual C99 journal events cross real Laravel route/validation; mocks block database access. */
class Phase9B15JournalWireHttpTest extends TestCase
{
    private const TOKEN = 'b15-fixture-bearer-1234567890123456789012345';

    private function raw(int $i): string
    {
        $path = getenv('VG_B15_EVENT_JSONL');
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $lines = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertIsArray($lines);
        $this->assertCount(4, $lines);
        return $lines[$i];
    }

    private function auth(string $id = 'b15-demo-device', int $times = 1): void
    {
        $device = new Device();
        $device->device_id = $id;
        $device->enabled = true;
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldReceive('resolve')->times($times)->with(self::TOKEN)->andReturn($device);
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
    }

    private function eventService(array $results, ?\Closure $match = null): void
    {
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldReceive('ingest')->times(count($results))
            ->withArgs($match ?? static fn (Device $d, array $p): bool =>
                $d->device_id === 'b15-demo-device' && $p['device_id'] === $d->device_id)
            ->andReturnValues($results);
        $this->app->instance(EventIngestService::class, $service);
    }

    private function postRaw(string $wire, bool $authorized = true)
    {
        $headers = ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'];
        if ($authorized) {
            $headers['HTTP_AUTHORIZATION'] = 'Bearer '.self::TOKEN;
        }
        return $this->call('POST', '/api/v1/events', [], [], [], $headers, $wire);
    }

    public function test_alm001_raised_journal_event_reaches_laravel(): void
    {
        $this->auth();
        $this->eventService([['status' => 201, 'body' => ['result' => 'event_persisted']]],
            static fn (Device $d, array $p): bool => $d->device_id === 'b15-demo-device'
                && (string) $p['event_id'] === '1' && $p['event_type'] === 'alarm_raised'
                && (string) $p['linked_alarm_id'] === '7'
                && (string) $p['occurred_at_ms'] === '100');
        $response = $this->postRaw($this->raw(0));
        $response->assertCreated()->assertJson(['result' => 'event_persisted']);
        $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
    }

    public function test_alm001_ack_event_does_not_clear_alarm_by_http_convention(): void
    {
        $this->auth();
        $this->eventService([['status' => 201, 'body' => ['result' => 'event_persisted']]],
            static fn (Device $d, array $p): bool => $p['event_type'] === 'alarm_ack'
                && (string) $p['linked_alarm_id'] === '7');
        $this->postRaw($this->raw(1))->assertCreated()->assertDontSee('alarm_cleared');
    }

    public function test_alm001_bench_test_clear_event_preserves_provenance(): void
    {
        $this->auth();
        $this->eventService([['status' => 201, 'body' => ['result' => 'event_persisted']]],
            static fn (Device $d, array $p): bool => $p['event_type'] === 'alarm_cleared'
                && $p['source_mode'] === 'bench_test' && (string) $p['event_id'] === '3');
        $this->postRaw($this->raw(2))->assertCreated();
    }

    public function test_net002_exact_journal_replay_maps_to_duplicate_receipt(): void
    {
        $this->auth(times: 2);
        $this->eventService([
            ['status' => 201, 'body' => ['result' => 'event_persisted']],
            ['status' => 200, 'body' => ['result' => 'identical_event_duplicate']],
        ]);
        $wire = $this->raw(0);
        $this->postRaw($wire)->assertCreated();
        $this->postRaw($wire)->assertOk()->assertJson(['result' => 'identical_event_duplicate']);
    }

    public function test_tel003_conflicting_event_receipt_is_409(): void
    {
        $this->auth(times: 2);
        $this->eventService([
            ['status' => 201, 'body' => ['result' => 'event_persisted']],
            ['status' => 409, 'body' => ['error' => 'conflicting_event_duplicate']],
        ]);
        $this->postRaw($this->raw(0))->assertCreated();
        $mutated = str_replace('"linked_alarm_id":7', '"linked_alarm_id":8', $this->raw(0));
        $this->assertNotSame($this->raw(0), $mutated);
        $this->postRaw($mutated)->assertStatus(409)->assertJson(['error' => 'conflicting_event_duplicate']);
    }

    public function test_sec002_no_bearer_rejected_before_token_lookup(): void
    {
        $auth = Mockery::mock(DeviceTokenAuthenticator::class);
        $auth->shouldNotReceive('resolve');
        $this->app->instance(DeviceTokenAuthenticator::class, $auth);
        $this->postRaw($this->raw(0), false)->assertUnauthorized()
            ->assertJson(['error' => 'invalid_device_authentication']);
    }

    public function test_api001_device_identity_mismatch_is_403_before_service(): void
    {
        $this->auth('other-device');
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldNotReceive('ingest');
        $this->app->instance(EventIngestService::class, $service);
        $this->postRaw($this->raw(0))->assertForbidden();
    }

    public function test_api001_unsupported_journal_recovery_event_is_422(): void
    {
        $this->auth();
        $service = Mockery::mock(EventIngestService::class);
        $service->shouldNotReceive('ingest');
        $this->app->instance(EventIngestService::class, $service);
        $invalid = str_replace('"event_type":"fault"', '"event_type":"recovery"', $this->raw(3));
        $this->assertNotSame($this->raw(3), $invalid);
        $this->postRaw($invalid)->assertUnprocessable();
    }
}
