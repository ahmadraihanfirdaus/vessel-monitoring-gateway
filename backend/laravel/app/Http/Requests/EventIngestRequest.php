<?php

namespace App\Http\Requests;

use App\Support\AlarmTransitionMetadata;
use App\Support\InspectsRawJsonObjects;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Validator;
use JsonException;

class EventIngestRequest extends FormRequest
{
    use InspectsRawJsonObjects;

    private const UINT64_MAX = '18446744073709551615';
    private const UINT32_MAX = '4294967295';

    private const ALLOWED_FIELDS = [
        'schema_version',
        'device_id',
        'boot_id',
        'event_id',
        'linked_alarm_id',
        'source_id',
        'source_mode',
        'event_type',
        'occurred_at_ms',
    ];

    public function authorize(): bool
    {
        return true;
    }

    protected function prepareForValidation(): void
    {
        $raw = $this->getContent();

        if ($raw === '') {
            return;
        }

        try {
            $decoded = json_decode(
                $raw,
                true,
                512,
                JSON_THROW_ON_ERROR | JSON_BIGINT_AS_STRING
            );
        } catch (JsonException) {
            return;
        }

        if (is_array($decoded) && ! array_is_list($decoded)) {
            $this->replace($decoded);
        }
    }

    public function rules(): array
    {
        $rules = [
            'schema_version' => ['required', 'string', 'in:1.0,1.1'],
            'device_id' => [
                'required',
                'string',
                'max:48',
                'regex:/\A[A-Za-z0-9._:-]+\z/',
            ],
            'boot_id' => [
                'required',
                'string',
                'max:48',
                'regex:/\A[A-Za-z0-9._:-]+\z/',
            ],
            'event_id' => [
                'required',
                $this->unsignedDecimalRule(self::UINT64_MAX, $this->input('schema_version') !== '1.1'),
            ],
            'linked_alarm_id' => [
                'required',
                $this->unsignedDecimalRule(self::UINT64_MAX, $this->input('schema_version') !== '1.1'),
            ],
            'source_id' => [
                'required',
                $this->unsignedDecimalRule(self::UINT32_MAX, false),
            ],
            'source_mode' => [
                'required',
                'string',
                'in:simulation,bench_test',
            ],
            'event_type' => [
                'required',
                'string',
                'in:alarm_raised,alarm_ack,alarm_cleared,fault',
            ],
            'occurred_at_ms' => [
                'required',
                $this->unsignedDecimalRule(self::UINT64_MAX, true),
            ],
        ];
        if ($this->input('schema_version') === '1.1') {
            $rules += [
                'alarm' => ['required', 'array:'.implode(',', AlarmTransitionMetadata::FIELDS)],
                'alarm.priority_code' => ['required', $this->unsignedDecimalRule(self::UINT32_MAX, false)],
                'alarm.reason_code' => ['required', $this->unsignedDecimalRule(self::UINT32_MAX, false)],
                'alarm.state' => ['required', 'string', 'in:active_unack,active_ack,cleared'],
                'alarm.raised_at_ms' => ['required', $this->unsignedDecimalRule(self::UINT64_MAX, true)],
                'alarm.acknowledged_at_ms' => ['present', 'nullable', $this->unsignedDecimalRule(self::UINT64_MAX, true)],
                'alarm.cleared_at_ms' => ['present', 'nullable', $this->unsignedDecimalRule(self::UINT64_MAX, true)],
            ];
        }

        return $rules;
    }

