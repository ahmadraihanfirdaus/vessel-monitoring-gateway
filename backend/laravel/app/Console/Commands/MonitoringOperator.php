<?php

namespace App\Console\Commands;

use App\Models\Device;
use App\Models\User;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;

class MonitoringOperator extends Command
{
    protected $signature = 'monitoring:operator {email} {--name=} {--device=*} {--revoke=*} {--disable} {--enable} {--password-env}';
    protected $description = 'Provision/revoke read-only monitoring access; never accepts a password argument';

    public function handle(): int
    {
        try {
            return $this->provision();
        } catch (\Illuminate\Database\QueryException) {
            // Query exceptions may include credential hash bindings. Never echo them.
            $this->error('Monitoring storage unavailable or update rejected.');
            return self::FAILURE;
        }
    }

    private function provision(): int
    {
        $email = strtolower((string) $this->argument('email'));
        if (Validator::make(['email' => $email, 'name' => $this->option('name') ?? 'Monitoring operator'],
            ['email' => ['required', 'email', 'max:254'], 'name' => ['required', 'string', 'max:100']])->fails()
            || ($this->option('disable') && $this->option('enable'))) {
            $this->error('Invalid operator options.');
            return self::FAILURE;
        }
        $existing = User::query()->where('email', $email)->first();
        $secret = null;
        if ($this->option('password-env')) {
            $secret = getenv('VG_MONITORING_PASSWORD');
        } elseif ($existing === null && $this->input->isInteractive()) {
            $secret = $this->secret('New operator password');
        }
        if (($existing === null || $this->option('password-env'))
            && (! is_string($secret) || strlen($secret) < 16 || strlen($secret) > 72)) {
            $this->error('A 16..72 byte password is required through hidden input or the dedicated process environment.');
            return self::FAILURE;
        }
        $grant = array_unique($this->option('device'));
        $revoke = array_unique($this->option('revoke'));
        if (array_intersect($grant, $revoke) !== [] || count($grant) > 100 || count($revoke) > 100) {
            $this->error('Invalid grant/revoke options.');
            return self::FAILURE;
        }
        return DB::transaction(function () use ($email, $existing, $secret, $grant, $revoke): int {
            // Validate every target before writing an account or partial grants.
            if (Device::query()->whereIn('device_id', $grant)->where('enabled', true)->count() !== count($grant)) {
                $this->error('Every grant requires an existing enabled device.');
                return self::FAILURE;
            }
            $user = $existing ?? new User(['email' => $email, 'name' => $this->option('name') ?? 'Monitoring operator']);
            if ($secret !== null) {
                $user->password = $secret; // Existing User hashed cast handles storage.
            }
            if ($this->option('name') !== null) {
                $user->name = $this->option('name');
            }
            if ($this->option('disable') || $this->option('enable')) {
                $user->forceFill(['disabled_at' => $this->option('disable') ? now() : null]);
            }
            $user->save();
            foreach ($grant as $deviceId) {
                DB::table('monitoring_device_access')->insertOrIgnore(['user_id' => $user->id, 'device_id' => $deviceId]);
            }
            if ($revoke !== []) {
                DB::table('monitoring_device_access')->where('user_id', $user->id)->whereIn('device_id', $revoke)->delete();
            }
            $this->info('Monitoring access updated.');
            return self::SUCCESS;
        });
    }
}
