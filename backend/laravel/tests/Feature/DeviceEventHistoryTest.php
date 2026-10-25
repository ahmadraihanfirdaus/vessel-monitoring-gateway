<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Pagination\Cursor;
use Illuminate\Support\Facades\DB;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\MySqlTestCase;

class DeviceEventHistoryTest extends MySqlTestCase
{
    use DatabaseTransactions;

    private function device(string $id = 'event-reader', bool $enabled = true): string
    {
        $bearer = bin2hex(random_bytes(32));
        Device::query()->create(['device_id' => $id, 'token_digest' => hash('sha256', $bearer), 'enabled' => $enabled]);

        return $bearer;
    }

    private function event(int $eventId, string $deviceId = 'event-reader', array $overrides = []): void
    {
        DB::table('monitoring_events')->insert(array_replace([
            'device_id' => $deviceId, 'schema_version' => '1.0', 'boot_id' => 'read-boot',
            'event_id' => $eventId, 'linked_alarm_id' => 7, 'source_id' => 1,
            'source_mode' => 'simulation', 'event_type' => 'alarm_ack',
            'occurred_at_ms' => $eventId, 'received_at' => '2026-10-25 01:00:00',
        ], $overrides));
    }

    private function getEvents(string $bearer, string $query = '')
    {
        $response = $this->withToken($bearer)->getJson('/api/v1/device/events'.$query);
        $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
        $this->assertStringContainsString('Authorization', (string) $response->headers->get('Vary'));
        $this->assertStringNotContainsString($bearer, $response->getContent());
        $this->assertStringNotContainsString(hash('sha256', $bearer), $response->getContent());

        return $response;
    }

    public function test_empty_history_is_explicit(): void
    {
        $this->getEvents($this->device())->assertOk()->assertExactJson([
            'device_id' => 'event-reader', 'items' => [], 'next_cursor' => null,
        ]);
    }

    public function test_reads_do_not_refresh_device_or_modify_events(): void
    {
        $bearer = $this->device();
        $this->event(1);
        $before = (array) DB::table('monitoring_events')->first();
        $this->getEvents($bearer)->assertOk();
        $this->assertSame($before, (array) DB::table('monitoring_events')->first());
        $this->assertNull(Device::query()->first()->getRawOriginal('last_seen_at'));
    }

    public function test_authentication_and_disabled_device_fail_closed(): void
    {
        $this->getJson('/api/v1/device/events?cursor=invalid')->assertUnauthorized();
        $this->getEvents(bin2hex(random_bytes(32)))->assertUnauthorized();
        $this->getEvents($this->device(enabled: false))->assertForbidden();
    }

    public function test_foreign_device_and_forged_cursor_cannot_expose_event_rows(): void
    {
        $bearer = $this->device();
        $foreign = $this->device('foreign-reader');
        $this->event(1, 'foreign-reader');
        $this->event(2);
        $this->getEvents($bearer)->assertOk()->assertJsonCount(1, 'items')->assertJsonPath('items.0.event_id', '2');
        $cursor = $this->getEvents($foreign, '?limit=1')->assertOk()->json('items');
        $this->assertSame('foreign-reader', $cursor[0]['device_id']);
        $forged = (new Cursor(['received_at' => '2026-10-25 01:00:00', 'id' => '18446744073709551615']))->encode();
        $this->getEvents($bearer, '?cursor='.$forged)->assertOk()
            ->assertJsonCount(1, 'items')->assertDontSee('foreign-reader');
        $this->getEvents($bearer, '?device_id=foreign-reader')->assertUnprocessable();
    }

    public function test_tied_receipts_paginate_without_duplicates_even_after_new_arrival(): void
    {
        $bearer = $this->device();
        foreach ([1, 2, 3, 4] as $id) {
            $this->event($id);
        }
        $first = $this->getEvents($bearer, '?limit=2')->assertOk()->assertJsonCount(2, 'items');
        $this->assertSame(['4', '3'], array_column($first->json('items'), 'event_id'));
        $this->event(5);
        $second = $this->getEvents($bearer, '?limit=2&cursor='.urlencode($first->json('next_cursor')))
            ->assertOk()->assertJsonPath('next_cursor', null);
        $this->assertSame(['2', '1'], array_column($second->json('items'), 'event_id'));
        // Internal row identifiers and any inferred alarm status are excluded.
        $this->assertSame([
            'schema_version', 'device_id', 'boot_id', 'event_id', 'linked_alarm_id',
            'source_id', 'source_mode', 'event_type', 'occurred_at_ms', 'received_at',
        ], array_keys($second->json('items.0')));
    }

