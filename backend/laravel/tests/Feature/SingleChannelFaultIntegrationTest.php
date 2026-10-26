<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

/** Actual C99 single-channel host stimulus, not a physical sensor/bus test. */
class SingleChannelFaultIntegrationTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    private function frames(): array
    {
        $path = getenv('VG_FAULT_ISOLATION_WIRE_JSONL');
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $frames = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertCount(4, $frames);

        return $frames;
    }

    private function deviceAndToken(): array
    {
        $token = bin2hex(random_bytes(32));
        $device = Device::query()->create(['device_id' => 'fault:demo',
            'token_digest' => hash('sha256', $token), 'enabled' => true]);

        return [$device, $token];
    }

    private function sendWire(string $wire, string $token)
    {
        return $this->call('POST', '/api/v1/telemetry', [], [], [], [
            'HTTP_AUTHORIZATION' => 'Bearer '.$token, 'CONTENT_TYPE' => 'application/json',
            'HTTP_ACCEPT' => 'application/json',
        ], $wire);
    }

    public function test_real_native_invalid_temperature_does_not_drop_other_current_channels(): void
    {
        [, $token] = $this->deviceAndToken();
        foreach ($this->frames() as $wire) {
            $packet = json_decode($wire, true, 512, JSON_THROW_ON_ERROR);
            $this->sendWire($wire, $token)->assertCreated();
            $state = $this->withToken($token)->getJson('/api/v1/device/state')->assertOk()
                ->assertJsonCount(44, 'state.channels')->json('state');
            foreach ($packet as $name => $expected) {
                $this->assertEquals($expected, $state[$name]);
            }
        }
        $this->assertDatabaseCount('telemetry_samples', 4);
        $this->assertDatabaseCount('telemetry_channels', 176);
        $this->assertSame(2, DB::table('telemetry_channels')->where('name', 'compartment_temperature_c')
            ->where('quality', 'invalid')->whereNull('value')->count());
        $this->assertSame(172, DB::table('telemetry_channels')->where('name', '<>', 'compartment_temperature_c')
            ->where('quality', 'valid')->whereNotNull('value')->count());
        $this->assertDatabaseHas('telemetry_channels', ['name' => 'engine_1_rpm', 'value' => 2003, 'quality' => 'valid']);
    }

    public function test_invalid_to_safe_zero_and_valid_to_null_are_refused_without_partial_rows(): void
    {
        [, $token] = $this->deviceAndToken();
        $packet = json_decode($this->frames()[1], true, 512, JSON_THROW_ON_ERROR);
        foreach ([['value' => 0, 'quality' => 'invalid'], ['value' => null, 'quality' => 'valid']] as $bad) {
            $packet['channels']['compartment_temperature_c'] = $bad;
            $this->sendWire(json_encode($packet, JSON_THROW_ON_ERROR), $token)->assertUnprocessable();
        }
        $this->assertDatabaseCount('telemetry_samples', 0);
        $this->assertDatabaseCount('telemetry_channels', 0);
    }

    public function test_fault_replay_is_idempotent_and_conflict_cannot_make_invalid_value_current(): void
    {
        [, $token] = $this->deviceAndToken();
        $wire = $this->frames()[1];
        $this->sendWire($wire, $token)->assertCreated();
        $this->sendWire($wire, $token)->assertOk()->assertJsonPath('result', 'identical_duplicate');
        $packet = json_decode($wire, true, 512, JSON_THROW_ON_ERROR);
        $packet['channels']['compartment_temperature_c'] = ['value' => 25, 'quality' => 'valid'];
        $this->sendWire(json_encode($packet, JSON_THROW_ON_ERROR), $token)->assertConflict();
        $this->assertDatabaseCount('telemetry_samples', 1);
        $this->assertDatabaseCount('telemetry_channels', 44);
        $this->withToken($token)->getJson('/api/v1/device/state')->assertOk()
            ->assertJsonPath('state.channels.compartment_temperature_c.value', null)
            ->assertJsonPath('state.channels.compartment_temperature_c.quality', 'invalid')
            ->assertJsonPath('state.channels.engine_1_rpm.value', 2001);
    }

    public function test_granted_browser_renders_fault_quality_and_unaffected_engine_then_valid_data(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $user = $this->operator();
        $this->grant($user, $device);
        config(['monitoring.presentation_profile' => 'continuous_simulation_v11',
            'monitoring.stale_after_seconds' => 10, 'monitoring.offline_after_seconds' => 30]);
        $frames = $this->frames();
        $this->sendWire($frames[1], $token)->assertCreated();
        $response = $this->actingAs($user, 'web')->get('/monitoring/fault:demo')->assertOk();
        $response->assertSee('SIMULATION')->assertSee('engine_1_rpm')->assertSee('2001')
            ->assertSee('compartment_temperature_c')->assertSee('INVALID')->assertSee('read-only');
        $this->assertMatchesRegularExpression('/<td>compartment_temperature_c<\/td><td>\s*&mdash;\s*<\/td>/', $response->getContent());
        $this->assertStringNotContainsString($token, $response->getContent());
        $this->sendWire($frames[3], $token)->assertCreated();
        $this->withToken($token)->getJson('/api/v1/device/state')->assertOk()
            ->assertJsonPath('state.channels.compartment_temperature_c.value', 30)
            ->assertJsonPath('state.channels.compartment_temperature_c.quality', 'valid')
            ->assertJsonPath('state.channels.engine_1_rpm.value', 2003);
    }

    public function test_unauthorized_fault_packet_is_not_stored(): void
    {
        $this->deviceAndToken();
        foreach (['', bin2hex(random_bytes(32))] as $token) {
            $this->sendWire($this->frames()[1], $token)->assertUnauthorized();
        }
        $this->assertDatabaseCount('telemetry_samples', 0);
        $this->assertDatabaseCount('telemetry_channels', 0);
    }
}
