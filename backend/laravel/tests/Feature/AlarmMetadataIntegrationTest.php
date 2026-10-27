<?php

namespace Tests\Feature;

use App\Models\Device;
use App\Models\MonitoringEvent;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use RuntimeException;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;
use Tests\Support\TestSchema;

class AlarmMetadataIntegrationTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    private function frames(): array
    {
        $path = getenv('VG_ALARM_METADATA_WIRE_JSONL');
        $this->assertIsString($path);
        $this->assertFileExists($path);
        $frames = file($path, FILE_IGNORE_NEW_LINES);
        $this->assertCount(11, $frames);

        return $frames;
    }

    private function deviceAndToken(): array
    {
        $token = bin2hex(random_bytes(32));
        $device = Device::query()->create(['device_id' => 'alarm:demo',
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

    public function test_native_recovered_transitions_persist_replay_read_and_render_complete_metadata(): void
    {
        [$device, $token] = $this->deviceAndToken();
        foreach ($this->frames() as $wire) {
            $this->send($wire, $token)->assertCreated();
            $this->send($wire, $token)->assertOk()->assertJsonPath('result', 'identical_event_duplicate');
        }
        $this->assertDatabaseCount('monitoring_events', 11);
        $zero = MonitoringEvent::query()->where('boot_id', 'synthetic-alarm-zero')->orderBy('event_id')->get();
        $this->assertSame('active_unack', $zero[0]->alarm_metadata['state']);
        $this->assertNull($zero[0]->alarm_metadata['acknowledged_at_ms']);
        $this->assertSame('active_ack', $zero[1]->alarm_metadata['state']);
        $this->assertSame('0', $zero[1]->alarm_metadata['acknowledged_at_ms']);
        $this->assertNull($zero[1]->alarm_metadata['cleared_at_ms']);
        $this->assertSame('cleared', $zero[2]->alarm_metadata['state']);
        $this->assertSame('0', $zero[2]->alarm_metadata['cleared_at_ms']);
        $this->withToken($token)->getJson('/api/v1/device/events?limit=100')->assertOk()->assertJsonCount(11, 'items');
        $user = $this->operator();
        $this->grant($user, $device);
        $response = $this->actingAs($user, 'web')->get('/monitoring/alarm:demo')->assertOk()
            ->assertSee('Alarm snapshot at transition')->assertSee('active_unack')->assertSee('active_ack')
            ->assertSee('cleared')->assertSee('Priority code (demo):')->assertSee('reason code:')
            ->assertSee('NOT_ACKNOWLEDGED')->assertSee('NOT_CLEARED')->assertSee('ACK bukan CLEAR');
        $this->assertStringNotContainsString($token, $response->getContent());
    }

    public function test_legacy_events_stay_metadata_unavailable_and_retain_old_read_shape(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $payload = json_decode($this->frames()[0], true, 512, JSON_THROW_ON_ERROR);
        unset($payload['alarm']);
        $payload['schema_version'] = '1.0';
        $wire = json_encode($payload, JSON_THROW_ON_ERROR);
        $this->send($wire, $token)->assertCreated();
        $this->send($wire, $token)->assertOk();
        $this->assertNull(MonitoringEvent::query()->firstOrFail()->alarm_metadata);
        $item = $this->withToken($token)->getJson('/api/v1/device/events')->assertOk()->json('items.0');
        $this->assertArrayNotHasKey('alarm', $item);
        $user = $this->operator();
        $this->grant($user, $device);
        $this->actingAs($user, 'web')->get('/monitoring/alarm:demo')->assertOk()
            ->assertSee('Metadata alarm lengkap tidak tersedia');
    }

    public function test_alarm_ack_state_never_reads_as_cleared_and_fact_snapshots_remain_immutable(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $frames = $this->frames();
        $this->send($frames[0], $token)->assertCreated();
        $this->send($frames[1], $token)->assertCreated();
        $this->withToken($token)->getJson('/api/v1/device/events')->assertOk()
            ->assertJsonPath('items.0.event_type', 'alarm_ack')->assertJsonPath('items.0.alarm.state', 'active_ack')
            ->assertJsonPath('items.0.alarm.cleared_at_ms', null)
            ->assertJsonPath('items.1.alarm.state', 'active_unack')
            ->assertJsonPath('items.1.alarm.acknowledged_at_ms', null);
        $this->send($frames[2], $token)->assertCreated();
        $this->assertSame('active_unack', MonitoringEvent::query()->where('event_id', 1)->firstOrFail()->alarm_metadata['state']);
    }

    public function test_metadata_reorder_is_identical_but_valid_changed_facts_conflict_without_mutation(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $payload = json_decode($this->frames()[0], true, 512, JSON_THROW_ON_ERROR);
        $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertCreated();
        $payload['alarm'] = array_reverse($payload['alarm'], true);
        $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertOk();
        $payload['alarm']['reason_code']++;
        $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertStatus(409);
        $this->assertSame(1001, MonitoringEvent::query()->firstOrFail()->alarm_metadata['reason_code']);
        unset($payload['alarm']);
        $payload['schema_version'] = '1.0';
        $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertStatus(409);
        $this->assertDatabaseCount('monitoring_events', 1);
    }

    public function test_reordered_persisted_json_replays_without_fact_mutation(): void
    {
        [, $token] = $this->deviceAndToken();
        $wire = $this->frames()[0];
        $this->send($wire, $token)->assertCreated();
        $event = MonitoringEvent::query()->firstOrFail();
        $facts = $event->alarm_metadata;
        // Persist a different object order on either engine. JSON object order
        // is not an event fact; MySQL binary JSON may reorder it on readback.
        $event->forceFill(['alarm_metadata' => array_reverse($facts, true)])->save();
        $before = $event->fresh()->getRawOriginal();
        $this->send($wire, $token)->assertOk()->assertJsonPath('result', 'identical_event_duplicate');
        $this->assertSame($before, $event->fresh()->getRawOriginal());
        $this->assertDatabaseCount('monitoring_events', 1);
        $this->assertNull($event->fresh()->alarm_metadata['acknowledged_at_ms']);
        $this->assertNull($event->fresh()->alarm_metadata['cleared_at_ms']);
        $payload = json_decode($wire, true, 512, JSON_THROW_ON_ERROR);
        $payload['alarm']['reason_code']++;
        $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertStatus(409);
        $this->assertSame($before, $event->fresh()->getRawOriginal());
    }

    public function test_inconsistent_lifecycle_and_codes_reject_before_any_database_write(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $original = json_decode($this->frames()[0], true, 512, JSON_THROW_ON_ERROR);
        foreach (['priority_code' => 0, 'reason_code' => 0, 'state' => 'active_ack', 'raised_at_ms' => 1,
            'acknowledged_at_ms' => 0, 'cleared_at_ms' => 0, 'unknown' => 1] as $key => $value) {
            $payload = $original;
            $payload['alarm'][$key] = $value;
            $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertStatus(422);
        }
        foreach (['fault', 'recovery', 'alarm_ack', 'alarm_cleared'] as $type) {
            $payload = $original;
            $payload['event_type'] = $type;
            $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertStatus(422);
        }
        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_quoted_floating_exponent_overflow_and_negative_alarm_numbers_are_rejected(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $wire = $this->frames()[0];
        foreach (['"3"', '3.0', '3e0', '-1', '4294967296'] as $number) {
            $this->send(str_replace('"priority_code":3', '"priority_code":'.$number, $wire), $token)->assertStatus(422);
        }
        foreach (['"0"', '0.0', '0e0', '-1', '18446744073709551616'] as $number) {
            $this->send(str_replace('"raised_at_ms":0', '"raised_at_ms":'.$number, $wire), $token)->assertStatus(422);
        }
        $this->send(str_replace('"event_id":1', '"event_id":0', $wire), $token)->assertStatus(422);
        $this->send(str_replace('"linked_alarm_id":1', '"linked_alarm_id":0', $wire), $token)->assertStatus(422);
        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_unicode_duplicate_keys_and_nested_shadowing_do_not_bypass_raw_integer_rules(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $wire = $this->frames()[0];
        foreach ([
            str_replace('"event_id":1', '"event_id":1,"\u0065vent_id":1', $wire),
            str_replace('"raised_at_ms":0', '"raised_at_ms":0,"\u0072aised_at_ms":0', $wire),
            str_replace('"state":"active_unack"', '"state":"active_unack","\u0073tate":"active_unack"', $wire),
            str_replace('"event_id":1', '"event_id":"1"', str_replace('"alarm":{', '"alarm":{"event_id":1,', $wire)),
        ] as $bad) {
            $this->send($bad, $token)->assertStatus(422);
        }
        $this->assertDatabaseCount('monitoring_events', 0);
        $escaped = str_replace('"event_id":1', '"\u0065vent_id":1', $wire);
        $this->send($escaped, $token)->assertCreated();
        $this->send($wire, $token)->assertOk();
    }

    public function test_metadata_uint64_and_uint32_maxima_preserve_exact_decimal_read_values(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $wire = '{"schema_version":"1.1","device_id":"alarm:demo","boot_id":"boundary",'
            .'"event_id":18446744073709551615,"linked_alarm_id":18446744073709551615,'
            .'"source_id":4294967295,"source_mode":"bench_test","event_type":"alarm_raised",'
            .'"occurred_at_ms":18446744073709551615,"alarm":{"priority_code":4294967295,'
            .'"reason_code":4294967295,"state":"active_unack","raised_at_ms":18446744073709551615,'
            .'"acknowledged_at_ms":null,"cleared_at_ms":null}}';
        $this->send($wire, $token)->assertCreated();
        $this->send($wire, $token)->assertOk();
        $this->withToken($token)->getJson('/api/v1/device/events')->assertOk()
            ->assertJsonPath('items.0.event_id', '18446744073709551615')
            ->assertJsonPath('items.0.alarm.raised_at_ms', '18446744073709551615')
            ->assertJsonPath('items.0.alarm.priority_code', 4294967295);
    }

    public function test_complete_metadata_keeps_auth_identity_and_4096_byte_boundaries(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $wire = $this->frames()[0];
        $this->send($wire, '')->assertUnauthorized();
        $this->send(str_replace('alarm:demo', 'foreign:demo', $wire), $token)->assertForbidden();
        $this->send($wire.str_repeat(' ', 4097 - strlen($wire)), $token)->assertStatus(413);
        $this->assertDatabaseCount('monitoring_events', 0);
        $this->send($wire.str_repeat(' ', 4096 - strlen($wire)), $token)->assertCreated();
    }

    public function test_missing_or_invalid_nested_metadata_never_uses_safe_defaults(): void
    {
        [$device, $token] = $this->deviceAndToken();
        $original = json_decode($this->frames()[0], true, 512, JSON_THROW_ON_ERROR);
        foreach ([null, [], ['priority_code' => 3], 'active_unack'] as $metadata) {
            $payload = $original;
            $payload['alarm'] = $metadata;
            $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertStatus(422);
        }
        $payload = $original;
        $payload['schema_version'] = '1.0';
        $this->send(json_encode($payload, JSON_THROW_ON_ERROR), $token)->assertStatus(422);
        $this->send($this->frames()[0], $token)->assertCreated();
        MonitoringEvent::query()->firstOrFail()->forceFill(['alarm_metadata' => null])->save();
        $this->withToken($token)->getJson('/api/v1/device/events')->assertOk()->assertJsonPath('items.0.alarm', null);
    }

    public function test_current_schema_rejects_previous_admission_profile_and_exposes_nullable_json_column(): void
    {
        TestSchema::assertMigratedAndEmpty(DB::connection('mysql')->getPdo());
        $this->assertContains('alarm_metadata', DB::connection('mysql')->getSchemaBuilder()->getColumnListing('monitoring_events'));
        $this->expectException(RuntimeException::class);
        TestSchema::assertMigratedAndEmpty(DB::connection('mysql')->getPdo(), false, true);
    }
}
