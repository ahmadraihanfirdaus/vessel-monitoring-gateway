<?php
namespace App\Support;
/** Bounded in-process identity ledger for deterministic fixtures only.
 * Not atomic across requests/processes, not MySQL-backed, not SIM-014 evidence. */
final class Phase9B5DedupLedger
{
    private array $seen=[];
    public function __construct(private int $capacity) {}
    public function ingest(string $raw): string
    {
        if (!Phase9B5StrictPayload::acceptsSynthetic($raw)) return 'REJECT';
        if ($this->capacity<1 || $this->capacity>64) return 'REJECT';
        $v=json_decode($raw,true,512,JSON_BIGINT_AS_STRING);
        $identity=json_encode([$v['device_id'],$v['boot_id'],(string)$v['sequence']],JSON_THROW_ON_ERROR);
        $signature=hash('sha256',json_encode($this->canonical($v),JSON_THROW_ON_ERROR|JSON_PRESERVE_ZERO_FRACTION));
        if (isset($this->seen[$identity])) return hash_equals($this->seen[$identity],$signature)?'DUPLICATE_SAME':'CONFLICT';
        if (count($this->seen)>=$this->capacity) return 'CAPACITY';
        $this->seen[$identity]=$signature;return 'ACCEPT_FIRST';
    }
    private function canonical(mixed $value): mixed
    {
        if (!is_array($value)) return $value;
        if (!array_is_list($value)) ksort($value,SORT_STRING);
        foreach ($value as $k=>$v) $value[$k]=$this->canonical($v);
        return $value;
    }
}
