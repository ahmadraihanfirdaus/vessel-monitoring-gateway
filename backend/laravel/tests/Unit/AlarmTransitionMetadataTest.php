<?php

namespace Tests\Unit;

use App\Support\AlarmTransitionMetadata as Metadata;
use PHPUnit\Framework\TestCase;

class AlarmTransitionMetadataTest extends TestCase
{
    private function raised(): array
    {
        return ['priority_code' => 3, 'reason_code' => 1001, 'state' => 'active_unack',
            'raised_at_ms' => 0, 'acknowledged_at_ms' => null, 'cleared_at_ms' => null];
    }

    public function test_zero_lifecycle_times_are_distinct_from_absent_times(): void
    {
        $alarm = $this->raised();
        $this->assertTrue(Metadata::consistent($alarm, 'alarm_raised', '0'));
        $this->assertFalse(Metadata::consistent($alarm, 'alarm_ack', '0'));
        $alarm['state'] = 'active_ack';
        $alarm['acknowledged_at_ms'] = 0;
        $this->assertTrue(Metadata::consistent($alarm, 'alarm_ack', '0'));
        $this->assertFalse(Metadata::consistent($alarm, 'alarm_cleared', '0'));
        $this->assertNull($alarm['cleared_at_ms']);
        $alarm['state'] = 'cleared';
        $alarm['cleared_at_ms'] = 0;
        $this->assertTrue(Metadata::consistent($alarm, 'alarm_cleared', '0'));
        $this->assertSame('0', Metadata::canonical($alarm)['acknowledged_at_ms']);
        $this->assertSame('0', Metadata::canonical($alarm)['cleared_at_ms']);
    }

    public function test_uint64_order_and_action_correspondence_do_not_use_float_comparison(): void
    {
        $alarm = $this->raised();
        $alarm['raised_at_ms'] = '18446744073709551613';
        $alarm['acknowledged_at_ms'] = '18446744073709551614';
        $alarm['cleared_at_ms'] = '18446744073709551615';
        $alarm['state'] = 'cleared';
        $this->assertTrue(Metadata::consistent($alarm, 'alarm_cleared', '18446744073709551615'));
        $this->assertFalse(Metadata::consistent($alarm, 'alarm_cleared', '18446744073709551614'));
        $alarm['cleared_at_ms'] = '18446744073709551613';
        $this->assertFalse(Metadata::consistent($alarm, 'alarm_cleared', '18446744073709551613'));
        $alarm['cleared_at_ms'] = '18446744073709551616';
        $this->assertFalse(Metadata::consistent($alarm, 'alarm_cleared', '18446744073709551616'));
    }

    public function test_malformed_or_inconsistent_facts_are_rejected_and_key_order_is_canonical(): void
    {
        foreach (['fault', 'recovery', '', 'alarm_ack', 'alarm_cleared'] as $type) {
            $this->assertFalse(Metadata::consistent($this->raised(), $type, '0'));
        }
        foreach (['priority_code' => 0, 'reason_code' => '4294967296', 'raised_at_ms' => null,
            'acknowledged_at_ms' => 1, 'cleared_at_ms' => 1, 'state' => 'cleared'] as $key => $value) {
            $alarm = $this->raised();
            $alarm[$key] = $value;
            $this->assertFalse(Metadata::consistent($alarm, 'alarm_raised', '0'));
        }
        $alarm = $this->raised();
        $alarm['unknown'] = 1;
        $this->assertFalse(Metadata::consistent($alarm, 'alarm_raised', '0'));
        $this->assertSame(Metadata::canonical($this->raised()), Metadata::canonical(array_reverse($this->raised(), true)));
        $this->assertSame('0', Metadata::canonical($this->raised())['raised_at_ms']);
        $this->assertNull(Metadata::canonical($this->raised())['acknowledged_at_ms']);
    }
}
