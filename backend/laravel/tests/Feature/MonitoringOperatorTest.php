<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

class MonitoringOperatorTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    public function test_provision_hashes_secret_and_grants_exact_devices_then_revokes_and_disables(): void
    {
        $this->monitoringDevice();
        $secret = bin2hex(random_bytes(20));
        $previous = getenv('VG_MONITORING_PASSWORD');
        putenv('VG_MONITORING_PASSWORD='.$secret);
        try {
            $args = ['email' => 'operator@example.com', '--password-env' => true, '--device' => ['monitor-demo']];
            $this->assertSame(0, Artisan::call('monitoring:operator', $args));
            $this->assertStringNotContainsString($secret, Artisan::output());
            $user = User::query()->firstOrFail();
            $this->assertTrue(Hash::check($secret, $user->password));
            $this->assertNotSame($secret, $user->password);
            $this->assertDatabaseCount('monitoring_device_access', 1);
            $this->assertSame(0, Artisan::call('monitoring:operator', $args));
            $this->assertDatabaseCount('monitoring_device_access', 1);
            $this->assertSame(0, Artisan::call('monitoring:operator', ['email' => $user->email, '--revoke' => ['monitor-demo'], '--disable' => true]));
            $this->assertDatabaseCount('monitoring_device_access', 0);
            $this->assertNotNull(DB::table('users')->value('disabled_at'));
        } finally {
            putenv($previous === false ? 'VG_MONITORING_PASSWORD' : 'VG_MONITORING_PASSWORD='.$previous);
        }
    }

    public function test_invalid_grant_or_missing_password_cannot_partially_provision(): void
    {
        $this->assertSame(1, Artisan::call('monitoring:operator', ['email' => 'operator@example.com', '--no-interaction' => true]));
        $this->assertDatabaseCount('users', 0);
        $previous = getenv('VG_MONITORING_PASSWORD');
        putenv('VG_MONITORING_PASSWORD='.bin2hex(random_bytes(20)));
        try {
            $this->assertSame(1, Artisan::call('monitoring:operator', ['email' => 'operator@example.com', '--password-env' => true, '--device' => ['unknown-demo']]));
            $this->assertDatabaseCount('users', 0);
            $this->assertDatabaseCount('monitoring_device_access', 0);
        } finally {
            putenv($previous === false ? 'VG_MONITORING_PASSWORD' : 'VG_MONITORING_PASSWORD='.$previous);
        }
    }

    public function test_operator_rows_block_migration_admission_in_real_transaction(): void
    {
        $this->operator();
        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessage('MYSQL_TEST_BLOCKED: preexisting application rows prohibited.');
        \Tests\Support\TestSchema::assertMigratedAndEmpty(DB::connection('mysql')->getPdo());
    }

    public function test_password_over_bcrypt_byte_limit_is_rejected_without_partial_account(): void
    {
        $previous = getenv('VG_MONITORING_PASSWORD');
        putenv('VG_MONITORING_PASSWORD='.str_repeat('synthetic', 9));
        try {
            $this->assertSame(1, Artisan::call('monitoring:operator', ['email' => 'operator@example.com', '--password-env' => true]));
            $this->assertDatabaseCount('users', 0);
        } finally {
            putenv($previous === false ? 'VG_MONITORING_PASSWORD' : 'VG_MONITORING_PASSWORD='.$previous);
        }
    }
}
