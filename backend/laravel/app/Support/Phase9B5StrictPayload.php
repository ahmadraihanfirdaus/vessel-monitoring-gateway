<?php
namespace App\Support;
/** Standalone synthetic request check: additionally rejects nested/escaped duplicate JSON keys.
 * No routes, database, device authentication, or TLS integration. */
final class Phase9B5StrictPayload
{
    private string $json;
    private int $offset=0;
    private int $length=0;
    public static function acceptsSynthetic(string $raw): bool
    {
        if (strlen($raw)===0 || strlen($raw)>4096) return false;
        $s=new self();$s->json=$raw;$s->length=strlen($raw);
        if (!$s->value(0)) return false;
        $s->space();
        return $s->offset===$s->length && Phase9B4IngestContract::acceptsSynthetic($raw);
    }
    private function space(): void {
        while ($this->offset<$this->length && str_contains(" \t\r\n",$this->json[$this->offset])) ++$this->offset;
    }
    private function string(): ?string {
        $start=$this->offset;
        if ($start >= $this->length || $this->json[$start]!=='"') return null;
        ++$this->offset;
        while ($this->offset<$this->length) {
            $c=$this->json[$this->offset++];
            if ($c==='"') {
                $decoded=json_decode(substr($this->json,$start,$this->offset-$start),true);
                return is_string($decoded)?$decoded:null;
            }
            if (ord($c)<32) return null;
            if ($c==='\\') {
                if ($this->offset >= $this->length) return null;
                ++$this->offset;
            }
        }
        return null;
    }
    private function value(int $depth): bool {
        if ($depth>32) return false;
        $this->space();
        if ($this->offset >= $this->length) return false;
        $c=$this->json[$this->offset];
        if ($c==='"') return $this->string()!==null;
        if ($c==='{' || $c==='[') {
            $isObj=$c==='{';++$this->offset;$this->space();
            $close=$isObj?'}':']';
            if ($this->offset<$this->length && $this->json[$this->offset]===$close) {++$this->offset;return true;}
            $keys=[];
            while (true) {
                if ($isObj) {
                    $key=$this->string();if ($key===null || array_key_exists('k:'.$key,$keys)) return false;
                    $keys['k:'.$key]=true;$this->space();
                    if ($this->offset >= $this->length || $this->json[$this->offset++]!==':') return false;
                }
                if (!$this->value($depth+1)) return false;
                $this->space();if ($this->offset >= $this->length) return false;
                $sep=$this->json[$this->offset++];
                if ($sep===$close) return true;
                if ($sep!==',') return false;
                $this->space();
            }
        }
        foreach (['true','false','null'] as $literal) {
            if (substr($this->json,$this->offset,strlen($literal))===$literal) {
                $this->offset+=strlen($literal);return true;
            }
        }
        $tail=substr($this->json,$this->offset);
        if (preg_match('/\A-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/',$tail,$m)===1) {
            $this->offset+=strlen($m[0]);return true;
        }
        return false;
    }
}
