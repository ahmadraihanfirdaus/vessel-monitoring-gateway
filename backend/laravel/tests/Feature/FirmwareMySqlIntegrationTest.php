<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Tests\MySqlTestCase;

/** Real C99 bytes -> Laravel HTTP kernel -> real auth/services/MySQL. No doubles. */
class FirmwareMySqlIntegrationTest extends MySqlTestCase
{
    use DatabaseTransactions;

    public function test_populated_catalog_is_rejected_before_migration_admission(): void
    {
        $before = DB::table('migrations')->count();
        $this->device('synthetic-isolation-probe');
        try {
            \Tests\Support\MySqlIsolation::assertMigratedAndEmpty(DB::connection('mysql')->getPdo());
            $this->fail('Populated catalog was admitted.');
        } catch (\RuntimeException $exception) {
            $this->assertSame('MYSQL_TEST_BLOCKED: preexisting application rows prohibited.', $exception->getMessage());
        }
        $this->assertSame($before, DB::table('migrations')->count());
    }

    private function wire(string $variable, int $index = 0): string
    {
        $path = getenv($variable);
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $lines = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertCount($variable === 'VG_B14_WIRE_JSONL' ? 2 : 4, $lines);
        $this->assertLessThanOrEqual(4096, strlen($lines[$index]));

        return $lines[$index];
    }

    private function device(string $id, bool $enabled = true): string
    {
        $bearer = bin2hex(random_bytes(32));
        Device::query()->create(['device_id' => $id, 'token_digest' => hash('sha256', $bearer), 'enabled' => $enabled]);

        return $bearer;
    }

    private function postWire(string $path, string $wire, ?string $bearer)
    {
        $headers = ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'];
        if ($bearer !== null) {
            $headers['HTTP_AUTHORIZATION'] = 'Bearer '.$bearer;
        }
        $response = $this->call('POST', $path, [], [], [], $headers, $wire);
        $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
        if ($bearer !== null) {
            $this->assertStringNotContainsString($bearer, $response->getContent());
        }

        return $response;
    }

    public function test_c99_telemetry_persists_null_zero_provenance_and_read_state(): void
    {
        $bearer = $this->device('b14-demo-device');
        $this->postWire('/api/v1/telemetry', $this->wire('VG_B14_WIRE_JSONL'), $bearer)->assertCreated();
        $this->assertDatabaseCount('telemetry_samples', 1);
        $this->assertDatabaseCount('telemetry_channels', 2);
        $this->assertDatabaseHas('telemetry_channels', ['name' => 'bilge_level', 'quality' => 'missing', 'value' => null]);
        $this->assertDatabaseHas('telemetry_channels', ['name' => 'zero_test', 'quality' => 'valid', 'value' => 0]);
        $state = $this->withToken($bearer)->getJson('/api/v1/device/state')->assertOk();
        $state->assertJsonPath('state.source_mode', 'simulation')
            ->assertJsonPath('state.channels.bilge_level.value', null)
            ->assertJsonPath('state.channels.bilge_level.quality', 'missing');
        $this->assertNotNull($state->json('state.channels.zero_test.value'));
        $this->assertEquals(0, $state->json('state.channels.zero_test.value'));
        $this->assertStringContainsString('no-store', (string) $state->headers->get('Cache-Control'));
    }

    public function test_exact_replay_is_idempotent_and_conflict_cannot_overwrite_sample(): void
    {
        $bearer = $this->device('b14-demo-device');
        $raw = $this->wire('VG_B14_WIRE_JSONL');
        $first = $this->postWire('/api/v1/telemetry', $raw, $bearer)->assertCreated();
        $id = $first->json('sample_id');
        $this->postWire('/api/v1/telemetry', $raw, $bearer)->assertOk()
            ->assertJson(['result' => 'identical_duplicate', 'sample_id' => $id]);
        $conflict = str_replace('"value":0', '"value":1', $raw);
        $this->assertNotSame($raw, $conflict);
        $this->postWire('/api/v1/telemetry', $conflict, $bearer)->assertStatus(409)
            ->assertJson(['error' => 'conflicting_duplicate', 'sample_id' => $id]);
        $this->assertDatabaseCount('telemetry_samples', 1);
        $this->assertDatabaseCount('telemetry_channels', 2);
        $this->assertDatabaseHas('telemetry_channels', ['name' => 'zero_test', 'value' => 0]);
    }

    public function test_c99_uint64_max_stays_exact_through_storage_receipt_and_health(): void
    {
        $bearer = $this->device('b14-demo-device');
        $raw = $this->wire('VG_B14_WIRE_JSONL', 1);
        $this->postWire('/api/v1/telemetry', $raw, $bearer)->assertCreated();
        $sample = DB::table('telemetry_samples')->first();
        $this->assertSame('18446744073709551615', (string) $sample->sequence);
        $this->assertSame('18446744073709551615', (string) $sample->uptime_ms);
        $this->postWire('/api/v1/telemetry', $raw, $bearer)->assertOk()->assertJsonPath('result', 'identical_duplicate');
        $health = $this->withToken($bearer)->getJson('/api/v1/device/health')->assertOk();
        $this->assertSame('18446744073709551615', (string) $health->json('last_sequence'));
        $this->assertSame('18446744073709551615', (string) $health->json('latest_uptime_ms'));
    }

