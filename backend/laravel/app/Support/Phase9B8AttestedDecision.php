<?php
namespace App\Support;
/** Test-only injected claims: NOT TLS certificate/secret/token or live clock verification. */
final class Phase9B8AttestedDecision
{
    public static function admit(array $claims,string $raw,int $nowMs,
        Phase9B5DedupLedger $ledger,Phase9B8ReplayWindow $window): array
    {
        $deny=['decision'=>'BLOCK','ack_eligible'=>false,'window'=>'DENIED'];
        if (array_keys($claims)!==[
            'tls_verified','external_secret','device_authenticated','device_id',
            'scope','iat_ms','exp_ms']) return $deny;
        if ($claims['scope']!=='telemetry:ingest' ||
            !is_int($claims['iat_ms']) || !is_int($claims['exp_ms']) ||
            $claims['iat_ms']<0 || $claims['exp_ms']<=$claims['iat_ms'] ||
            $claims['exp_ms']-$claims['iat_ms']>300000 ||
            $nowMs<$claims['iat_ms'] || $nowMs>=$claims['exp_ms']) return $deny;
        $base=array_slice($claims,0,4,true);
        if (!Phase9B5AuthClaims::allowSynthetic($base,$raw)) return $deny;
        $data=json_decode($raw,true,512,JSON_BIGINT_AS_STRING);
        if (!is_array($data)|| !array_key_exists('sequence',$data) ||
            !isset($data['device_id'],$data['boot_id'])) return $deny;
        $state=$window->classify($data['device_id'],$data['boot_id'],$data['sequence']);
        if (!in_array($state,['FIRST','NEXT','REPEAT'],true))
            return ['decision'=>'BLOCK','ack_eligible'=>false,'window'=>$state];
        $r=Phase9B6HostDecision::ingest($base,$raw,$ledger);
        $ok=(($state==='REPEAT' && $r['decision']==='DUPLICATE_SAME') ||
             ($state!=='REPEAT' && $r['decision']==='ACCEPT_FIRST'));
        if (!$ok) return ['decision'=>$r['decision'],'ack_eligible'=>false,'window'=>$state];
        if ($state!=='REPEAT' && !$window->record($data['device_id'],$data['boot_id'],$data['sequence']))
            return $deny;
        return ['decision'=>$r['decision'],'ack_eligible'=>true,'window'=>$state];
    }
}
