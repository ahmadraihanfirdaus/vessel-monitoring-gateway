<?php

namespace App\Services;

use App\Models\Device;

class DeviceTokenAuthenticator
{
    public function resolve(string $bearerToken): ?Device
    {
        $digest = hash('sha256', $bearerToken);

        return Device::query()
            ->where('token_digest', $digest)
            ->first();
    }
}
