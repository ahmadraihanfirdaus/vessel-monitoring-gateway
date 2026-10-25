<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Tests\MySqlTestCase;

class EventCommitReceiptIntegrationTest extends MySqlTestCase
{
    use DatabaseTransactions;

    private function fixture(): array
    {
        $token = bin2hex(random_bytes(32));
        Device::query()->create(['device_id' => 'receipt:demo', 'token_digest' => hash('sha256', $token), 'enabled' => true]);
        $wire = json_encode(['schema_version' => '1.0', 'device_id' => 'receipt:demo', 'boot_id' => 'receipt-boot',
            'event_id' => 1, 'linked_alarm_id' => 7, 'source_id' => 1, 'source_mode' => 'simulation',
            'event_type' => 'alarm_raised', 'occurred_at_ms' => 0], JSON_THROW_ON_ERROR);

        return [$token, $wire];
    }

    private function send(string $wire, string $token, ?string $version)
    {
        $server = ['HTTP_AUTHORIZATION' => 'Bearer '.$token,
            'CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'];
        if ($version !== null) {
            $server['HTTP_X_VG_EVENT_RECEIPT'] = $version;
        }

        return $this->call('POST', '/api/v1/events', [], [], [], $server, $wire);
    }

    public function test_caller_owned_outer_transaction_refuses_receipt_before_writing_event(): void
    {
        [$token, $wire] = $this->fixture();
        $this->assertGreaterThan(0, DB::transactionLevel());
        $this->send($wire, $token, '1')->assertStatus(503)
            ->assertExactJson(['error' => 'event_receipt_requires_committed_transaction']);
        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_unknown_empty_or_combined_version_rejects_before_persistence(): void
    {
        [$token, $wire] = $this->fixture();
        foreach (['0', '2', '', '1, 1'] as $version) {
            $this->send($wire, $token, $version)->assertBadRequest()
                ->assertExactJson(['error' => 'invalid_event_receipt_version']);
        }
        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_receipt_opt_in_does_not_bypass_authentication_identity_or_schema(): void
    {
        [$token, $wire] = $this->fixture();
        $this->send($wire, 'synthetic-invalid', '1')->assertUnauthorized();
        $foreign = str_replace('receipt:demo', 'other:demo', $wire);
        $this->send($foreign, $token, '1')->assertForbidden();
        $this->send('{}', $token, '1')->assertUnprocessable();
        $this->assertDatabaseCount('monitoring_events', 0);
    }

    public function test_ordinary_ingestion_and_duplicate_json_are_unchanged_without_opt_in(): void
    {
        [$token, $wire] = $this->fixture();
        $this->send($wire, $token, null)->assertCreated()->assertExactJson(['result' => 'event_persisted']);
        $this->send($wire, $token, null)->assertOk()->assertExactJson(['result' => 'identical_event_duplicate']);
        $this->assertDatabaseCount('monitoring_events', 1);
    }
}
