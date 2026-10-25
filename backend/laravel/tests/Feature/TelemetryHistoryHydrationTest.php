<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Tests\MySqlTestCase;

class TelemetryHistoryHydrationTest extends MySqlTestCase
{
    use DatabaseTransactions;

    public function test_page_hydrates_channels_once_without_mixing_samples_or_devices(): void
    {
        $bearer = bin2hex(random_bytes(32));
        foreach (['history-reader', 'foreign-history'] as $deviceId) {
            Device::query()->create(['device_id' => $deviceId, 'token_digest' => hash('sha256', $deviceId === 'history-reader' ? $bearer : bin2hex(random_bytes(32))), 'enabled' => true]);
            for ($sequence = 1; $sequence <= 101; $sequence++) {
                $id = DB::table('telemetry_samples')->insertGetId([
                    'device_id' => $deviceId, 'schema_version' => '1.0', 'firmware_version' => 'history-fw',
                    'boot_id' => 'history-boot', 'sequence' => $sequence, 'uptime_ms' => $sequence,
                    'source_mode' => 'simulation', 'received_at' => '2026-10-25 01:00:00',
                ]);
                DB::table('telemetry_channels')->insert([
                    ['telemetry_sample_id' => $id, 'name' => 'zero', 'value' => 0, 'quality' => 'valid'],
                    ['telemetry_sample_id' => $id, 'name' => 'missing', 'value' => null, 'quality' => 'missing'],
                    ['telemetry_sample_id' => $id, 'name' => 'stale', 'value' => $sequence, 'quality' => 'stale'],
                ]);
            }
        }

        DB::enableQueryLog();
        DB::flushQueryLog();
        $response = $this->withToken($bearer)->getJson('/api/v1/device/history?limit=100')
            ->assertOk()->assertJsonCount(100, 'items');
        $queries = DB::getQueryLog();
        DB::disableQueryLog();
        $channelQueries = array_filter($queries, static fn (array $entry) => str_contains($entry['query'], 'telemetry_channels'));
        $this->assertCount(1, $channelQueries);
        $this->assertCount(100, array_values($channelQueries)[0]['bindings']);
        foreach ($response->json('items') as $index => $sample) {
            $this->assertSame('history-reader', $sample['device_id']);
            $this->assertSame(101 - $index, (int) $sample['sequence']);
            $this->assertNotNull($sample['channels']['zero']['value']);
            $this->assertEquals(0, $sample['channels']['zero']['value']);
            $this->assertNull($sample['channels']['missing']['value']);
            $this->assertSame('missing', $sample['channels']['missing']['quality']);
            $this->assertSame('stale', $sample['channels']['stale']['quality']);
            $this->assertEquals($sample['sequence'], $sample['channels']['stale']['value']);
        }
        $cursor = urlencode($response->json('next_cursor'));
        $this->withToken($bearer)->getJson('/api/v1/device/history?limit=100&cursor='.$cursor)
            ->assertOk()->assertJsonCount(1, 'items')->assertJsonPath('items.0.sequence', 1)
            ->assertJsonPath('next_cursor', null);
    }

    public function test_empty_history_does_not_query_channels(): void
    {
        $bearer = bin2hex(random_bytes(32));
        Device::query()->create(['device_id' => 'empty-history', 'token_digest' => hash('sha256', $bearer), 'enabled' => true]);
        DB::enableQueryLog();
        DB::flushQueryLog();
        $this->withToken($bearer)->getJson('/api/v1/device/history')->assertOk()->assertJsonPath('items', []);
        $queries = DB::getQueryLog();
        DB::disableQueryLog();
        foreach ($queries as $entry) {
            $this->assertStringNotContainsString('telemetry_channels', $entry['query']);
        }
    }
}
