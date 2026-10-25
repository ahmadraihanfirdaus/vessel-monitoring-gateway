<?php

namespace App\Support;

/** Opt-in exact-body confirmation; caller must establish committed/authenticated context. */
final class EventCommitReceipt
{
    public const HEADER = 'X-VG-Event-Receipt';
    public const CONTENT_TYPE = 'application/vnd.vgw.event-receipt-v1';
    public const LENGTH = 134;

    public static function issue(string $wire, string $bearer, int $status): ?string
    {
        if (strlen($wire) < 1 || strlen($wire) > 4096 || strlen($bearer) < 32 || strlen($bearer) > 256
            || ! in_array($status, [200, 201], true)) {
            return null;
        }
        $digest = hash('sha256', $wire);
        // Use the actual authenticated bearer, never its stored token digest.
        $mac = hash_hmac('sha256', "VG_EVENT_COMMIT_V1\n{$status}\n{$digest}", $bearer);

        return 'VGR1:'.$digest.':'.$mac;
    }
}
