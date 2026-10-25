<?php

namespace Tests\Support;

use App\Models\Device;
use App\Models\User;
use Illuminate\Support\Facades\DB;

trait MonitoringFixtures
{
    private function operator(string $email = 'operator@example.com'): User
    {
        return User::query()->create(['name' => 'Synthetic operator', 'email' => $email, 'password' => bin2hex(random_bytes(20))]);
    }

    private function monitoringDevice(string $id = 'monitor-demo', bool $enabled = true): Device
    {
        return Device::query()->create(['device_id' => $id, 'token_digest' => hash('sha256', random_bytes(32)), 'enabled' => $enabled]);
    }

    private function grant(User $user, Device $device): void
    {
        DB::table('monitoring_device_access')->insert(['user_id' => $user->id, 'device_id' => $device->device_id]);
    }

    private function sample(Device $device, string $receivedAt, array $channels, string $mode = 'simulation'): int
    {
        $id = (int) DB::table('telemetry_samples')->insertGetId([
            'device_id' => $device->device_id, 'schema_version' => '1.0', 'firmware_version' => 'synthetic-ui',
            'boot_id' => 'synthetic-boot', 'sequence' => 1, 'uptime_ms' => 1,
            'source_mode' => $mode, 'received_at' => $receivedAt,
        ]);
        foreach ($channels as $name => $channel) {
            DB::table('telemetry_channels')->insert(['telemetry_sample_id' => $id, 'name' => $name,
                'value' => $channel['value'], 'quality' => $channel['quality']]);
        }
        return $id;
    }
}