    public function withValidator(Validator $validator): void
    {
        $validator->after(function (Validator $validator): void {
            try {
                $decoded = json_decode($this->getContent(), true, 512, JSON_THROW_ON_ERROR | JSON_BIGINT_AS_STRING);
            } catch (JsonException) {
                $validator->errors()->add('payload', 'Request body must be valid JSON.');
                return;
            }
            if (! is_array($decoded) || array_is_list($decoded)) {
                $validator->errors()->add('payload', 'Request body must be a JSON object.');
                return;
            }
            $complete = $this->input('schema_version') === '1.1';
            $allowed = $complete ? [...self::ALLOWED_FIELDS, 'alarm'] : self::ALLOWED_FIELDS;
            if (array_diff(array_keys($decoded), $allowed) !== []) {
                $validator->errors()->add('payload', 'Unknown event payload field is not allowed.');
            }
            $members = $this->parseRawObjectMembers($this->getContent());
            if ($members === null) {
                $validator->errors()->add('payload', 'Event JSON structure cannot be inspected safely.');
                return;
            }
            $this->assertExactMembers($validator, $members, $allowed, '');
            foreach (['event_id' => ! $complete, 'linked_alarm_id' => ! $complete,
                'source_id' => false, 'occurred_at_ms' => true] as $field => $allowZero) {
                $this->assertUnsignedMember($validator, $members, $field, $allowZero);
            }
            if (! $complete) {
                return;
            }
            $alarmMembers = array_values(array_filter($members, static fn ($m) => $m['key'] === 'alarm'));
            $alarm = count($alarmMembers) === 1 ? $this->parseRawObjectMembers(trim($alarmMembers[0]['value'])) : null;
            if ($alarm === null) {
                $validator->errors()->add('alarm', 'Alarm must be one JSON object.');
                return;
            }
            $this->assertExactMembers($validator, $alarm, AlarmTransitionMetadata::FIELDS, 'alarm.');
            foreach (['priority_code', 'reason_code', 'raised_at_ms', 'acknowledged_at_ms', 'cleared_at_ms'] as $field) {
                $this->assertUnsignedMember($validator, $alarm, $field,
                    ! in_array($field, ['priority_code', 'reason_code'], true),
                    in_array($field, ['acknowledged_at_ms', 'cleared_at_ms'], true), 'alarm.');
            }
            if ($validator->errors()->isEmpty() && ! AlarmTransitionMetadata::consistent(
                $this->input('alarm'), $this->input('event_type'), (string) $this->input('occurred_at_ms'))) {
                $validator->errors()->add('alarm', 'Alarm state and lifecycle times must match this event transition.');
            }
        });
    }

    private function unsignedDecimalRule(
        string $max,
        bool $allowZero
    ): \Closure {
        return static function (
            string $attribute,
            mixed $value,
            \Closure $fail
        ) use ($max, $allowZero): void {
            if (is_int($value)) {
                if ($value < 0 || (! $allowZero && $value === 0)) {
                    $fail("The {$attribute} field must be an unsigned integer.");
                    return;
                }
                $decimal = (string) $value;
            } elseif (
                is_string($value)
                && preg_match('/\A(?:0|[1-9][0-9]*)\z/', $value) === 1
            ) {
                if (! $allowZero && $value === '0') {
                    $fail("The {$attribute} field must be greater than zero.");
                    return;
                }
                $decimal = ltrim($value, '0');
                $decimal = $decimal === '' ? '0' : $decimal;
            } else {
                $fail("The {$attribute} field must be an unsigned integer.");
                return;
            }

            if (
                strlen($decimal) > strlen($max)
                || (
                    strlen($decimal) === strlen($max)
                    && strcmp($decimal, $max) > 0
                )
            ) {
                $fail("The {$attribute} field exceeds its allowed range.");
            }
        };
    }

    /** Exact decoded key names reject escaped duplicates at the current object level. */
    private function assertExactMembers(Validator $validator, array $members, array $allowed, string $prefix): void
    {
        $counts = [];
        foreach ($members as $member) {
            $counts[$member['key']] = ($counts[$member['key']] ?? 0) + 1;
            if (! in_array($member['key'], $allowed, true)) {
                $validator->errors()->add($prefix.'payload', 'Unknown event object field is not allowed.');
            }
        }
        foreach ($allowed as $field) {
            if (($counts[$field] ?? 0) !== 1) {
                $validator->errors()->add($prefix.$field, $field.' must be encoded exactly once.');
            }
        }
    }

    private function assertUnsignedMember(Validator $validator, array $members, string $field,
        bool $allowZero, bool $nullable = false, string $prefix = ''): void
    {
        $found = array_values(array_filter($members, static fn ($m) => $m['key'] === $field));
        if (count($found) !== 1) {
            return; // Exact-member inspection reports the missing/duplicate field.
        }
        $raw = trim($found[0]['value']);
        if ($nullable && $raw === 'null') {
            return;
        }
        $pattern = $allowZero ? '/\A(?:0|[1-9][0-9]*)\z/' : '/\A[1-9][0-9]*\z/';
        if (preg_match($pattern, $raw) !== 1) {
            $validator->errors()->add($prefix.$field, $field.' must be an unquoted unsigned JSON integer.');
        }
    }
}
