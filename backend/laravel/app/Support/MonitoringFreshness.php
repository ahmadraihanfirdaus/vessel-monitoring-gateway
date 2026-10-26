<?php

namespace App\Support;

use Carbon\CarbonImmutable;

final class MonitoringFreshness
{
    /** Conservative browser display budget; receipt chronology remains server-owned. */
    public static function display(?string $receivedAt, CarbonImmutable $now, mixed $stale, mixed $offline): array
    {
        $result = self::classify($receivedAt, $now, $stale, $offline);
        $result += ['age_ms' => null, 'stale_ms' => null, 'offline_ms' => null];
        // Largest integral seconds whose milliseconds fit JavaScript's exact integer domain.
        $limit = 9007199254740;
        if ($result['age_seconds'] !== null && $result['age_seconds'] <= $limit
            && (int) $stale <= $limit && (int) $offline <= $limit) {
            $age = $result['age_seconds'] * 1000 + (int) ceil((int) $now->format('u') / 1000);
            if ($age <= 9007199254740991) {
                $result['age_ms'] = $age;
                $result['stale_ms'] = (int) $stale * 1000;
                $result['offline_ms'] = (int) $offline * 1000;
            }
        }

        return $result;
    }

    public static function classify(?string $receivedAt, CarbonImmutable $now, mixed $stale, mixed $offline): array
    {
        if ((! is_int($stale) && ! is_string($stale)) || (! is_int($offline) && ! is_string($offline))) {
            return ['label' => 'UNKNOWN', 'reason' => 'FRESHNESS POLICY NOT CONFIGURED', 'age_seconds' => null];
        }
        $stale = filter_var($stale, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]]);
        $offline = filter_var($offline, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]]);
        if ($stale === false || $offline === false || $offline <= $stale) {
            return ['label' => 'UNKNOWN', 'reason' => 'FRESHNESS POLICY NOT CONFIGURED', 'age_seconds' => null];
        }
        if ($receivedAt === null) {
            return ['label' => 'OFFLINE', 'reason' => 'NO RECEIPT', 'age_seconds' => null];
        }
        try {
            $time = CarbonImmutable::createFromFormat('!Y-m-d H:i:s', $receivedAt, 'UTC');
            if ($time === false || $time->format('Y-m-d H:i:s') !== $receivedAt) {
                throw new \InvalidArgumentException();
            }
            $age = $now->getTimestamp() - $time->getTimestamp();
            if ($age < 0) {
                throw new \InvalidArgumentException();
            }
        } catch (\Throwable) {
            return ['label' => 'UNKNOWN', 'reason' => 'INVALID OR FUTURE RECEIPT', 'age_seconds' => null];
        }

        return ['label' => $age >= $offline ? 'OFFLINE' : ($age >= $stale ? 'STALE' : 'LIVE'),
            'reason' => 'SERVER RECEIPT AGE', 'age_seconds' => $age];
    }
}
