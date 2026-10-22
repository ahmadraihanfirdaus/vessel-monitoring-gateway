<?php
namespace App\Support;

/** Phase 9 UI-001: label only. Upstream decides freshness; no invented age thresholds. */
final class DashboardSignalLabel
{
    public static function labels(string $freshness, string $sourceMode): array
    {
        $labels = [
            'live' => 'LIVE',
            'stale' => 'STALE',
            'offline' => 'OFFLINE',
        ];
        $source = [
            'simulation' => 'SIMULATION',
            'bench_test' => 'BENCH TEST',
            'physical' => 'PHYSICAL',
        ];
        return [
            'freshness' => $labels[$freshness] ?? 'UNKNOWN',
            'source_mode' => $source[$sourceMode] ?? 'UNKNOWN',
        ];
    }
}
