<?php
namespace App\Support;
/** Host fixture channel reconciliation, NOT database quality evidence. */
final class Phase9B6ChannelAudit
{
    public static function profile(array $channels): ?array
    {
        if ($channels===[] || count($channels)>16 || array_is_list($channels)) return null;
        $counts=['valid_zero'=>0,'valid_nonzero'=>0,'missing_null'=>0,'stale_null'=>0,'stale_value'=>0,'other_null'=>0];
        foreach ($channels as $key=>$row) {
            if (!is_string($key) || !preg_match('/\A[A-Za-z0-9._:-]{1,32}\z/D',$key) ||
                !is_array($row) || array_keys($row)!==['value','quality']) return null;
            $q=$row['quality'];$v=$row['value'];
            if ($q==='valid') {
                if (!is_int($v) && !is_float($v)) return null;
                if (!is_finite((float)$v)) return null;
                ++$counts[$v==0?'valid_zero':'valid_nonzero'];
            } elseif ($q==='missing' || $q==='invalid' || $q==='unknown') {
                if ($v!==null) return null;
                ++$counts[$q==='missing'?'missing_null':'other_null'];
            } elseif ($q==='stale') {
                if ($v!==null && !is_int($v) && !is_float($v)) return null;
                if ($v!==null && !is_finite((float)$v)) return null;
                ++$counts[$v===null?'stale_null':'stale_value'];
            } else return null;
        }
        return $counts;
    }
}
