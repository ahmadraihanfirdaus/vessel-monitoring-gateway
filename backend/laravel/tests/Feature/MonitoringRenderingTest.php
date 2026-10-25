<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

class MonitoringRenderingTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    public function test_all_eight_sections_render_actual_data_and_configured_assignments(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $time = now()->format('Y-m-d H:i:s');
        $this->sample($device, $time, [
            'zero_demo' => ['value' => 0, 'quality' => 'valid'],
            'missing_demo' => ['value' => null, 'quality' => 'missing'],
            'stale_demo' => ['value' => 2, 'quality' => 'stale'],
        ]);
        config(['monitoring.stale_after_seconds' => 10, 'monitoring.offline_after_seconds' => 30,
            'monitoring.channel_sections.safety' => ['zero_demo'], 'monitoring.channel_sections.propulsion' => ['missing_demo'],
            'monitoring.channel_sections.navigation' => ['stale_demo'], 'monitoring.channel_sections.power' => ['zero_demo']]);
        DB::table('monitoring_events')->insert(['device_id' => $device->device_id, 'schema_version' => '1.0',
            'boot_id' => 'render-boot', 'event_id' => '18446744073709551615', 'linked_alarm_id' => 7,
            'source_id' => 1, 'source_mode' => 'bench_test', 'event_type' => 'alarm_ack', 'occurred_at_ms' => 0, 'received_at' => $time]);
        $response = $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk()
            ->assertSee('LIVE')->assertSee('SIMULATION')->assertSee('zero_demo')->assertSee('MISSING')->assertSee('STALE')
            ->assertSee('alarm_ack')->assertSee('18446744073709551615')->assertSee('bench_test')
            ->assertSee('ACK bukan CLEAR')->assertSee('NOT_APPROVED');
        foreach (['Overview', 'Safety', 'Propulsion', 'Navigation', 'Power', 'Alarms and Events', 'Device Health', 'Test Evidence'] as $section) {
            $response->assertSee('aria-label="'.$section.'"', false);
        }
        $response->assertViewHas('sectionChannels', static fn ($sections) => array_keys($sections['safety']) === ['zero_demo']
            && $sections['propulsion']['missing_demo']['value'] === null && count($sections['power']) === 1);
        $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
        $this->assertStringNotContainsString($device->token_digest, $response->getContent());
    }

    public function test_replayed_sample_and_fresh_transport_are_distinguished(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $device->forceFill(['last_seen_at' => now()])->save();
        $this->sample($device, now()->subSeconds(20)->format('Y-m-d H:i:s'), ['stale_demo' => ['value' => 0, 'quality' => 'valid']]);
        config(['monitoring.stale_after_seconds' => 10, 'monitoring.offline_after_seconds' => 30]);
        $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk()
            ->assertViewHas('sampleFreshness', static fn ($f) => $f['label'] === 'STALE')
            ->assertViewHas('transportFreshness', static fn ($f) => $f['label'] === 'LIVE');
    }

    public function test_unconfigured_policy_never_labels_a_receipt_live(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $this->sample($device, now()->format('Y-m-d H:i:s'), []);
        config(['monitoring.stale_after_seconds' => null, 'monitoring.offline_after_seconds' => null]);
        $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk()
            ->assertSee('FRESHNESS POLICY NOT CONFIGURED')->assertViewHas('sampleFreshness', static fn ($f) => $f['label'] === 'UNKNOWN');
    }

    public function test_no_sample_is_explicit_without_zero_or_safe_defaults(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        config(['monitoring.stale_after_seconds' => 10, 'monitoring.offline_after_seconds' => 30]);
        $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk()
            ->assertSee('DATA NOT CONNECTED')->assertSee('OFFLINE')->assertSee('Tidak diasumsikan bernilai nol atau aman.');
    }

    public function test_output_escapes_channel_names_and_never_displays_invalid_numeric_values(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $this->sample($device, now()->format('Y-m-d H:i:s'), ['<script>alert(1)</script>' => ['value' => 98765, 'quality' => 'invalid']]);
        $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk()
            ->assertSee('&lt;script&gt;', false)->assertDontSee('<script>', false)->assertDontSee('98765')->assertSee('INVALID');
    }

    public function test_browser_reads_do_not_write_device_event_or_telemetry_state(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $before = (array) DB::table('devices')->first();
        $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk();
        $this->assertSame($before, (array) DB::table('devices')->first());
        $this->assertDatabaseCount('telemetry_samples', 0);
        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_browser_snapshot_uses_one_matching_sample_lookup(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $this->sample($device, now()->format('Y-m-d H:i:s'), []);
        DB::enableQueryLog();
        DB::flushQueryLog();
        $response = $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk();
        $queries = DB::getQueryLog();
        DB::disableQueryLog();
        $this->assertCount(1, array_filter($queries, static fn ($q) => str_contains($q['query'], 'telemetry_samples')));
        $response->assertViewHas('health', static fn ($health) => $health['latest_firmware_version'] === 'synthetic-ui');
    }

    public function test_persisted_bench_sample_visibly_transitions_live_stale_offline_on_refresh(): void
    {
        $this->travelTo(\Carbon\CarbonImmutable::parse('2026-10-25 12:00:00', 'UTC'));
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $this->sample($device, now()->format('Y-m-d H:i:s'), ['zero_demo' => ['value' => 0, 'quality' => 'valid']], 'bench_test');
        config(['monitoring.stale_after_seconds' => 10, 'monitoring.offline_after_seconds' => 30]);
        foreach (['LIVE', 'STALE', 'OFFLINE'] as $step => $expected) {
            $this->travelTo(\Carbon\CarbonImmutable::parse('2026-10-25 12:00:00', 'UTC')->addSeconds([0, 10, 30][$step]));
            $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk()
                ->assertSee('class="badge '.$expected.'"', false)->assertSee('BENCH TEST')->assertSee('zero_demo')
                ->assertViewHas('sampleFreshness', static fn ($f) => $f['label'] === $expected);
        }
        $this->assertDatabaseCount('telemetry_samples', 1);
    }
}
