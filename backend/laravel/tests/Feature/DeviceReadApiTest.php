<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Tests\MySqlTestCase;

class DeviceReadApiTest extends MySqlTestCase
{
    use DatabaseTransactions;

    public function test_state_is_null_before_first_sample(): void
    {
        [$device, $bearer] = $this->createDevice();

        $this->withToken($bearer)
            ->getJson('/api/v1/device/state')
            ->assertOk()
            ->assertJson([
                'device_id' => $device->device_id,
                'state' => null,
            ]);
    }

    public function test_state_returns_latest_sample_only(): void
    {
        [$device, $bearer] = $this->createDevice();

        $first = $this->insertSample(
            $device->device_id,
            1,
            '2026-10-18 01:00:00'
        );

        $second = $this->insertSample(
            $device->device_id,
            2,
            '2026-10-18 01:01:00'
        );

        $this->insertChannel($first, 'temperature_c', 30.0, 'valid');
        $this->insertChannel($second, 'temperature_c', 31.0, 'valid');

        $this->withToken($bearer)
            ->getJson('/api/v1/device/state')
            ->assertOk()
            ->assertJsonPath('state.sequence', 2)
            ->assertJsonPath(
                'state.channels.temperature_c.quality',
                'valid'
            );
    }

    public function test_history_is_newest_first_and_bounded(): void
    {
        [$device, $bearer] = $this->createDevice();

        for ($i = 1; $i <= 3; $i++) {
            $this->insertSample(
                $device->device_id,
                $i,
                sprintf('2026-10-18 01:0%d:00', $i)
            );
        }

        $response = $this->withToken($bearer)
            ->getJson('/api/v1/device/history?limit=2')
            ->assertOk()
            ->assertJsonCount(2, 'items');

        $this->assertSame(3, $response->json('items.0.sequence'));
        $this->assertSame(2, $response->json('items.1.sequence'));
        $this->assertIsString($response->json('next_cursor'));
    }

    public function test_history_cursor_continuation_does_not_duplicate_rows(): void
    {
        [$device, $bearer] = $this->createDevice();

        for ($i = 1; $i <= 3; $i++) {
            $this->insertSample(
                $device->device_id,
                $i,
                sprintf('2026-10-18 02:0%d:00', $i)
            );
        }

        $first = $this->withToken($bearer)
            ->getJson('/api/v1/device/history?limit=2')
            ->assertOk();

        $cursor = urlencode((string) $first->json('next_cursor'));

        $second = $this->withToken($bearer)
            ->getJson('/api/v1/device/history?limit=2&cursor='.$cursor)
            ->assertOk();

        $firstIds = collect($first->json('items'))
            ->pluck('sequence')
            ->all();

        $secondIds = collect($second->json('items'))
            ->pluck('sequence')
            ->all();

        $this->assertSame(
            [],
            array_values(array_intersect($firstIds, $secondIds))
        );
    }

    public function test_health_never_seen_is_explicitly_nullable(): void
    {
        [$device, $bearer] = $this->createDevice();

        $this->withToken($bearer)
            ->getJson('/api/v1/device/health')
            ->assertOk()
            ->assertJson([
                'device_id' => $device->device_id,
                'seen' => false,
                'last_seen_at' => null,
                'last_boot_id' => null,
                'last_sequence' => null,
                'age_seconds' => null,
            ]);
    }

    public function test_health_exposes_last_seen_and_latest_sample_metadata(): void
    {
        [$device, $bearer] = $this->createDevice();

        $device->forceFill([
            'last_seen_at' => now()->subSeconds(5),
            'last_boot_id' => 'boot-health',
            'last_sequence' => 9,
        ])->save();

        $this->insertSample(
            $device->device_id,
            9,
            now()->subSeconds(5)->format('Y-m-d H:i:s'),
            'boot-health',
            'fw-health',
            9876,
            'simulation'
        );

        $this->withToken($bearer)
            ->getJson('/api/v1/device/health')
            ->assertOk()
            ->assertJsonPath('seen', true)
            ->assertJsonPath('last_boot_id', 'boot-health')
            ->assertJsonPath('last_sequence', 9)
            ->assertJsonPath('latest_firmware_version', 'fw-health')
            ->assertJsonPath('latest_source_mode', 'simulation')
            ->assertJsonPath('latest_uptime_ms', 9876);
    }

    public function test_read_endpoints_require_device_authentication(): void
    {
        $this->getJson('/api/v1/device/state')->assertUnauthorized();
        $this->getJson('/api/v1/device/history')->assertUnauthorized();
        $this->getJson('/api/v1/device/health')->assertUnauthorized();
    }

    private function createDevice(): array
    {
        $bearer = Str::random(64);

        $device = Device::query()->create([
            'device_id' => 'read-'.Str::lower(Str::random(20)),
            'token_digest' => hash('sha256', $bearer),
            'enabled' => true,
        ]);

        return [$device, $bearer];
    }

    private function insertSample(
        string $deviceId,
        int $sequence,
        string $receivedAt,
        string $bootId = 'boot-read',
        string $firmware = 'fw-read',
        int $uptime = 1000,
        string $sourceMode = 'simulation'
    ): int {
        return (int) DB::table('telemetry_samples')->insertGetId([
            'device_id' => $deviceId,
            'schema_version' => '1.0',
            'firmware_version' => $firmware,
            'boot_id' => $bootId,
            'sequence' => $sequence,
            'uptime_ms' => $uptime,
            'source_mode' => $sourceMode,
            'received_at' => $receivedAt,
        ]);
    }

    private function insertChannel(
        int $sampleId,
        string $name,
        ?float $value,
        string $quality
    ): void {
        DB::table('telemetry_channels')->insert([
            'telemetry_sample_id' => $sampleId,
            'name' => $name,
            'quality' => $quality,
            'value' => $value,
        ]);
    }
}
