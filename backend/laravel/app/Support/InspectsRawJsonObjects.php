<?php

namespace App\Support;

use JsonException;

/** Structural inspection only; caller must first validate the complete JSON. */
trait InspectsRawJsonObjects
{
    /**
     * Parse only object-member boundaries from already valid JSON.
     *
     * @return array<int, array{key:string,value:string}>|null
     */
    private function parseRawObjectMembers(string $raw): ?array
    {
        $length = strlen($raw);
        $offset = 0;
        $this->skipRawWhitespace($raw, $offset);

        if ($offset >= $length || $raw[$offset] !== '{') {
            return null;
        }

        ++$offset;
        $members = [];

        while (true) {
            $this->skipRawWhitespace($raw, $offset);

            if ($offset >= $length) {
                return null;
            }

            if ($raw[$offset] === '}') {
                ++$offset;
                break;
            }

            $keyToken = $this->consumeRawJsonString($raw, $offset);

            if ($keyToken === null) {
                return null;
            }

            try {
                $key = json_decode(
                    $keyToken,
                    true,
                    512,
                    JSON_THROW_ON_ERROR
                );
            } catch (JsonException) {
                return null;
            }

            if (! is_string($key)) {
                return null;
            }

            $this->skipRawWhitespace($raw, $offset);

            if ($offset >= $length || $raw[$offset] !== ':') {
                return null;
            }

            ++$offset;
            $this->skipRawWhitespace($raw, $offset);
            $valueStart = $offset;

            if (! $this->consumeRawJsonValue($raw, $offset)) {
                return null;
            }

            $members[] = [
                'key' => $key,
                'value' => substr($raw, $valueStart, $offset - $valueStart),
            ];

            $this->skipRawWhitespace($raw, $offset);

            if ($offset >= $length) {
                return null;
            }

            if ($raw[$offset] === ',') {
                ++$offset;

                continue;
            }

            if ($raw[$offset] === '}') {
                ++$offset;
                break;
            }

            return null;
        }

        $this->skipRawWhitespace($raw, $offset);

        return $offset === $length ? $members : null;
    }

    private function consumeRawJsonString(
        string $raw,
        int &$offset
    ): ?string {
        $length = strlen($raw);

        if ($offset >= $length || $raw[$offset] !== '"') {
            return null;
        }

        $start = $offset;
        ++$offset;

        while ($offset < $length) {
            if ($raw[$offset] === '\\') {
                $offset += 2;

                continue;
            }

            if ($raw[$offset] === '"') {
                ++$offset;

                return substr($raw, $start, $offset - $start);
            }

            ++$offset;
        }

        return null;
    }

    private function consumeRawJsonValue(
        string $raw,
        int &$offset
    ): bool {
        $length = strlen($raw);

        if ($offset >= $length) {
            return false;
        }

        if ($raw[$offset] === '"') {
            return $this->consumeRawJsonString($raw, $offset) !== null;
        }

        if ($raw[$offset] === '{' || $raw[$offset] === '[') {
            return $this->consumeRawJsonComposite($raw, $offset);
        }

        $start = $offset;

        while ($offset < $length
            && $raw[$offset] !== ','
            && $raw[$offset] !== '}') {
            ++$offset;
        }

        return trim(substr($raw, $start, $offset - $start)) !== '';
    }

    private function consumeRawJsonComposite(
        string $raw,
        int &$offset
    ): bool {
        $length = strlen($raw);
        $stack = [$raw[$offset]];
        ++$offset;

        while ($offset < $length && $stack !== []) {
            if ($raw[$offset] === '"') {
                if ($this->consumeRawJsonString($raw, $offset) === null) {
                    return false;
                }

                continue;
            }

            if ($raw[$offset] === '{' || $raw[$offset] === '[') {
                $stack[] = $raw[$offset];
                ++$offset;

                continue;
            }

            if ($raw[$offset] === '}' || $raw[$offset] === ']') {
                $opening = array_pop($stack);
                $expected = $opening === '{' ? '}' : ']';

                if ($raw[$offset] !== $expected) {
                    return false;
                }

                ++$offset;

                continue;
            }

            ++$offset;
        }

        return $stack === [];
    }

    private function skipRawWhitespace(
        string $raw,
        int &$offset
    ): void {
        $length = strlen($raw);

        while ($offset < $length
            && ($raw[$offset] === ' '
                || $raw[$offset] === "\t"
                || $raw[$offset] === "\r"
                || $raw[$offset] === "\n")) {
            ++$offset;
        }
    }

}
