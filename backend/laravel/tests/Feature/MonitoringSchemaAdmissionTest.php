<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\MySqlTestCase;
use Tests\Support\TestSchema;

class MonitoringSchemaAdmissionTest extends MySqlTestCase
{
    use DatabaseTransactions;

    #[DataProvider('newTableRows')]
    public function test_runtime_rows_deny_migration_admission(string $table, array $row): void
    {
        DB::table($table)->insert($row);
        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessage('MYSQL_TEST_BLOCKED: preexisting application rows prohibited.');
        TestSchema::assertMigratedAndEmpty(DB::connection('mysql')->getPdo());
    }

    public static function newTableRows(): array
    {
        return [
            ['cache', ['key' => 'synthetic', 'value' => 'synthetic', 'expiration' => 1]],
            ['cache_locks', ['key' => 'synthetic', 'owner' => 'synthetic', 'expiration' => 1]],
            ['sessions', ['id' => 'synthetic', 'payload' => 'synthetic', 'last_activity' => 1]],
        ];
    }

    public function test_explicit_legacy_upgrade_refuses_already_upgraded_catalog(): void
    {
        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessage('MYSQL_TEST_BLOCKED: expected migrated test schema required.');
        TestSchema::assertMigratedAndEmpty(DB::connection('mysql')->getPdo(), true);
    }
}
