<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Str;
use Tests\MySqlTestCase;

class EventIngestTest extends MySqlTestCase
{
    use DatabaseTransactions;

    public function test_distinct_event_is_persisted_once(): void
    {
        [$device, $bearer] = $this->createDevice();

        $this->withToken($bearer)
            ->postJson('/api/v1/events', $this->payload($device->device_id))
            ->assertCreated()
            ->assertJson(['result' => 'event_persisted']);

        $this->assertDatabaseCount('monitoring_events', 1);
    }

    public function test_identical_duplicate_is_idempotent(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);

        $this->withToken($bearer)
            ->postJson('/api/v1/events', $payload)
            ->assertCreated();

        $this->withToken($bearer)
            ->postJson('/api/v1/events', $payload)
            ->assertOk()
            ->assertJson(['result' => 'identical_event_duplicate']);

        $this->assertDatabaseCount('monitoring_events', 1);
    }

    public function test_conflicting_duplicate_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);

        $this->withToken($bearer)
            ->postJson('/api/v1/events', $payload)
            ->assertCreated();

        $payload['event_type'] = 'fault';

        $this->withToken($bearer)
            ->postJson('/api/v1/events', $payload)
            ->assertConflict()
            ->assertJson(['error' => 'conflicting_event_duplicate']);

        $this->assertDatabaseCount('monitoring_events', 1);
    }

    public function test_auth_disabled_and_identity_mismatch_are_rejected(): void
    {
        $deviceId = 'rt-event-auth';

        $this->postJson('/api/v1/events', $this->payload($deviceId))
            ->assertUnauthorized();

        $this->withToken(Str::random(64))
            ->postJson('/api/v1/events', $this->payload($deviceId))
            ->assertUnauthorized();

        [$disabled, $disabledBearer] = $this->createDevice(false);

        $this->withToken($disabledBearer)
            ->postJson('/api/v1/events', $this->payload($disabled->device_id))
            ->assertForbidden();

        [$enabled, $enabledBearer] = $this->createDevice();

        $this->withToken($enabledBearer)
            ->postJson('/api/v1/events', $this->payload('different-device'))
            ->assertForbidden();
    }

    public function test_invalid_and_physical_source_are_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();

        $invalid = $this->payload($device->device_id);
        $invalid['source_id'] = 0;

        $this->withToken($bearer)
            ->postJson('/api/v1/events', $invalid)
            ->assertUnprocessable();

        $physical = $this->payload($device->device_id);
        $physical['source_mode'] = 'physical';

        $this->withToken($bearer)
            ->postJson('/api/v1/events', $physical)
            ->assertUnprocessable();

        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_payload_over_4096_bytes_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $raw = json_encode(
            ['padding' => str_repeat('x', 5000)],
            JSON_THROW_ON_ERROR
        );

        $this->call(
            'POST',
            '/api/v1/events',
            [],
            [],
            [],
            [
                'HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                'CONTENT_TYPE' => 'application/json',
                'HTTP_ACCEPT' => 'application/json',
            ],
            $raw
        )->assertStatus(413);

        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_uint64_max_event_identity_is_preserved(): void
    {
        [$device, $bearer] = $this->createDevice();
        $raw = json_encode(
            $this->payload($device->device_id),
            JSON_THROW_ON_ERROR
        );

        $raw = str_replace(
            '"event_id":42',
            '"event_id":18446744073709551615',
            $raw
        );

        $this->call(
            'POST',
            '/api/v1/events',
            [],
            [],
            [],
            [
                'HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                'CONTENT_TYPE' => 'application/json',
                'HTTP_ACCEPT' => 'application/json',
            ],
            $raw
        )->assertCreated();

        $this->assertDatabaseHas('monitoring_events', [
            'device_id' => $device->device_id,
            'event_id' => '18446744073709551615',
        ]);
    }

    public function test_linked_alarm_zero_is_accepted_for_fault_event(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);
        $payload['linked_alarm_id'] = 0;
        $payload['event_type'] = 'fault';

        $this->withToken($bearer)
            ->postJson('/api/v1/events', $payload)
            ->assertCreated();
    }

    public function test_duplicate_raw_event_identity_key_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $raw = json_encode(
            $this->payload($device->device_id),
            JSON_THROW_ON_ERROR
        );

        $raw = str_replace(
            '"event_id":42',
            '"event_id":42,"event_id":43',
            $raw
        );

        $this->call(
            'POST',
            '/api/v1/events',
            [],
            [],
            [],
            [
                'HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                'CONTENT_TYPE' => 'application/json',
                'HTTP_ACCEPT' => 'application/json',
            ],
            $raw
        )->assertUnprocessable();

        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_unicode_escaped_duplicate_event_fields_are_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $base = json_encode(
            $this->payload($device->device_id),
            JSON_THROW_ON_ERROR
        );

        // Both pairs have the same decoded JSON property name.
        // The second spelling must not overwrite the first silently.
        $cases = [
            str_replace(
                '"event_id":42',
                '"event_id":42,"\\u0065vent_id":43',
                $base
            ),
            str_replace(
                '"source_mode":"simulation"',
                '"source_mode":"simulation","source_\\u006dode":"bench_test"',
                $base
            ),
        ];

        foreach ($cases as $raw) {
            $this->call(
                'POST',
                '/api/v1/events',
                [],
                [],
                [],
                [
                    'HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                    'CONTENT_TYPE' => 'application/json',
                    'HTTP_ACCEPT' => 'application/json',
                ],
                $raw
            )->assertUnprocessable();
        }

        $this->assertDatabaseCount('monitoring_events', 0);
    }

    private function createDevice(bool $enabled = true): array
    {
        $bearer = Str::random(64);

        $device = Device::query()->create([
            'device_id' => 'event-'.Str::lower(Str::random(20)),
            'token_digest' => hash('sha256', $bearer),
            'enabled' => $enabled,
        ]);

        return [$device, $bearer];
    }

    private function payload(string $deviceId): array
    {
        return [
            'schema_version' => '1.0',
            'device_id' => $deviceId,
            'boot_id' => 'boot-event-001',
            'event_id' => 42,
            'linked_alarm_id' => 7,
            'source_id' => 2,
            'source_mode' => 'simulation',
            'event_type' => 'alarm_raised',
            'occurred_at_ms' => 123456,
        ];
    }
}
