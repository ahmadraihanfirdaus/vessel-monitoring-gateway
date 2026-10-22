<?php
namespace App\Support;
/** Standalone host-fixture validator, NOT wired to API routes or middleware.
 * Real Laravel FormRequest, device auth and MySQL semantics remain separate. */
final class Phase9B4IngestContract
{
    public static function acceptsSynthetic(string $raw): bool
    {
        if ($raw === '' || strlen($raw) > 4096) return false;
        try { $data = json_decode($raw, true, 512, JSON_THROW_ON_ERROR | JSON_BIGINT_AS_STRING); }
        catch (\JsonException $e) { return false; }
        if (!is_array($data) || array_is_list($data)) return false;
        $fields = ['schema_version','device_id','firmware_version','boot_id',
                   'sequence','uptime_ms','source_mode','channels'];
        if (array_keys($data) !== $fields || $data['schema_version'] !== '1.0') return false;
        foreach (['device_id','firmware_version','boot_id'] as $f) {
            if (!is_string($data[$f]) || !preg_match('/\A[A-Za-z0-9._:-]{1,48}\z/D',$data[$f])) return false;
        }
        foreach (['sequence','uptime_ms'] as $f) {
            $v=$data[$f];
            if (!is_int($v) && !is_string($v)) return false;
            if (!preg_match('/\A(?:0|[1-9][0-9]*)\z/D',(string)$v)) return false;
            if (strlen((string)$v)>20 || (strlen((string)$v)==20 && strcmp((string)$v,'18446744073709551615')>0)) return false;
        }
        if (!in_array($data['source_mode'],['simulation','bench_test'],true)) return false;
        $channels=$data['channels'];
        if (!is_array($channels) || array_is_list($channels) || count($channels)<1 || count($channels)>16) return false;
        foreach ($channels as $key=>$row) {
            if (!is_string($key) || !preg_match('/\A[A-Za-z0-9._:-]{1,32}\z/D',$key)) return false;
            if (!is_array($row) || array_keys($row)!==['value','quality']) return false;
            if (!in_array($row['quality'], ['valid','invalid','missing','stale','unknown'],true)) return false;
            $value=$row['value'];
            if ($row['quality']==='valid' && (!is_numeric($value) || !is_int($value) && !is_float($value))) return false;
            if (in_array($row['quality'],['invalid','missing','unknown'],true) && $value!==null) return false;
            if ($row['quality']==='stale' && $value!==null && !is_int($value) && !is_float($value)) return false;
            if (($row['quality']==='valid' || $row['quality']==='stale') && $value!==null && !is_finite((float)$value)) return false;
        }
        return true;
    }
}
