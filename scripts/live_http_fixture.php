<?php

/** Explicit test fixture lifecycle; no migrations, production bootstrap or seeding. */
use App\Models\Device;
use App\Models\User;
use Illuminate\Support\Facades\DB;
use Tests\Support\LiveHttpSafety;
use Tests\Support\TestSchema;

require dirname(__DIR__).'/backend/laravel/vendor/autoload.php';

try {
    if (PHP_SAPI !== 'cli') {
        throw new RuntimeException('LIVE_HTTP_BLOCKED: fixture lifecycle is CLI only.');
    }
    $mode = $argv[1] ?? '--check';
    $mutations = ['--prepare', '--revoke', '--grant', '--disable', '--enable', '--clear-cache', '--cleanup'];
    if (! in_array($mode, array_merge(['--check', '--inspect-owned', '--session-audit', '--formal-audit', '--retry-audit', '--resilience-audit'], $mutations), true) ||
        (in_array($mode, $mutations, true) && ($argv[2] ?? '') !== '--execute')) {
        throw new RuntimeException('LIVE_HTTP_BLOCKED: explicit supported fixture action required.');
    }
    $profile = LiveHttpSafety::fromEnvironment();
    $app = LiveHttpSafety::application($profile);
    if (in_array($mode, ['--check', '--prepare'], true)) {
        TestSchema::assertMigratedAndEmpty(DB::connection('mysql')->getPdo());
    } else {
        LiveHttpSafety::assertOwnedRows($profile);
    }
    if ($mode === '--check') {
        echo 'LIVE_HTTP_CONFIG_AUDIT='.json_encode(['environment' => 'testing', 'php' => PHP_VERSION,
            'target' => ['host' => config('database.connections.mysql.host'), 'port' => config('database.connections.mysql.port'),
                'database' => config('database.connections.mysql.database'), 'username' => config('database.connections.mysql.username')],
            'identity' => $app->make('live-http-test-identity'),
            'session_driver' => config('session.driver'), 'cache_driver' => config('cache.default'),
            'secure_cookie' => config('session.secure'), 'app_debug' => config('app.debug'),
            'app_key_configured' => true, 'app_key_cipher_compatible' => true,
            'app_key_source' => 'ephemeral_runner_process', 'overrides' => $app->make('live-http-test-audit')], JSON_UNESCAPED_SLASHES)."\n";
        echo "LIVE_HTTP_PREFLIGHT=PASS_EXACT_EMPTY_APPROVED_CATALOG_PHP_8_2_35_VALID_PROCESS_KEY\n";
        exit(0);
    }
    if ($mode === '--inspect-owned') {
        echo "LIVE_HTTP_OWNERSHIP=PASS_EXACT_TEST_NAMESPACE\n";
        exit(0);
    }
    if ($mode === '--session-audit') {
        // Internal runner capture only: never emit raw session IDs/cookies.
        $sessions = DB::table('sessions')->where('user_agent', $profile['agent'])
            ->get(['id', 'user_id'])->map(static fn ($row) => [
                'fingerprint' => hash('sha256', $row->id), 'authenticated' => $row->user_id !== null]);
        echo json_encode(['sessions' => $sessions], JSON_THROW_ON_ERROR)."\n";
        exit(0);
    }
    if ($mode === '--formal-audit') {
        // Read-only, exact lease identities, after effective target and ownership guards.
        // Never return arbitrary rows, sessions, credentials, coordinates or SQL.
        $result = [];
        foreach (['src-simulation', 'src-bench_test', 'src-physical', 'dedup', 'authbad'] as $label) {
            $query = DB::table('telemetry_samples')->where('device_id', $profile['device'])
                ->where('boot_id', $label.'-'.$profile['id'])->where('sequence', '1');
            $count = (clone $query)->count();
            $rows = (clone $query)->limit(2)->get(['id', 'source_mode', 'schema_version', 'firmware_version', 'uptime_ms']);
            $facts = [];
            foreach ($rows as $row) {
                $channelQuery = DB::table('telemetry_channels')->where('telemetry_sample_id', $row->id);
                $channel = (clone $channelQuery)->where('name', 'demo_channel')->first(['quality', 'value']);
                $facts[] = ['source_mode' => $row->source_mode, 'schema_version' => $row->schema_version,
                    'firmware_version' => $row->firmware_version, 'uptime_ms' => (string) $row->uptime_ms,
                    'channel_count' => (clone $channelQuery)->count(),
                    'quality' => $channel?->quality, 'value' => $channel?->value];
            }
            $result[$label] = ['count' => $count, 'rows' => $facts];
        }
        echo json_encode(['identity' => $app->make('live-http-test-identity'), 'database' => config('database.connections.mysql.database'),
            'username' => config('database.connections.mysql.username'), 'facts' => $result], JSON_THROW_ON_ERROR)."\n";
        exit(0);
    }
    if ($mode === '--retry-audit') {
        // Read-only exact lease/fixed identity. No arbitrary row/SQL/credential output.
        $query = DB::table('monitoring_events')->where('device_id', $profile['device'])
            ->where('boot_id', 'receipt-next-'.$profile['id'])->where('event_id', '1');
        $rows = (clone $query)->limit(2)->get(['schema_version', 'event_id', 'linked_alarm_id', 'source_id',
            'source_mode', 'event_type', 'occurred_at_ms', 'alarm_metadata']);
        $facts = $rows->map(static fn ($row) => [
            'schema_version' => $row->schema_version, 'event_id' => (string) $row->event_id,
            'linked_alarm_id' => (string) $row->linked_alarm_id, 'source_id' => (int) $row->source_id,
            'source_mode' => $row->source_mode, 'event_type' => $row->event_type,
            'occurred_at_ms' => (string) $row->occurred_at_ms,
            'alarm' => json_decode($row->alarm_metadata, true, flags: JSON_THROW_ON_ERROR),
        ])->all();
        echo json_encode(['identity' => $app->make('live-http-test-identity'), 'database' => config('database.connections.mysql.database'),
            'username' => config('database.connections.mysql.username'),
            'event_count' => (clone $query)->count(), 'facts' => $facts], JSON_THROW_ON_ERROR)."\n";
        exit(0);
    }
    if ($mode === '--resilience-audit') {
        // Read-only fixed lease boot; no arbitrary query/SQL or sensitive fields.
        $boot = 'resilience-'.$profile['id'];
        $samples = DB::table('telemetry_samples')->where('device_id', $profile['device'])->where('boot_id', $boot);
        $events = DB::table('monitoring_events')->where('device_id', $profile['device'])->where('boot_id', $boot);
        $sampleFacts = [];
        foreach ((clone $samples)->orderBy('sequence')->limit(5)->get(['id', 'sequence']) as $sample) {
            $channels = DB::table('telemetry_channels')->where('telemetry_sample_id', $sample->id);
            $temperature = (clone $channels)->where('name', 'compartment_temperature_c')->first(['quality', 'value']);
            $sampleFacts[] = ['sequence' => (string) $sample->sequence, 'channel_count' => (clone $channels)->count(),
                'temperature' => ['quality' => $temperature?->quality, 'value' => $temperature?->value]];
        }
        $eventFacts = (clone $events)->orderBy('event_id')->limit(5)->get([
            'schema_version', 'device_id', 'boot_id', 'event_id', 'linked_alarm_id', 'source_id',
            'source_mode', 'event_type', 'occurred_at_ms', 'alarm_metadata'])->map(static fn ($event) => [
                'schema_version' => $event->schema_version, 'device_id' => $event->device_id, 'boot_id' => $event->boot_id,
                'event_id' => (string) $event->event_id, 'linked_alarm_id' => (string) $event->linked_alarm_id,
                'source_id' => (string) $event->source_id, 'source_mode' => $event->source_mode,
                'event_type' => $event->event_type, 'occurred_at_ms' => (string) $event->occurred_at_ms,
                'alarm' => json_decode($event->alarm_metadata, true, flags: JSON_THROW_ON_ERROR),
            ])->all();
        echo json_encode(['identity' => $app->make('live-http-test-identity'), 'database' => config('database.connections.mysql.database'),
            'username' => config('database.connections.mysql.username'), 'sample_count' => (clone $samples)->count(),
            'event_count' => (clone $events)->count(), 'samples' => $sampleFacts, 'events' => $eventFacts], JSON_THROW_ON_ERROR)."\n";
        exit(0);
    }
    if ($mode === '--prepare') {
        $input = getenv('VG_LIVE_LOGIN_SECRET');
        $material = getenv('VG_LIVE_DEVICE_TOKEN');
        if (! is_string($input) || strlen($input) < 16 || strlen($input) > 72 ||
            ! is_string($material) || preg_match('/\A[a-f0-9]{64}\z/', $material) !== 1) {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: dedicated process test inputs required.');
        }
        DB::transaction(static function () use ($profile, $input, $material): void {
            $user = new User;
            $user->name = $profile['name'];
            $user->email = $profile['email'];
            $user->password = $input;
            $user->save();
            $device = Device::query()->create(['device_id' => $profile['device'],
                'token_digest' => hash('sha256', $material), 'enabled' => true]);
            Device::query()->create(['device_id' => $profile['other'],
                'token_digest' => hash('sha256', hash('sha256', 'other:'.$material)), 'enabled' => true]);
            DB::table('monitoring_device_access')->insert(['user_id' => $user->id,
                'device_id' => $device->device_id]);
        });
    } elseif ($mode === '--cleanup') {
        // Ownership is checked again inside the transaction before exact deletes.
        DB::transaction(static function () use ($profile): void {
            LiveHttpSafety::assertOwnedRows($profile);
            $devices = [$profile['device'], $profile['other']];
            $userIds = User::query()->where('email', $profile['email'])->pluck('id')->all();
            DB::table('sessions')->where('user_agent', $profile['agent'])->where('ip_address', '127.0.0.1')->delete();
            $samples = DB::table('telemetry_samples')->whereIn('device_id', $devices)->select('id');
            DB::table('telemetry_channels')->whereIn('telemetry_sample_id', $samples)->delete();
            DB::table('telemetry_samples')->whereIn('device_id', $devices)->delete();
            DB::table('monitoring_events')->whereIn('device_id', $devices)->delete();
            DB::table('monitoring_device_access')->whereIn('user_id', $userIds)->delete();
            Device::query()->whereIn('device_id', $devices)->delete();
            User::query()->where('email', $profile['email'])->delete();
            foreach (['cache', 'cache_locks'] as $table) {
                $like = str_replace(['\\', '_', '%'], ['\\\\', '\\_', '\\%'], $profile['prefix']).'%';
                DB::table($table)->where('key', 'like', $like)->delete();
            }
        });
        TestSchema::assertMigratedAndEmpty(DB::connection('mysql')->getPdo());
    } elseif ($mode === '--clear-cache') {
        foreach (['cache', 'cache_locks'] as $table) {
            $like = str_replace(['\\', '_', '%'], ['\\\\', '\\_', '\\%'], $profile['prefix']).'%';
            DB::table($table)->where('key', 'like', $like)->delete();
        }
    } else {
        $user = User::query()->where('email', $profile['email'])->firstOrFail();
        $device = Device::query()->where('device_id', $profile['device'])->firstOrFail();
        if ($mode === '--revoke') {
            DB::table('monitoring_device_access')->where('user_id', $user->id)->where('device_id', $device->device_id)->delete();
        } elseif ($mode === '--grant') {
            DB::table('monitoring_device_access')->insertOrIgnore(['user_id' => $user->id, 'device_id' => $device->device_id]);
            if (! DB::table('monitoring_device_access')->where('user_id', $user->id)->where('device_id', $device->device_id)->exists()) {
                throw new RuntimeException('LIVE_HTTP_BLOCKED: fixture grant was not applied.');
            }
        } else {
            $user->disabled_at = $mode === '--disable' ? now() : null;
            $user->save();
        }
    }
    echo 'LIVE_HTTP_ACTION='.strtoupper(substr($mode, 2))."_PASS\n";
} catch (Throwable $exception) {
    // Exception messages can contain SQL bindings/keys. Never emit them.
    fwrite(STDERR, 'LIVE_HTTP_GATE=BLOCKED_'.class_basename($exception)."\n");
    if ($exception instanceof RuntimeException &&
        preg_match('/\A(?:LIVE_HTTP|MYSQL_TEST|TEST_BOOT)_BLOCKED: [A-Za-z0-9 ._-]{1,160}\z/', $exception->getMessage()) === 1) {
        fwrite(STDERR, $exception->getMessage()."\n");
    }
    exit(3);
}
