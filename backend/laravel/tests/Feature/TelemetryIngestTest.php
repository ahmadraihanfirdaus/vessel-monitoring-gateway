<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Str;
use Tests\MySqlTestCase;

class TelemetryIngestTest extends MySqlTestCase
{
    use DatabaseTransactions;

    public function test_distinct_valid_sample_is_persisted_once(): void
    {
        [$device, $bearer] = $this->createDevice();

        $response = $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $this->payload($device->device_id));

        $response->assertCreated()->assertJson([
            'result' => 'created',
        ]);

        $this->assertDatabaseCount('telemetry_samples', 1);
        $this->assertDatabaseCount('telemetry_channels', 5);
    }

    public function test_identical_duplicate_is_idempotent(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);

        $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $payload)
            ->assertCreated();

        $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $payload)
            ->assertOk()
            ->assertJson(['result' => 'identical_duplicate']);

        $this->assertDatabaseCount('telemetry_samples', 1);
        $this->assertDatabaseCount('telemetry_channels', 5);
    }

    public function test_late_identical_duplicate_keeps_newer_sequence(): void
    {
        [$device, $bearer] = $this->createDevice();
        $ten = $this->payload($device->device_id);
        $ten['sequence'] = 10;
        $eleven = $ten;
        $eleven['sequence'] = 11;
        $eleven['uptime_ms'] = 123457;

        $this->withToken($bearer)->postJson('/api/v1/telemetry', $ten)
            ->assertCreated();
        $this->withToken($bearer)->postJson('/api/v1/telemetry', $eleven)
            ->assertCreated();
        $this->withToken($bearer)->postJson('/api/v1/telemetry', $ten)
            ->assertOk()->assertJson(['result' => 'identical_duplicate']);

        $this->assertSame('11', (string) $device->fresh()->getRawOriginal('last_sequence'));
        $this->assertDatabaseCount('telemetry_samples', 2);
        $this->assertDatabaseCount('telemetry_channels', 10);
    }

    public function test_late_distinct_sample_same_boot_keeps_high_watermark(): void
    {
        [$device, $bearer] = $this->createDevice();
        $ten = $this->payload($device->device_id);
        $ten['sequence'] = 10;
        $twelve = $ten;
        $twelve['sequence'] = 12;
        $twelve['uptime_ms'] = 123458;
        $eleven = $ten;
        $eleven['sequence'] = 11;
        $eleven['uptime_ms'] = 123457;

        foreach ([$ten, $twelve, $eleven] as $payload) {
            $this->withToken($bearer)
                ->postJson('/api/v1/telemetry', $payload)
                ->assertCreated();
        }
        $this->assertSame('12', (string) $device->fresh()->getRawOriginal('last_sequence'));
        $this->assertDatabaseCount('telemetry_samples', 3);
    }

    public function test_duplicate_from_prior_boot_does_not_replace_current_boot(): void
    {
        [$device, $bearer] = $this->createDevice();
        $bootA = $this->payload($device->device_id);
        $bootA['boot_id'] = 'boot-A';
        $bootA['sequence'] = 100;
        $bootB = $bootA;
        $bootB['boot_id'] = 'boot-B';
        $bootB['sequence'] = 1;
        $bootB['uptime_ms'] = 100;

        $this->withToken($bearer)->postJson('/api/v1/telemetry', $bootA)
            ->assertCreated();
        $this->withToken($bearer)->postJson('/api/v1/telemetry', $bootB)
            ->assertCreated();
        $this->withToken($bearer)->postJson('/api/v1/telemetry', $bootA)
            ->assertOk()->assertJson(['result' => 'identical_duplicate']);

        $fresh = $device->fresh();
        $this->assertSame('boot-B', $fresh->getRawOriginal('last_boot_id'));
        $this->assertSame('1', (string) $fresh->getRawOriginal('last_sequence'));
        $this->assertDatabaseCount('telemetry_samples', 2);
    }

    public function test_uint64_decimal_comparison_does_not_overflow_on_late_sample(): void
    {
        [$device] = $this->createDevice();
        $service = app(\App\Services\TelemetryIngestService::class);
        $base = $this->payload($device->device_id);
        $base['sequence'] = '18446744073709551615';
        $service->ingest($device, $base);
        $older = $base;
        $older['sequence'] = '9223372036854775808';
        $older['uptime_ms'] = 123455;
        $service->ingest($device, $older);

        $this->assertSame(
            '18446744073709551615',
            (string) $device->fresh()->getRawOriginal('last_sequence')
        );
        $this->assertDatabaseCount('telemetry_samples', 2);
    }

    public function test_conflicting_duplicate_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);

        $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $payload)
            ->assertCreated();

        $payload['channels']['temperature_c']['value'] = 32.0;

        $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $payload)
            ->assertStatus(409)
            ->assertJson(['error' => 'conflicting_duplicate']);

        $this->assertDatabaseCount('telemetry_samples', 1);
    }

    public function test_missing_or_unknown_authentication_is_rejected(): void
    {
        $deviceId = 'demo-device-001';

        $this->postJson('/api/v1/telemetry', $this->payload($deviceId))
            ->assertUnauthorized();

        $this->withToken(Str::random(64))
            ->postJson('/api/v1/telemetry', $this->payload($deviceId))
            ->assertUnauthorized();

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_disabled_device_and_identity_mismatch_are_rejected(): void
    {
        [$disabled, $disabledBearer] = $this->createDevice(false);

        $this->withToken($disabledBearer)
            ->postJson('/api/v1/telemetry', $this->payload($disabled->device_id))
            ->assertForbidden();

        [$enabled, $enabledBearer] = $this->createDevice();

        $this->withToken($enabledBearer)
            ->postJson('/api/v1/telemetry', $this->payload('different-device'))
            ->assertForbidden()
            ->assertJson(['error' => 'device_identity_mismatch']);

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_invalid_quality_value_contract_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);
        $payload['channels']['bilge_level']['value'] = 0;

        $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $payload)
            ->assertUnprocessable();

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_payload_over_4096_bytes_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);
        $payload['padding'] = str_repeat('x', 4096);

        $raw = json_encode($payload, JSON_THROW_ON_ERROR);

        $response = $this
            ->withHeader('Authorization', 'Bearer '.$bearer)
            ->withHeader('Content-Type', 'application/json')
            ->call('POST', '/api/v1/telemetry', [], [], [], [], $raw);

        $response->assertStatus(413)
            ->assertJson(['error' => 'telemetry_payload_too_large']);

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_uint64_max_sequence_and_uptime_are_preserved(): void
    {
        [$device, $bearer] = $this->createDevice();
        $raw = json_encode(
            $this->payload($device->device_id),
            JSON_THROW_ON_ERROR
        );

        $raw = str_replace(
            '"sequence":42',
            '"sequence":18446744073709551615',
            $raw
        );
        $raw = str_replace(
            '"uptime_ms":123456',
            '"uptime_ms":18446744073709551615',
            $raw
        );

        $this
            ->call('POST', '/api/v1/telemetry', [], [], [], [
                'HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                'CONTENT_TYPE' => 'application/json',
                'HTTP_ACCEPT' => 'application/json',
            ], $raw)
            ->assertCreated();

        $this->assertDatabaseHas('telemetry_samples', [
            'sequence' => '18446744073709551615',
            'uptime_ms' => '18446744073709551615',
        ]);
    }

    public function test_channel_named_sequence_does_not_conflict_with_identity_validation(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);

        $payload['channels']['sequence'] = [
            'value' => 7.0,
            'quality' => 'valid',
        ];

        $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $payload)
            ->assertCreated();

        $this->assertDatabaseHas('telemetry_channels', [
            'name' => 'sequence',
            'quality' => 'valid',
        ]);
    }

    public function test_quoted_uint64_identity_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);
        $payload['sequence'] = '18446744073709551615';

        $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $payload)
            ->assertUnprocessable();

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_quoted_top_level_sequence_with_sequence_channel_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);
        $payload['channels']['sequence'] = [
            'value' => 7.0,
            'quality' => 'valid',
        ];

        $raw = json_encode($payload, JSON_THROW_ON_ERROR);
        $raw = str_replace(
            '"sequence":42',
            '"sequence":"18446744073709551615"',
            $raw
        );

        $this
            ->call('POST', '/api/v1/telemetry', [], [], [], [
                'HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                'CONTENT_TYPE' => 'application/json',
                'HTTP_ACCEPT' => 'application/json',
            ], $raw)
            ->assertUnprocessable();

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_channel_value_member_must_be_explicit_even_when_null(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);

        unset($payload['channels']['bilge_level']['value']);

        $this->withToken($bearer)
            ->postJson('/api/v1/telemetry', $payload)
            ->assertUnprocessable();

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_duplicate_top_level_identity_key_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $raw = json_encode(
            $this->payload($device->device_id),
            JSON_THROW_ON_ERROR
        );

        $raw = str_replace(
            '"sequence":42',
            '"sequence":42,"sequence":43',
            $raw
        );

        $this
            ->call('POST', '/api/v1/telemetry', [], [], [], [
                'HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                'CONTENT_TYPE' => 'application/json',
                'HTTP_ACCEPT' => 'application/json',
            ], $raw)
            ->assertUnprocessable();

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_duplicate_channel_key_is_rejected(): void
    {
        [$device, $bearer] = $this->createDevice();
        $payload = $this->payload($device->device_id);
        $raw = json_encode($payload, JSON_THROW_ON_ERROR);

        $duplicateChannel = trim(
            json_encode(
                [
                    'temperature_c' => [
                        'value' => 31.25,
                        'quality' => 'valid',
                    ],
                ],
                JSON_THROW_ON_ERROR
            ),
            '{}'
        );

        $raw = str_replace(
            '"channels":{',
            '"channels":{'.$duplicateChannel.',',
            $raw
        );

        $this
            ->call('POST', '/api/v1/telemetry', [], [], [], [
                'HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                'CONTENT_TYPE' => 'application/json',
                'HTTP_ACCEPT' => 'application/json',
            ], $raw)
            ->assertUnprocessable();

        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    private function createDevice(bool $enabled = true): array
    {
        $bearer = Str::random(64);

        $device = Device::query()->create([
            'device_id' => 'demo-device-'.Str::lower(Str::random(8)),
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
            'firmware_version' => 'phase9-test',
            'boot_id' => 'boot-demo-0001',
            'sequence' => 42,
            'uptime_ms' => 123456,
            'source_mode' => 'simulation',
            'channels' => [
                'temperature_c' => [
                    'value' => 31.25,
                    'quality' => 'valid',
                ],
                'bilge_level' => [
                    'value' => null,
                    'quality' => 'missing',
                ],
                'vibration_index' => [
                    'value' => null,
                    'quality' => 'invalid',
                ],
                'battery_voltage' => [
                    'value' => 12.4,
                    'quality' => 'stale',
                ],
                'zero_test' => [
                    'value' => 0.0,
                    'quality' => 'valid',
                ],
            ],
        ];
    }
}
