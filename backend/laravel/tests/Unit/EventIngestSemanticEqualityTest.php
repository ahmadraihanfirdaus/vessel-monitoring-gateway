<?php

namespace Tests\Unit;

use App\Models\MonitoringEvent;
use App\Services\EventIngestService;
use App\Support\AlarmTransitionMetadata;
use PHPUnit\Framework\TestCase;
use ReflectionMethod;

class EventIngestSemanticEqualityTest extends TestCase
{
    private function payload(): array
    {
        return ['device_id' => 'order:fixture', 'schema_version' => '1.1', 'boot_id' => 'order-boot',
            'event_id' => '18446744073709551615', 'linked_alarm_id' => '18446744073709551615',
            'source_id' => 4294967295, 'source_mode' => 'bench_test', 'event_type' => 'alarm_ack',
            'occurred_at_ms' => '18446744073709551615', 'alarm' => [
                'priority_code' => 4294967295, 'reason_code' => 1001, 'state' => 'active_ack',
                'raised_at_ms' => '0', 'acknowledged_at_ms' => '18446744073709551615', 'cleared_at_ms' => null]];
    }

    private function identical(mixed $stored, ?array $payload = null): bool
    {
        $payload ??= $this->payload();
        $event = new MonitoringEvent;
        $attributes = $payload;
        unset($attributes['alarm']);
        // Exercise the actual Eloquent JSON cast, with no database substitute.
        $attributes['alarm_metadata'] = $stored === null ? null : json_encode($stored, JSON_THROW_ON_ERROR);
        $event->setRawAttributes($attributes, true);

        return (new ReflectionMethod(EventIngestService::class, 'semanticallyEqual'))
            ->invoke(new EventIngestService, $event, $payload);
    }

    public function test_all_persisted_json_key_permutations_replay_identically_without_value_coercion(): void
    {
        $expected = AlarmTransitionMetadata::canonical($this->payload()['alarm']);
        $count = 0;
        $visit = function (array $remaining, array $ordered) use (&$visit, &$count): void {
            if ($remaining === []) {
                $this->assertTrue($this->identical($ordered));
                $count++;

                return;
            }
            foreach ($remaining as $key => $value) {
                $rest = $remaining;
                unset($rest[$key]);
                $visit($rest, $ordered + [$key => $value]);
            }
        };
        $visit($expected, []);
        $this->assertSame(720, $count);
    }

    public function test_missing_extra_malformed_and_type_changed_persisted_facts_remain_conflicts(): void
    {
        $expected = AlarmTransitionMetadata::canonical($this->payload()['alarm']);
        $this->assertTrue($this->identical($expected));
        foreach ($expected as $key => $value) {
            $missing = $expected;
            unset($missing[$key]);
            $this->assertFalse($this->identical($missing));
            if (is_int($value)) {
                $quoted = $expected;
                $quoted[$key] = (string) $value;
                $this->assertFalse($this->identical($quoted));
            }
            foreach ([null, false, true, 0, '0', 1.0, [], 'changed'] as $changed) {
                if ($changed === $value) {
                    continue;
                }
                $altered = $expected;
                $altered[$key] = $changed;
                $this->assertFalse($this->identical($altered));
            }
        }
        $this->assertFalse($this->identical($expected + ['unknown' => null]));
        foreach ([null, [], 'not-an-object', 0, false] as $malformed) {
            $this->assertFalse($this->identical($malformed));
        }
        $legacy = $this->payload();
        $legacy['schema_version'] = '1.0';
        unset($legacy['alarm']);
        $this->assertTrue($this->identical(null, $legacy));
        $this->assertFalse($this->identical($expected, $legacy));
    }
}
