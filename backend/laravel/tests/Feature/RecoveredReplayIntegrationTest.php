<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Models\MonitoringEvent;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

class RecoveredReplayIntegrationTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    private function frames(): array
    {
        $path = getenv('VG_RECOVERED_REPLAY_WIRE_JSONL');
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $frames = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertCount(6, $frames);

        return $frames;
    }

    private function identity(): array
    {
        $token = bin2hex(random_bytes(32));
        $device = Device::query()->create(['device_id' => 'replay:demo',
            'token_digest' => hash('sha256', $token), 'enabled' => true]);

        return [$device, $token];
    }

    private function send(string $wire, string $token)
    {
        return $this->call('POST', '/api/v1/events', [], [], [], [
            'HTTP_AUTHORIZATION' => 'Bearer '.$token, 'CONTENT_TYPE' => 'application/json',
            'HTTP_ACCEPT' => 'application/json',
        ], $wire);
    }

    public function test_actual_three_boot_recovery_is_idempotent_without_collapsing_ids_or_fabricating_metadata(): void
    {
        [, $token] = $this->identity();
        foreach ($this->frames() as $wire) {
            $this->send($wire, $token)->assertCreated();
            $this->send($wire, $token)->assertOk()->assertJsonPath('result', 'identical_event_duplicate');
        }
        $this->assertDatabaseCount('monitoring_events', 6);
        $this->assertSame(['boot-a', 'replay-boot-b', 'replay-boot-c'], MonitoringEvent::query()
            ->where('event_id', '1')->orderBy('boot_id')->pluck('boot_id')->all());
        $this->assertSame(2, MonitoringEvent::query()->whereNull('alarm_metadata')->count());
        $items = $this->withToken($token)->getJson('/api/v1/device/events?limit=100')
            ->assertOk()->assertJsonCount(6, 'items')->json('items');
        foreach ($items as $item) {
            if ($item['schema_version'] === '1.0') {
                $this->assertArrayNotHasKey('alarm', $item);
            }
            if ($item['boot_id'] === 'replay-boot-b' && $item['event_id'] === '2') {
                $this->assertSame('active_ack', $item['alarm']['state']);
                $this->assertSame('0', $item['alarm']['acknowledged_at_ms']);
                $this->assertNull($item['alarm']['cleared_at_ms']);
            }
        }
    }

    public function test_late_reverse_replay_renders_original_facts_without_inferring_global_active_state(): void
    {
        [$device, $token] = $this->identity();
        foreach (array_reverse($this->frames()) as $wire) {
            $this->send($wire, $token)->assertCreated();
        }
        $user = $this->operator();
        $this->grant($user, $device);
        $view = $this->actingAs($user, 'web')->get('/monitoring/replay:demo')->assertOk()
            ->assertSee('boot-a')->assertSee('replay-boot-b')->assertSee('replay-boot-c')
            ->assertSee('bench_test')->assertSee('active_ack')->assertSee('cleared')
            ->assertSee('ACK bukan CLEAR')->assertSee('daftar ini tidak menentukan alarm aktif')
            ->assertSee('tidak direkonstruksi dari event lain');
        $this->assertStringNotContainsString($token, $view->getContent());
        $this->assertDatabaseCount('telemetry_samples', 0);
        $this->assertDatabaseCount('monitoring_events', 6);
    }

    public function test_metadata_conflict_and_legacy_retroactive_upgrade_refuse_without_changing_retained_facts(): void
    {
        [, $token] = $this->identity();
        $frames = $this->frames();
        foreach ($frames as $wire) {
            $this->send($wire, $token)->assertCreated();
        }
        $changed = json_decode($frames[5], true, 512, JSON_THROW_ON_ERROR);
        $changed['alarm']['reason_code'] = 1003;
        $this->send(json_encode($changed, JSON_THROW_ON_ERROR), $token)->assertStatus(409);
        $legacy = json_decode($frames[0], true, 512, JSON_THROW_ON_ERROR);
        $legacy['schema_version'] = '1.1';
        $legacy['alarm'] = ['priority_code' => 1, 'reason_code' => 1, 'state' => 'active_unack',
            'raised_at_ms' => 10, 'acknowledged_at_ms' => null, 'cleared_at_ms' => null];
        $this->send(json_encode($legacy, JSON_THROW_ON_ERROR), $token)->assertStatus(409);
        $this->assertNull(MonitoringEvent::query()->where('boot_id', 'boot-a')->where('event_id', '1')->firstOrFail()->alarm_metadata);
        $this->assertSame(1002, MonitoringEvent::query()->where('boot_id', 'replay-boot-c')->firstOrFail()->alarm_metadata['reason_code']);
        $this->assertDatabaseCount('monitoring_events', 6);
    }

    public function test_recovered_bytes_keep_authentication_identity_and_raw_unsigned_validation_boundaries(): void
    {
        [, $token] = $this->identity();
        $frames = $this->frames();
        $this->send($frames[0], 'synthetic-invalid')->assertUnauthorized();
        $foreign = str_replace('"device_id":"replay:demo"', '"device_id":"other:demo"', $frames[0]);
        $this->send($foreign, $token)->assertForbidden();
        $duplicate = str_replace('"boot_id":', '"boot_id":"spoof","\\u0062oot_id":', $frames[0]);
        $this->send($duplicate, $token)->assertUnprocessable();
        $overflow = str_replace('"event_id":1,', '"event_id":18446744073709551616,', $frames[0]);
        $this->send($overflow, $token)->assertUnprocessable();
        $this->assertDatabaseCount('monitoring_events', 0);
    }
}
