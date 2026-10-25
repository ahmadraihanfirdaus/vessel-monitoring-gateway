<?php

namespace App\Support;

/** Validated schema 1.1 alarm facts. All times are boot-relative milliseconds. */
final class AlarmTransitionMetadata
{
    public const FIELDS = ['priority_code', 'reason_code', 'state', 'raised_at_ms', 'acknowledged_at_ms', 'cleared_at_ms'];

    private static function compare(string $a, string $b): int
    {
        return strlen($a) <=> strlen($b) ?: strcmp($a, $b);
    }

    public static function consistent(array $alarm, string $type, string $occurred): bool
    {
        // No casts of uint64 times to float/int. Range/lexical checks belong to
        // request admission; keep this guard safe on malformed internal callers.
        if (count($alarm) !== count(self::FIELDS) || array_diff(array_keys($alarm), self::FIELDS) !== []) {
            return false;
        }
        foreach (['priority_code', 'reason_code'] as $field) {
            if ((! is_int($alarm[$field] ?? null) && ! is_string($alarm[$field] ?? null))
                || preg_match('/\A[1-9][0-9]*\z/', (string) $alarm[$field]) !== 1
                || self::compare((string) $alarm[$field], '4294967295') > 0) {
                return false;
            }
        }
        foreach (['raised_at_ms', 'acknowledged_at_ms', 'cleared_at_ms'] as $field) {
            if (! array_key_exists($field, $alarm)) {
                return false;
            }
            if ($alarm[$field] !== null && ((! is_int($alarm[$field]) && ! is_string($alarm[$field]))
                || preg_match('/\A(?:0|[1-9][0-9]*)\z/', (string) $alarm[$field]) !== 1
                || self::compare((string) $alarm[$field], '18446744073709551615') > 0)) {
                return false;
            }
        }
        if ($alarm['raised_at_ms'] === null || preg_match('/\A(?:0|[1-9][0-9]*)\z/', $occurred) !== 1
            || self::compare($occurred, '18446744073709551615') > 0) {
            return false;
        }
        $raised = (string) $alarm['raised_at_ms'];
        $ack = $alarm['acknowledged_at_ms'] === null ? null : (string) $alarm['acknowledged_at_ms'];
        $clear = $alarm['cleared_at_ms'] === null ? null : (string) $alarm['cleared_at_ms'];
        if (self::compare($raised, $occurred) > 0 || ($ack !== null && self::compare($ack, $raised) < 0)
            || ($clear !== null && (self::compare($clear, $raised) < 0
                || ($ack !== null && self::compare($clear, $ack) < 0)))) {
            return false;
        }

        return match ($type) {
            'alarm_raised' => ($alarm['state'] ?? null) === 'active_unack'
                && $ack === null && $clear === null && $occurred === $raised,
            'alarm_ack' => ($alarm['state'] ?? null) === 'active_ack'
                && $ack !== null && $clear === null && $occurred === $ack,
            'alarm_cleared' => ($alarm['state'] ?? null) === 'cleared'
                && $clear !== null && $occurred === $clear,
            default => false,
        };
    }

    /** Stable persistence/read representation independent of input key order. */
    public static function canonical(array $alarm): array
    {
        return [
            'priority_code' => (int) $alarm['priority_code'], 'reason_code' => (int) $alarm['reason_code'],
            'state' => $alarm['state'], 'raised_at_ms' => (string) $alarm['raised_at_ms'],
            'acknowledged_at_ms' => $alarm['acknowledged_at_ms'] === null ? null : (string) $alarm['acknowledged_at_ms'],
            'cleared_at_ms' => $alarm['cleared_at_ms'] === null ? null : (string) $alarm['cleared_at_ms'],
        ];
    }
}
