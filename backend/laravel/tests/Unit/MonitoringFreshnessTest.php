<?php

namespace Tests\Unit;

use App\Support\MonitoringFreshness;
use Carbon\CarbonImmutable;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

class MonitoringFreshnessTest extends TestCase
{
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
