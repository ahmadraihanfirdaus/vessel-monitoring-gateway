<?php

namespace Tests\Unit;

use App\Support\EventCommitReceipt;
use PHPUnit\Framework\TestCase;

class EventCommitReceiptTest extends TestCase
{
    public function test_fixed_receipt_binds_exact_bytes_status_and_authentication_input(): void
    {
        $bearer = bin2hex(random_bytes(32));
        $wire = '{"synthetic":1}';
        $receipt = EventCommitReceipt::issue($wire, $bearer, 201);
        $this->assertIsString($receipt);
        $this->assertSame(134, strlen($receipt));
        $this->assertMatchesRegularExpression('/\AVGR1:[a-f0-9]{64}:[a-f0-9]{64}\z/', $receipt);
        $this->assertSame(hash('sha256', $wire), explode(':', $receipt)[1]);
        $this->assertStringNotContainsString($bearer, $receipt);
        $this->assertNotSame($receipt, EventCommitReceipt::issue($wire.' ', $bearer, 201));
        $this->assertNotSame($receipt, EventCommitReceipt::issue($wire, $bearer, 200));
        $this->assertSame($receipt, EventCommitReceipt::issue($wire, $bearer, 201));
    }

    public function test_invalid_size_key_or_status_cannot_issue_a_receipt(): void
    {
        $bearer = bin2hex(random_bytes(32));
        foreach ([['', $bearer, 201], [str_repeat('x', 4097), $bearer, 201],
            ['body', str_repeat('x', 31), 201], ['body', str_repeat('x', 257), 201],
            ['body', $bearer, 0], ['body', $bearer, 202], ['body', $bearer, 409]] as $input) {
            $this->assertNull(EventCommitReceipt::issue(...$input));
        }
        $this->assertSame(134, strlen(EventCommitReceipt::issue(str_repeat('x', 4096), str_repeat('x', 32), 201)));
        $this->assertSame(134, strlen(EventCommitReceipt::issue('body', str_repeat('x', 256), 200)));
    }

    public function test_stored_token_digest_is_not_an_equivalent_signing_key(): void
    {
        $bearer = bin2hex(random_bytes(32));
        $this->assertNotSame(EventCommitReceipt::issue('body', $bearer, 201),
            EventCommitReceipt::issue('body', hash('sha256', $bearer), 201));
    }
}
