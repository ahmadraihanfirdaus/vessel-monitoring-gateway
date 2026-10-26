<?php

namespace Tests\Unit;

use App\Support\MonitoringFreshness;
use Carbon\CarbonImmutable;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

class MonitoringFreshnessTest extends TestCase
{
    public function test_browser_deadlines_round_up_fraction_without_changing_server_classification(): void
    {
        $now = CarbonImmutable::parse('2026-10-25 12:00:01.999001', 'UTC');
        $result = MonitoringFreshness::display('2026-10-25 12:00:00', $now, 2, 4);
        $this->assertSame('LIVE', $result['label']);
        $this->assertSame(1, $result['age_seconds']);
        $this->assertSame(2000, $result['age_ms']);
        $this->assertSame(2000, $result['stale_ms']);
        $this->assertSame(4000, $result['offline_ms']);
    }

    public function test_unsafe_browser_policy_preserves_explicit_server_snapshot_without_deadlines(): void
    {
        $now = CarbonImmutable::parse('2026-10-25 12:00:00', 'UTC');
        foreach ([[1, PHP_INT_MAX], [null, null], [1, 1], ['bad', 4]] as [$stale, $offline]) {
            $result = MonitoringFreshness::display('2026-10-25 12:00:00', $now, $stale, $offline);
            $this->assertNull($result['age_ms']);
            $this->assertNull($result['stale_ms']);
            $this->assertNull($result['offline_ms']);
        }
        $this->assertSame('LIVE', MonitoringFreshness::display('2026-10-25 12:00:00', $now, 1, PHP_INT_MAX)['label']);
    }

    public function test_missing_and_future_receipts_have_no_browser_live_budget(): void
    {
        $now = CarbonImmutable::parse('2026-10-25 12:00:00', 'UTC');
        foreach ([null, '2026-10-25 12:00:01'] as $receipt) {
            $result = MonitoringFreshness::display($receipt, $now, 2, 4);
            $this->assertNull($result['age_ms']);
            $this->assertContains($result['label'], ['OFFLINE', 'UNKNOWN']);
        }
    }

    #[DataProvider('cases')]
    public function test_freshness_boundaries_and_invalid_policy(?string $time, mixed $stale, mixed $offline, string $label, ?int $age): void
    {
        $result = MonitoringFreshness::classify($time, CarbonImmutable::parse('2026-10-25 12:00:00', 'UTC'), $stale, $offline);
        $this->assertSame($label, $result['label']);
        $this->assertSame($age, $result['age_seconds']);
        $this->assertNotEmpty($result['reason']);
    }

    public static function cases(): array
    {
        // Test-oracle intervals only; no engineering deployment threshold.
        return [
            [null, null, null, 'UNKNOWN', null], [null, 10, 30, 'OFFLINE', null],
            ['2026-10-25 12:00:00', 10, 30, 'LIVE', 0],
            ['2026-10-25 11:59:51', 10, 30, 'LIVE', 9],
            ['2026-10-25 11:59:50', 10, 30, 'STALE', 10],
            ['2026-10-25 11:59:31', '10', '30', 'STALE', 29],
            ['2026-10-25 11:59:30', 10, 30, 'OFFLINE', 30],
            ['2026-10-25 12:00:01', 10, 30, 'UNKNOWN', null],
            ['2026-02-30 00:00:00', 10, 30, 'UNKNOWN', null],
            ['', 10, 30, 'UNKNOWN', null], ['tomorrow', 10, 30, 'UNKNOWN', null],
            [null, 0, 30, 'UNKNOWN', null], [null, 10, 10, 'UNKNOWN', null],
            [null, 30, 10, 'UNKNOWN', null], [null, -1, 30, 'UNKNOWN', null],
            [null, '1e1', 30, 'UNKNOWN', null], [null, [], 30, 'UNKNOWN', null],
            [null, 1.5, 30, 'UNKNOWN', null], [null, true, 30, 'UNKNOWN', null],
        ];
    }
}
