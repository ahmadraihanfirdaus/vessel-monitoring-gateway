<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

class RuntimeUplinkIntegrationTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    public function test_actual_c99_runtime_frames_persist_and_render_with_colon_device_identity(): void
    {
        $path = getenv('VG_RUNTIME_WIRE_JSONL');
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $lines = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertCount(6, $lines);
        $bearer = bin2hex(random_bytes(32));
        $device = Device::query()->create(['device_id' => 'runtime:demo', 'token_digest' => hash('sha256', $bearer), 'enabled' => true]);
        foreach ($lines as $line) {
            $this->call('POST', '/api/v1/telemetry', [], [], [], ['HTTP_AUTHORIZATION' => 'Bearer '.$bearer,
                'CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'], $line)->assertCreated();
        }
        $this->assertDatabaseCount('telemetry_samples', 6);
        $this->assertDatabaseHas('telemetry_channels', ['quality' => 'missing', 'value' => null]);
        $this->assertDatabaseHas('telemetry_channels', ['quality' => 'invalid', 'value' => null]);
        $this->withToken($bearer)->getJson('/api/v1/device/history')->assertOk()->assertJsonCount(6, 'items')
            ->assertJsonPath('items.0.sequence', 6)->assertJsonPath('items.1.channels.demo_channel.quality', 'stale');
        $user = $this->operator();
        $this->actingAs($user, 'web')->get('/monitoring/runtime:demo')->assertNotFound();
        $this->grant($user, $device);
        config(['monitoring.stale_after_seconds' => 10, 'monitoring.offline_after_seconds' => 30]);
        $this->get('/monitoring/runtime:demo')->assertOk()->assertSee('demo_channel')->assertSee('SIMULATION')->assertSee('LIVE');
        $this->assertSame(4, DB::table('telemetry_channels')->whereNotNull('value')->count());
    }
}