    public function test_same_boot_late_sample_preserves_high_watermark_and_all_history(): void
    {
        $bearer = $this->device('b14-demo-device');
        $this->postWire('/api/v1/telemetry', $this->wire('VG_B14_WIRE_JSONL', 1), $bearer)->assertCreated();
        $this->postWire('/api/v1/telemetry', $this->wire('VG_B14_WIRE_JSONL'), $bearer)->assertCreated();
        $this->assertSame('18446744073709551615',
            (string) Device::query()->first()->getRawOriginal('last_sequence'));
        $this->withToken($bearer)->getJson('/api/v1/device/history?limit=1')->assertOk()
            ->assertJsonCount(1, 'items');
        $this->assertDatabaseCount('telemetry_samples', 2);
        // /state is latest SERVER RECEIPT, not a cross-boot chronological oracle.
    }

    public function test_auth_identity_and_disabled_device_denials_leave_no_samples(): void
    {
        $raw = $this->wire('VG_B14_WIRE_JSONL');
        $this->postWire('/api/v1/telemetry', $raw, null)->assertUnauthorized();
        $this->postWire('/api/v1/telemetry', $raw, bin2hex(random_bytes(32)))->assertUnauthorized();
        $other = $this->device('other-synthetic-device');
        $this->postWire('/api/v1/telemetry', $raw, $other)->assertForbidden();
        $disabled = $this->device('b14-demo-device', false);
        $this->postWire('/api/v1/telemetry', $raw, $disabled)->assertForbidden();
        $this->assertDatabaseCount('telemetry_samples', 0);
        $this->assertDatabaseCount('telemetry_channels', 0);
    }

    public function test_invalid_null_zero_quality_and_oversize_wire_never_persist(): void
    {
        $bearer = $this->device('b14-demo-device');
        $raw = $this->wire('VG_B14_WIRE_JSONL');
        $bad = str_replace('"quality":"missing"', '"quality":"valid"', $raw);
        $this->assertNotSame($raw, $bad);
        $this->postWire('/api/v1/telemetry', $bad, $bearer)->assertUnprocessable();
        $this->postWire('/api/v1/telemetry', substr($raw, 0, -1), $bearer)->assertUnprocessable();
        $this->postWire('/api/v1/telemetry', str_repeat(' ', 4097), $bearer)->assertStatus(413);
        $overflow = str_replace('18446744073709551615', '18446744073709551616', $this->wire('VG_B14_WIRE_JSONL', 1));
        $this->postWire('/api/v1/telemetry', $overflow, $bearer)->assertUnprocessable();
        $this->assertDatabaseCount('telemetry_samples', 0);
        $this->assertDatabaseCount('telemetry_channels', 0);
    }

    public function test_c99_event_lifecycle_keeps_distinct_identity_source_and_alarm_link(): void
    {
        $bearer = $this->device('b15-demo-device');
        foreach (['alarm_raised', 'alarm_ack', 'alarm_cleared', 'fault'] as $i => $type) {
            $raw = $this->wire('VG_B15_EVENT_JSONL', $i);
            $this->postWire('/api/v1/events', $raw, $bearer)->assertCreated()->assertJsonPath('result', 'event_persisted');
            $this->postWire('/api/v1/events', $raw, $bearer)->assertOk()->assertJsonPath('result', 'identical_event_duplicate');
            $this->assertDatabaseHas('monitoring_events', ['event_id' => $i + 1, 'linked_alarm_id' => 7,
                'event_type' => $type, 'source_mode' => $i === 2 ? 'bench_test' : 'simulation']);
        }
        $this->assertDatabaseCount('monitoring_events', 4);
        // Persistence of ACK is not an instruction to clear a local alarm.
    }

    public function test_event_conflict_and_foreign_device_cannot_rewrite_or_insert_events(): void
    {
        $bearer = $this->device('b15-demo-device');
        $raw = $this->wire('VG_B15_EVENT_JSONL');
        $this->postWire('/api/v1/events', $raw, $bearer)->assertCreated();
        $changed = str_replace('"linked_alarm_id":7', '"linked_alarm_id":8', $raw);
        $this->assertNotSame($raw, $changed);
        $this->postWire('/api/v1/events', $changed, $bearer)->assertStatus(409)->assertJsonPath('error', 'conflicting_event_duplicate');
        $other = $this->device('foreign-synthetic-device');
        $this->postWire('/api/v1/events', $raw, $other)->assertForbidden();
        $this->postWire('/api/v1/events', $raw, null)->assertUnauthorized();
        $this->assertDatabaseCount('monitoring_events', 1);
        $this->assertDatabaseHas('monitoring_events', ['event_id' => 1, 'linked_alarm_id' => 7]);
        $this->assertNull(Device::query()->where('device_id', 'foreign-synthetic-device')->first()->last_seen_at);
    }
}
