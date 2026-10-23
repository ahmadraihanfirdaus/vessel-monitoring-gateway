<?php

namespace App\Support;

use Illuminate\Database\QueryException;
use Illuminate\Http\JsonResponse;

/** Sanitize only recognizable transport/database availability failures. */
final class DependencyUnavailableResponse
{
    public static function forConnectionFailure(QueryException $exception): ?JsonResponse
    {
        // A QueryException can also be bad SQL or an integrity violation.
        // Such programming/data errors must not be disguised as transient 503s.
        $code = (string) $exception->getCode();
        $driverCode = (string) ($exception->errorInfo[1] ?? '');
        $sqlState = (string) ($exception->errorInfo[0] ?? '');

        $connectCodes = ['2002', '2003', '2006', '2013', '2055'];
        if (! in_array($code, $connectCodes, true)
            && ! in_array($driverCode, $connectCodes, true)
            && preg_match('/\A08[A-Z0-9]{3}\z/', $sqlState) !== 1) {
            return null;
        }

        return response()->json([
            'error' => 'backend_temporarily_unavailable',
        ], 503)->header('Retry-After', '5');
    }
}
