<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\EventIngestRequest;
use App\Models\Device;
use App\Support\DependencyUnavailableResponse;
use App\Support\EventCommitReceipt;
use Illuminate\Database\QueryException;
use App\Services\EventIngestService;
use Illuminate\Support\Facades\DB;
use Symfony\Component\HttpFoundation\Response;

class EventIngestController extends Controller
{
    public function __construct(
        private readonly EventIngestService $service
    ) {
    }

    public function __invoke(EventIngestRequest $request): Response
    {
        $device = $request->attributes->get('authenticated_device');

        if (! $device instanceof Device) {
            return response()->json([
                'error' => 'invalid_device_authentication',
            ], 401);
        }

        $payload = $request->validated();

        if ((string) $payload['device_id'] !== $device->device_id) {
            return response()->json([
                'error' => 'device_identity_mismatch',
            ], 403);
        }

        $receiptRequested = $request->headers->has(EventCommitReceipt::HEADER);
        if ($receiptRequested && $request->headers->all(strtolower(EventCommitReceipt::HEADER)) !== ['1']) {
            return response()->json(['error' => 'invalid_event_receipt_version'], 400);
        }
        // Signing a savepoint release would falsely confirm a transaction that
        // its caller can still roll back. Refuse before any event write.
        if ($receiptRequested && DB::transactionLevel() !== 0) {
            return response()->json(['error' => 'event_receipt_requires_committed_transaction'], 503);
        }

        try {
            $result = $this->service->ingest($device, $payload);
        } catch (QueryException $exception) {
            $response = DependencyUnavailableResponse::forConnectionFailure($exception);
            if ($response !== null) {
                return $response;
            }
            throw $exception;
        }

        if (! $receiptRequested || ! in_array($result['status'], [200, 201], true)) {
            return response()->json($result['body'], $result['status']);
        }
        $bearer = $request->bearerToken();
        $receipt = DB::transactionLevel() === 0 && is_string($bearer)
            && in_array($result['body']['result'] ?? null, ['event_persisted', 'identical_event_duplicate'], true)
            ? EventCommitReceipt::issue($request->getContent(), $bearer, $result['status']) : null;
        if ($receipt === null) {
            return response()->json(['error' => 'event_receipt_unavailable'], 503);
        }

        return response($receipt, $result['status'])->header('Content-Type', EventCommitReceipt::CONTENT_TYPE);
    }
}
