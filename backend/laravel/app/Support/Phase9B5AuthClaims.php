<?php
namespace App\Support;
/** Host-only injected verification claims. NO TLS validation or real secrets performed here. */
final class Phase9B5AuthClaims
{
    public static function allowSynthetic(array $claims,string $raw): bool
    {
        if (array_keys($claims)!==['tls_verified','external_secret','device_authenticated','device_id']) return false;
        if ($claims['tls_verified']!==true || $claims['external_secret']!==true || $claims['device_authenticated']!==true) return false;
        if (!is_string($claims['device_id']) || !Phase9B5StrictPayload::acceptsSynthetic($raw)) return false;
        $data=json_decode($raw,true,512,JSON_BIGINT_AS_STRING);
        return hash_equals($claims['device_id'],$data['device_id']);
    }
}
