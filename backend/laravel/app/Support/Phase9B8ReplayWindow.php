<?php
namespace App\Support;
/** Bounded, in-process synthetic ordered cursor; NOT transactional or persistent. */
final class Phase9B8ReplayWindow
{
    private array $cursor = [];
    public function __construct(private int $capacity = 32) {}
    private function key(string $device,string $boot): string
    {
        return json_encode([$device,$boot],JSON_THROW_ON_ERROR);
    }
    public function classify(string $device,string $boot,mixed $seq): string
    {
        if ($device==='' || $boot==='' || strlen($device)>64 || strlen($boot)>64 ||
            (!is_string($seq) && !is_int($seq))) return 'REJECT';
        $s=(string)$seq;
        if (preg_match('/\A[1-9][0-9]{0,9}\z/D',$s)!==1 ||
            (float)$s>4294967295.0) return 'REJECT';
        if ($this->capacity<1 || $this->capacity>64) return 'REJECT';
        $key=$this->key($device,$boot);
        if (!array_key_exists($key,$this->cursor))
            return count($this->cursor)<$this->capacity?'FIRST':'CAPACITY';
        $last=$this->cursor[$key];$v=(int)$s;
        if ($v===$last) return 'REPEAT';
        if ($v<$last) return 'STALE';
        return $v===$last+1?'NEXT':'GAP';
    }
    public function record(string $device,string $boot,mixed $seq): bool
    {
        $decision=$this->classify($device,$boot,$seq);
        if ($decision!=='FIRST' && $decision!=='NEXT') return false;
        $this->cursor[$this->key($device,$boot)]=(int)$seq;
        return true;
    }
}
