<?php

namespace App\Http\Requests;

use App\Support\InspectsRawJsonObjects;
use Closure;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Validator;
use JsonException;

class TelemetryIngestRequest extends FormRequest
{
    use InspectsRawJsonObjects;

    private const SAFE_TOKEN_PATTERN = '/\A[A-Za-z0-9._:-]+\z/';

    private const UINT64_MAX = '18446744073709551615';

    private const SOURCE_MODES = [
        'simulation',
        'bench_test',
        'physical',
    ];

    private const QUALITIES = [
        'valid',
        'invalid',
        'missing',
        'stale',
        'unknown',
    ];

    private const TOP_LEVEL_FIELDS = [
        'schema_version',
        'device_id',
        'firmware_version',
        'boot_id',
        'sequence',
        'uptime_ms',
        'source_mode',
        'channels',
    ];

    protected function prepareForValidation(): void
    {
        if (! $this->isJson()) {
            return;
        }

        try {
            $preserved = json_decode(
                $this->getContent(),
                true,
                512,
                JSON_THROW_ON_ERROR | JSON_BIGINT_AS_STRING
            );
        } catch (JsonException) {
            return;
        }

        if (! is_array($preserved)) {
            return;
        }

        $input = $this->json()->all();

        if (! is_array($input)) {
            return;
        }

        foreach (['sequence', 'uptime_ms'] as $field) {
            if (array_key_exists($field, $preserved)) {
                $input[$field] = $preserved[$field];
            }
        }

        $this->replace($input);
    }

    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'schema_version' => ['required', 'string', 'in:1.0,1.1'],
            'device_id' => [
                'required',
                'string',
                'max:48',
                'regex:'.self::SAFE_TOKEN_PATTERN,
            ],
            'firmware_version' => [
                'required',
                'string',
                'max:48',
                'regex:'.self::SAFE_TOKEN_PATTERN,
            ],
            'boot_id' => [
                'required',
                'string',
                'max:48',
                'regex:'.self::SAFE_TOKEN_PATTERN,
            ],
            'sequence' => ['required', $this->uint64Rule()],
            'uptime_ms' => ['required', $this->uint64Rule()],
            'source_mode' => ['required', 'string', 'in:'.implode(',', self::SOURCE_MODES)],
            'channels' => ['required', 'array', 'min:1', 'max:'.($this->input('schema_version') === '1.1' ? 72 : 16)],
            'channels.*' => ['required', 'array:value,quality'],
            'channels.*.value' => ['present', 'nullable', 'numeric'],
            'channels.*.quality' => [
                'required',
                'string',
                'in:'.implode(',', self::QUALITIES),
            ],
        ];
    }

    public function withValidator(Validator $validator): void
    {
        $validator->after(function (Validator $validator): void {
            $this->validateTopLevelFields($validator);
            $this->validateRawObjectKeyUniqueness($validator);
            $this->validateRawUnsignedInteger($validator, 'sequence');
            $this->validateRawUnsignedInteger($validator, 'uptime_ms');
            $this->validateChannels($validator);
        });
    }

    private function uint64Rule(): Closure
    {
        return function (string $attribute, mixed $value, Closure $fail): void {
            if (! $this->isUnsigned64($value)) {
                $fail($attribute.' must be an unsigned 64-bit integer.');
            }
        };
    }

    private function isUnsigned64(mixed $value): bool
    {
        if (is_int($value)) {
            return $value >= 0;
        }

        if (! is_string($value)
            || preg_match('/\A(?:0|[1-9][0-9]*)\z/', $value) !== 1) {
            return false;
        }

        $length = strlen($value);
        $maxLength = strlen(self::UINT64_MAX);

        if ($length < $maxLength) {
            return true;
        }

        if ($length > $maxLength) {
            return false;
        }

        return strcmp($value, self::UINT64_MAX) <= 0;
    }

    private function validateRawUnsignedInteger(
        Validator $validator,
        string $field
    ): void {
        $members = $this->rawTopLevelMembers();

        if ($members === null) {
            return;
        }

        $matchingMembers = array_values(array_filter(
            $members,
            static fn (array $member): bool => $member['key'] === $field
        ));

        if (count($matchingMembers) !== 1
            || preg_match(
                '/\A(?:0|[1-9][0-9]*)\z/',
                trim($matchingMembers[0]['value'] ?? '')
            ) !== 1) {
            $validator->errors()->add(
                $field,
                $field.' must be encoded exactly once as an unsigned JSON integer.'
            );
        }
    }

    private function validateRawObjectKeyUniqueness(
        Validator $validator
    ): void {
        if (! $this->isJson()) {
            return;
        }

        $members = $this->rawTopLevelMembers();

        if ($members === null) {
            if ($this->rawJsonIsValid()) {
                $validator->errors()->add(
                    'payload',
                    'Telemetry JSON structure could not be inspected safely.'
                );
            }

            return;
        }

        foreach ($this->duplicateRawKeys($members) as $key) {
            $validator->errors()->add(
                'payload',
                'Duplicate top-level JSON key is not allowed: '.$key.'.'
            );
        }

        $channelMembers = array_values(array_filter(
            $members,
            static fn (array $member): bool => $member['key'] === 'channels'
        ));

        if (count($channelMembers) !== 1) {
            return;
        }

        $channels = $this->parseRawObjectMembers(
            trim($channelMembers[0]['value'])
        );

        if ($channels === null) {
            return;
        }

        foreach ($this->duplicateRawKeys($channels) as $name) {
            $validator->errors()->add(
                'channels',
                'Duplicate channel JSON key is not allowed: '.$name.'.'
            );
        }

        foreach ($channels as $channel) {
            $channelFields = $this->parseRawObjectMembers(
                trim($channel['value'])
            );

            if ($channelFields === null) {
                continue;
            }

            foreach ($this->duplicateRawKeys($channelFields) as $field) {
                $validator->errors()->add(
                    'channels.'.$channel['key'],
                    'Duplicate channel field is not allowed: '.$field.'.'
                );
            }
        }
    }

    private function rawTopLevelMembers(): ?array
    {
        if (! $this->isJson() || ! $this->rawJsonIsValid()) {
            return null;
        }

        return $this->parseRawObjectMembers($this->getContent());
    }

    private function rawJsonIsValid(): bool
    {
        try {
            json_decode(
                $this->getContent(),
                true,
                512,
                JSON_THROW_ON_ERROR | JSON_BIGINT_AS_STRING
            );

            return true;
        } catch (JsonException) {
            return false;
        }
    }

    /**
     * @param array<int, array{key:string,value:string}> $members
     * @return array<int, string>
     */
    private function duplicateRawKeys(array $members): array
    {
        $counts = [];

        foreach ($members as $member) {
            $counts[$member['key']] = ($counts[$member['key']] ?? 0) + 1;
        }

        return array_keys(array_filter(
            $counts,
            static fn (int $count): bool => $count > 1
        ));
    }

    private function validateTopLevelFields(Validator $validator): void
    {
        $json = $this->json()->all();

        if (! is_array($json)) {
            return;
        }

        $unexpected = array_diff(array_keys($json), self::TOP_LEVEL_FIELDS);

        if ($unexpected !== []) {
            $validator->errors()->add(
                'payload',
                'Unexpected telemetry payload fields are not allowed.'
            );
        }
    }

    private function validateChannels(Validator $validator): void
    {
        $channels = $this->input('channels');

        if (! is_array($channels)) {
            return;
        }

        foreach ($channels as $rawName => $channel) {
            $name = (string) $rawName;

            if (strlen($name) === 0
                || strlen($name) > 32
                || preg_match(self::SAFE_TOKEN_PATTERN, $name) !== 1) {
                $validator->errors()->add(
                    'channels.'.$name,
                    'Channel name does not satisfy the telemetry contract.'
                );
            }

            if (! is_array($channel)
                || ! array_key_exists('quality', $channel)
                || ! array_key_exists('value', $channel)) {
                continue;
            }

            $quality = $channel['quality'];
            $value = $channel['value'];

            if (! is_string($quality)
                || ! in_array($quality, self::QUALITIES, true)) {
                continue;
            }

            $numericFinite = (is_int($value) || is_float($value))
                && is_finite((float) $value);

            if ($quality === 'valid' && ! $numericFinite) {
                $validator->errors()->add(
                    'channels.'.$name.'.value',
                    'Valid quality requires a finite JSON numeric value.'
                );
            }

            if ($quality === 'stale'
                && $value !== null
                && ! $numericFinite) {
                $validator->errors()->add(
                    'channels.'.$name.'.value',
                    'Stale quality permits null or a finite JSON numeric value.'
                );
            }

            if (in_array($quality, ['invalid', 'missing', 'unknown'], true)
                && $value !== null) {
                $validator->errors()->add(
                    'channels.'.$name.'.value',
                    'Invalid, missing, or unknown quality requires a null value.'
                );
            }
        }
    }
}