    public function test_receipt_order_does_not_claim_cross_boot_occurrence_order(): void
    {
        $bearer = $this->device();
        $this->event(90, overrides: ['occurred_at_ms' => 9000]);
        $this->event(1, overrides: ['boot_id' => 'new-boot', 'occurred_at_ms' => 0, 'received_at' => '2026-10-25 01:00:01']);
        $this->getEvents($bearer)->assertOk()->assertJsonPath('items.0.boot_id', 'new-boot')
            ->assertJsonPath('items.0.occurred_at_ms', '0')->assertJsonPath('items.1.event_id', '90');
    }

    public function test_filters_remain_device_scoped_and_apply_through_cursor(): void
    {
        $bearer = $this->device();
        $this->device('foreign-reader');
        $this->event(1, overrides: ['source_mode' => 'bench_test']);
        $this->event(2, overrides: ['source_mode' => 'bench_test']);
        $this->event(3, overrides: ['source_mode' => 'bench_test', 'event_type' => 'alarm_cleared']);
        $this->event(4);
        $this->event(5, 'foreign-reader', ['source_mode' => 'bench_test']);
        $query = '?limit=1&event_type=alarm_ack&source_mode=bench_test';
        $first = $this->getEvents($bearer, $query)->assertOk()->assertJsonPath('items.0.event_id', '2');
        $this->getEvents($bearer, $query.'&cursor='.urlencode($first->json('next_cursor')))->assertOk()
            ->assertJsonCount(1, 'items')->assertJsonPath('items.0.event_id', '1')->assertJsonPath('next_cursor', null);
        $this->getEvents($bearer, '?event_type=fault')->assertOk()->assertJsonPath('items', []);
    }

    public function test_default_and_maximum_page_size_are_bounded(): void
    {
        $bearer = $this->device();
        for ($id = 1; $id <= 101; $id++) {
            $this->event($id);
        }
        $this->getEvents($bearer)->assertOk()->assertJsonCount(50, 'items');
        $this->getEvents($bearer, '?limit=100')->assertOk()->assertJsonCount(100, 'items');
        $this->assertDatabaseCount('monitoring_events', 101);
    }

    public function test_uint64_values_remain_exact_decimal_strings_in_json(): void
    {
        $bearer = $this->device();
        $maximum = '18446744073709551615';
        $this->event(1, overrides: ['event_id' => $maximum, 'linked_alarm_id' => $maximum, 'occurred_at_ms' => $maximum, 'source_id' => '4294967295']);
        $this->getEvents($bearer)->assertOk()->assertJsonPath('items.0.event_id', $maximum)
            ->assertJsonPath('items.0.linked_alarm_id', $maximum)->assertJsonPath('items.0.occurred_at_ms', $maximum)
            ->assertJsonPath('items.0.source_id', '4294967295');
    }

    #[DataProvider('invalidQueries')]
    public function test_invalid_query_never_queries_event_table(string $query): void
    {
        $bearer = $this->device();
        DB::enableQueryLog();
        DB::flushQueryLog();
        $this->getEvents($bearer, '?'.$query)->assertUnprocessable();
        $queries = DB::getQueryLog();
        DB::disableQueryLog();
        foreach ($queries as $entry) {
            $this->assertStringNotContainsString('monitoring_events', $entry['query']);
        }
    }

    public static function invalidQueries(): array
    {
        $date = '2026-10-25 01:00:00';
        return [
            ['limit=0'], ['limit=101'], ['limit=-1'], ['limit=1.5'], ['limit[]=1'],
            ['event_type=recovery'], ['event_type[]=alarm_ack'], ['event_type='],
            ['source_mode=physical'], ['source_mode='], ['source_mode[]=simulation'],
            ['cursor='], ['cursor=garbage'], ['cursor[]=garbage'], ['cursor='.str_repeat('a', 2049)],
            ['cursor='.(new Cursor(['id' => 1]))->encode()],
            ['cursor='.(new Cursor(['received_at' => '2026-02-30 01:00:00', 'id' => 1]))->encode()],
            ['cursor='.(new Cursor(['received_at' => $date, 'id' => 0]))->encode()],
            ['cursor='.(new Cursor(['received_at' => $date, 'id' => '18446744073709551616']))->encode()],
            ['cursor='.(new Cursor(['received_at' => $date, 'id' => 1, 'device_id' => 'foreign-reader']))->encode()],
            ['sort=occurred_at_ms'],
        ];
    }
}
