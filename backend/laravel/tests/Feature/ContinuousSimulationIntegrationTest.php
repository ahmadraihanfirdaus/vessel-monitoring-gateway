<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

class ContinuousSimulationIntegrationTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    private function frames(): array
    {
        $path = getenv('VG_CONTINUOUS_WIRE_JSONL');
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $frames = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertCount(24, $frames);

        return $frames;
    }

    private function deviceAndToken(): array
    {
        $bearer = bin2hex(random_bytes(32));
        $device = Device::query()->create(['device_id' => 'continuous:demo',
            'token_digest' => hash('sha256', $bearer), 'enabled' => true]);

        return [$device, $bearer];
    }

    private function sendWire(string $wire, string $bearer)
    {
        return $this->call('POST', '/api/v1/telemetry', [], [], [], [
            'HTTP_AUTHORIZATION' => 'Bearer '.$bearer, 'CONTENT_TYPE' => 'application/json',
            'HTTP_ACCEPT' => 'application/json',
        ], $wire);
    }

    private function payload(int $count, string $version = '1.1'): array
    {
        $payload = json_decode($this->frames()[0], true, 512, JSON_THROW_ON_ERROR);
        $payload['schema_version'] = $version;
        $payload['channels'] = [];
        for ($i = 0; $i < $count; $i++) {
            $payload['channels']['c'.$i] = ['value' => 0, 'quality' => 'valid'];
        }

        return $payload;
    }

    public function test_actual_recovered_c99_frames_persist_48_channels_and_render_domain_sections(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        foreach ($this->frames() as $wire) {
            $this->sendWire($wire, $bearer)->assertCreated();
            $this->sendWire($wire, $bearer)->assertOk()->assertJsonPath('result', 'identical_duplicate');
        }
        $this->assertDatabaseCount('telemetry_samples', 24);
        $this->assertDatabaseCount('telemetry_channels', 24 * 48);
        $this->withToken($bearer)->getJson('/api/v1/device/state')->assertOk()
            ->assertJsonPath('state.schema_version', '1.1')->assertJsonPath('state.sequence', 24)
            ->assertJsonCount(48, 'state.channels')->assertJsonPath('state.channels.runtime_journal_retained.value', 8)
            ->assertJsonPath('state.channels.runtime_journal_rejected.value', 58);
        $user = $this->operator();
        $this->grant($user, $device);
        config(['monitoring.presentation_profile' => 'continuous_simulation_v11',
            'monitoring.stale_after_seconds' => 10, 'monitoring.offline_after_seconds' => 30]);
        $response = $this->actingAs($user, 'web')->get('/monitoring/continuous:demo')->assertOk();
        $response->assertSee('SIMULATION')->assertSee('engine_4_rpm')->assertSee('vapor_surrogate')
            ->assertSee('unitless surrogate; not ppm or %LEL')->assertSee('RUNNING')->assertSee('GOOD')
            ->assertSee('low-power prototype')->assertSee('incomplete retention');
        $this->assertStringNotContainsString($bearer, $response->getContent());
    }

    public function test_v10_stays_16_v11_accepts_72_and_73_rejects_atomically(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        foreach ([['1.0', 16, 201], ['1.0', 17, 422], ['1.1', 72, 201], ['1.1', 73, 422]] as $index => [$version, $count, $status]) {
            $payload = $this->payload($count, $version);
            $payload['sequence'] = $index + 1;
            $this->sendWire(json_encode($payload, JSON_THROW_ON_ERROR), $bearer)->assertStatus($status);
        }
        $this->assertDatabaseCount('telemetry_samples', 2);
        $this->assertDatabaseCount('telemetry_channels', 88);
    }

    public function test_new_version_does_not_bypass_4096_byte_limit(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        $wire = $this->frames()[0];
        $this->sendWire($wire.str_repeat(' ', 4096 - strlen($wire)), $bearer)->assertCreated();
        $this->sendWire($wire.str_repeat(' ', 4097 - strlen($wire)), $bearer)->assertStatus(413);
        $this->assertDatabaseCount('telemetry_samples', 1);
        $this->assertDatabaseCount('telemetry_channels', 48);
    }

    public function test_version_conflicts_do_not_create_second_identity_and_reordered_replay_is_idempotent(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        $payload = $this->payload(16);
        $this->sendWire(json_encode($payload, JSON_THROW_ON_ERROR), $bearer)->assertCreated();
        $payload['channels'] = array_reverse($payload['channels'], true);
        $this->sendWire(json_encode($payload, JSON_THROW_ON_ERROR), $bearer)->assertOk()
            ->assertJsonPath('result', 'identical_duplicate');
        $payload['schema_version'] = '1.0';
        $this->sendWire(json_encode($payload, JSON_THROW_ON_ERROR), $bearer)->assertStatus(409);
        $this->assertDatabaseCount('telemetry_samples', 1);
    }

    public function test_authentication_and_device_identity_still_fail_closed(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        $this->sendWire($this->frames()[0], '')->assertUnauthorized();
        $this->sendWire($this->frames()[0], bin2hex(random_bytes(32)))->assertUnauthorized();
        $payload = $this->payload(1);
        $payload['device_id'] = 'foreign:demo';
        $this->sendWire(json_encode($payload, JSON_THROW_ON_ERROR), $bearer)->assertForbidden();
        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_unknown_versions_numeric_versions_and_duplicate_keys_reject_without_rows(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        foreach (['1.2', '01.1', 1.1, ['1.1']] as $version) {
            $payload = $this->payload(1);
            $payload['schema_version'] = $version;
            $this->sendWire(json_encode($payload, JSON_THROW_ON_ERROR), $bearer)->assertStatus(422);
        }
        $wire = $this->frames()[0];
        $this->sendWire(str_replace('"schema_version":"1.1"', '"schema_version":"1.0","schema_version":"1.1"', $wire), $bearer)->assertStatus(422);
        $this->sendWire(str_replace('"engine_1_rpm":', '"engine_1_rpm":{"value":0,"quality":"valid"},"engine_1_rpm":', $wire), $bearer)->assertStatus(422);
        $this->assertDatabaseCount('telemetry_samples', 0);
    }

    public function test_new_version_preserves_uint64_lexical_and_null_quality_rules(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        $base = json_encode($this->payload(1), JSON_THROW_ON_ERROR);
        foreach (['1.0', '1e0', '"1"', '-1', '18446744073709551616'] as $badSequence) {
            $this->sendWire(str_replace('"sequence":1,', '"sequence":'.$badSequence.',', $base), $bearer)->assertStatus(422);
        }
        $this->sendWire(str_replace('"sequence":1,', '"sequence":18446744073709551615,', $base), $bearer)->assertCreated();
        $this->assertSame('18446744073709551615', (string) DB::table('telemetry_samples')->value('sequence'));
        foreach ([['value' => 0, 'quality' => 'missing'], ['value' => null, 'quality' => 'valid']] as $channel) {
            $payload = $this->payload(1);
            $payload['channels']['c0'] = $channel;
            $this->sendWire(json_encode($payload, JSON_THROW_ON_ERROR), $bearer)->assertStatus(422);
        }
        $this->assertDatabaseCount('telemetry_samples', 1);
    }

    public function test_recovered_missing_and_stale_navigation_survive_mysql_and_history(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        $frames = $this->frames();
        foreach ([0, 2, 4, 8] as $index) {
            $this->sendWire($frames[$index], $bearer)->assertCreated();
        }
        $this->withToken($bearer)->getJson('/api/v1/device/history')->assertOk()
            ->assertJsonPath('items.0.channels.nav_latitude_deg.value', 0)
            ->assertJsonPath('items.1.channels.nav_latitude_deg.value', null)
            ->assertJsonPath('items.1.channels.nav_latitude_deg.quality', 'missing')
            ->assertJsonPath('items.2.channels.nav_latitude_deg.quality', 'stale');
    }

    public function test_demo_presentation_remains_opt_in_and_source_version_guarded(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        $this->sendWire($this->frames()[0], $bearer)->assertCreated();
        $user = $this->operator();
        $this->grant($user, $device);
        $this->actingAs($user, 'web')->get('/monitoring/continuous:demo')->assertOk()
            ->assertDontSee('unitless surrogate; not ppm or %LEL');
        config(['monitoring.presentation_profile' => 'continuous_simulation_v11']);
        $this->get('/monitoring/continuous:demo')->assertOk()->assertSee('unitless surrogate; not ppm or %LEL');
        DB::table('telemetry_samples')->update(['source_mode' => 'bench_test']);
        $this->get('/monitoring/continuous:demo')->assertOk()->assertDontSee('unitless surrogate; not ppm or %LEL');
    }

    public function test_binary64_persistence_and_replay_ignore_ambient_php_precision_without_tolerance(): void
    {
        [$device, $bearer] = $this->deviceAndToken();
        $precision = ini_get('precision');
        $serializePrecision = ini_get('serialize_precision');
        try {
            ini_set('precision', '2');
            ini_set('serialize_precision', '2');
            foreach (['1.0', '1.1'] as $version) {
                foreach (['0.10000000149011612', '1.0000000000000002', '-1.2345678901234567',
                    '1e-200', '1e200', '0'] as $index => $number) {
                    $wire = '{"schema_version":"'.$version.'","device_id":"continuous:demo",'
                        .'"firmware_version":"synthetic","boot_id":"precision-'.$version.'",'
                        .'"sequence":'.($index + 1).',"uptime_ms":0,"source_mode":"simulation",'
                        .'"channels":{"c0":{"value":'.$number.',"quality":"valid"}}}';
                    $this->sendWire($wire, $bearer)->assertCreated();
                    $stored = DB::table('telemetry_channels')->orderByDesc('id')->value('value');
                    $this->assertSame(pack('d', (float) $number), pack('d', (float) $stored));
                    $this->sendWire($wire, $bearer)->assertOk()->assertJsonPath('result', 'identical_duplicate');
                    if ($number === '1.0000000000000002') {
                        $this->sendWire(str_replace($number, '1.0000000000000004', $wire), $bearer)->assertStatus(409);
                    }
                }
            }
            $this->assertDatabaseCount('telemetry_samples', 12);
        } finally {
            ini_set('precision', $precision);
            ini_set('serialize_precision', $serializePrecision);
        }
    }
}
