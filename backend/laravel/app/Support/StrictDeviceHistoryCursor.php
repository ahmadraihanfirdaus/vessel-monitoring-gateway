<?php

namespace App\Support;

use Illuminate\Pagination\Cursor;

/** Validate Laravel cursor shape for the actual (received_at DESC, id DESC) query. */
final class StrictDeviceHistoryCursor
{
    public static function isValid(string $encoded): bool
    {
        try {
            $cursor = Cursor::fromEncoded($encoded);
        } catch (\Throwable) {
            return false;
        }

        if ($cursor === null || $cursor->encode() !== $encoded) {
            return false;
        }

        // Cursor::parameters() requires explicit names and discards extras.
        // toArray() lets us reject additional forged ordering fields.
        $parameters = $cursor->toArray();
        if (array_keys($parameters) !== ['received_at', 'id', '_pointsToNextItems']
            || ! is_bool($parameters['_pointsToNextItems'])) {
            return false;
        }

        $receivedAt = $parameters['received_at'];
        if (! is_string($receivedAt)
            || preg_match('/\A[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\z/', $receivedAt) !== 1) {
            return false;
        }

        $parsed = \DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $receivedAt);
        if ($parsed === false || $parsed->format('Y-m-d H:i:s') !== $receivedAt) {
            return false;
        }

        $id = $parameters['id'];
        if (! is_int($id) && ! is_string($id)) {
            return false;
        }

        $decimal = (string) $id;
        if (preg_match('/\A[1-9][0-9]*\z/', $decimal) !== 1) {
            return false;
        }

        // Database identifiers are unsigned BIGINT; never cast to float/int.
        $maximum = '18446744073709551615';
        return strlen($decimal) < strlen($maximum)
            || (strlen($decimal) === strlen($maximum) && strcmp($decimal, $maximum) <= 0);
    }
}
