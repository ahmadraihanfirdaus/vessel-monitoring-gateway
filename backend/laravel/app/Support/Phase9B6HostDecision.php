<?php
namespace App\Support;
/** Synthetic host ingest decision only: NO HTTP, auth implementation or MySQL transaction. */
final class Phase9B6HostDecision
{
    public static function ingest(array $claims,string $raw,Phase9B5DedupLedger $ledger): array
    {
        $deny=['decision'=>'BLOCK','ack_eligible'=>false,'identity'=>null,'quality'=>null];
        if (!Phase9B5AuthClaims::allowSynthetic($claims,$raw)) return $deny;
        if (!Phase9B5StrictPayload::acceptsSynthetic($raw)) return $deny;
        $data=json_decode($raw,true,512,JSON_BIGINT_AS_STRING);
        if (!is_array($data) || !isset($data['channels'])) return $deny;
        $profile=Phase9B6ChannelAudit::profile($data['channels']);
        if ($profile===null) return $deny;
        $decision=$ledger->ingest($raw);
        if (!in_array($decision,['ACCEPT_FIRST','DUPLICATE_SAME','CONFLICT','CAPACITY','REJECT'],true)) return $deny;
        return ['decision'=>$decision,
            'ack_eligible'=>in_array($decision,['ACCEPT_FIRST','DUPLICATE_SAME'],true),
            'identity'=>[$data['device_id'],$data['boot_id'],(string)$data['sequence']],
            'quality'=>$profile];
    }
}
