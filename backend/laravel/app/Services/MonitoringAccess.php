<?php

namespace App\Services;

use App\Models\Device;
use App\Models\User;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Facades\DB;

class MonitoringAccess
{
    public function enabled(User $user): bool
    {
        return DB::table('users')->where('id', $user->getAuthIdentifier())->whereNull('disabled_at')->exists();
    }

    public function devices(User $user): Builder
    {
        // Recheck grants and user disablement on every read, including sessions
        // created before revocation. Never select credential-bearing device columns.
        return Device::query()->join('monitoring_device_access as access', 'access.device_id', '=', 'devices.device_id')
            ->join('users', 'users.id', '=', 'access.user_id')
            ->where('users.id', $user->getAuthIdentifier())->whereNull('users.disabled_at')
            ->where('devices.enabled', true)
            ->select(['devices.device_id', 'devices.enabled', 'devices.last_seen_at', 'devices.last_boot_id', 'devices.last_sequence']);
    }
}
