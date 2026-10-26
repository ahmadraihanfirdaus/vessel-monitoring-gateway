<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\DatabaseTransactions;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

class MonitoringExpiryTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    public function test_granted_html_has_neutral_snapshot_fallback_four_bound_labels_and_hashed_external_asset(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $this->sample($device, now()->format('Y-m-d H:i:s'), ['zero' => ['value' => 0, 'quality' => 'valid']]);
        config(['monitoring.stale_after_seconds' => 2, 'monitoring.offline_after_seconds' => 4]);
        $response = $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk()
            ->assertSee('SNAPSHOT: LIVE')->assertSee('snapshot age:')->assertSee('Snapshot server:')
            ->assertSee('monitoring-freshness.js?v='.hash_file('sha256', public_path('assets/monitoring-freshness.js')), false);
        $this->assertSame(4, substr_count($response->getContent(), 'data-vg-freshness-scope='));
        $this->assertStringNotContainsString('class="badge LIVE"', $response->getContent());
        $csp = $response->headers->get('Content-Security-Policy');
        $this->assertStringContainsString("script-src 'self'; connect-src 'none'", $csp);
        $this->assertStringNotContainsString("script-src 'self' 'unsafe-inline'", $csp);
        $this->assertStringNotContainsString('<script>', $response->getContent());
    }

    public function test_login_list_and_denial_keep_scripts_disabled(): void
    {
        $this->assertStringContainsString("script-src 'none'", $this->get('/login')->headers->get('Content-Security-Policy'));
        $user = $this->operator();
        foreach (['/monitoring', '/monitoring/unknown-device'] as $path) {
            $response = $this->actingAs($user, 'web')->get($path);
            $this->assertStringContainsString("script-src 'none'", $response->headers->get('Content-Security-Policy'));
        }
    }

    public function test_absent_optional_asset_on_server_retains_neutral_authenticated_snapshot(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $this->sample($device, now()->format('Y-m-d H:i:s'), []);
        config(['monitoring.stale_after_seconds' => 2, 'monitoring.offline_after_seconds' => 4]);
        // Change only this test application's public path to an absent owned
        // fixture name; never move/delete the actual asset or other WIP files.
        $this->app->usePublicPath(sys_get_temp_dir().'/vg-absent-public-'.bin2hex(random_bytes(12)));
        $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk()
            ->assertSee('SNAPSHOT: LIVE')->assertViewHas('freshnessAssetHash', '')
            ->assertViewHas('sampleFreshness', static fn ($freshness) => $freshness['label'] === 'LIVE');
    }
}
