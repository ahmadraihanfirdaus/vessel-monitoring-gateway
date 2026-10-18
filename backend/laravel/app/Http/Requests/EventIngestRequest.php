<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Validator;
use JsonException;

class EventIngestRequest extends FormRequest
{
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
        return [
            'schema_version' => ['required', 'string', 'in:1.0'],
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
                $this->unsignedDecimalRule(self::UINT64_MAX, true),
            ],
            'linked_alarm_id' => [
                'required',
                $this->unsignedDecimalRule(self::UINT64_MAX, true),
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
    }

    public function withValidator(Validator $validator): void
    {
        $validator->after(function (Validator $validator): void {
            $raw = $this->getContent();

            try {
                $decoded = json_decode(
                    $raw,
                    true,
                    512,
                    JSON_THROW_ON_ERROR | JSON_BIGINT_AS_STRING
                );
            } catch (JsonException) {
                $validator->errors()->add(
                    'payload',
                    'Request body must be valid JSON.'
                );

                return;
            }

            if (! is_array($decoded) || array_is_list($decoded)) {
                $validator->errors()->add(
                    'payload',
                    'Request body must be a JSON object.'
                );

                return;
            }

            $unknown = array_diff(array_keys($decoded), self::ALLOWED_FIELDS);

            if ($unknown !== []) {
                $validator->errors()->add(
                    'payload',
                    'Unknown event payload field is not allowed.'
                );
            }

            foreach (self::ALLOWED_FIELDS as $field) {
                if ($this->rawKeyCount($raw, $field) !== 1) {
                    $validator->errors()->add(
                        $field,
                        "{$field} must be encoded exactly once."
                    );
                }
            }

            foreach (
                [
                    'event_id' => true,
                    'linked_alarm_id' => true,
                    'source_id' => false,
                    'occurred_at_ms' => true,
                ] as $field => $allowZero
            ) {
                $this->assertRawUnsignedInteger(
                    $validator,
                    $raw,
                    $field,
                    $allowZero
                );
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

    private function rawKeyCount(string $raw, string $field): int
    {
        $pattern = '/"' . preg_quote($field, '/') . '"\s*:/';

        return preg_match_all($pattern, $raw) ?: 0;
    }

    private function assertRawUnsignedInteger(
        Validator $validator,
        string $raw,
        string $field,
        bool $allowZero
    ): void {
        $number = $allowZero
            ? '(?:0|[1-9][0-9]*)'
            : '(?:[1-9][0-9]*)';

        $pattern = '/"'
            . preg_quote($field, '/')
            . '"\s*:\s*'
            . $number
            . '\s*(?=,|\})/';

        if (preg_match($pattern, $raw) !== 1) {
            $validator->errors()->add(
                $field,
                "{$field} must be an unquoted unsigned JSON integer."
            );
        }
    }
}
