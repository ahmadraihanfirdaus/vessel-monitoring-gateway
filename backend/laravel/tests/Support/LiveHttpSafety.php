<?php

namespace Tests\Support;

use App\Models\Device;
use App\Models\User;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\DB;
use RuntimeException;

/** Test-only, explicitly isolated HTTP fixture namespace. No production bootstrap. */
final class LiveHttpSafety
{
    public static function profile(string $id): array
    {
        if (preg_match('/\A[a-f0-9]{32}\z/', $id) !== 1) {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: invalid fixture namespace.');
        }

        return ['id' => $id, 'device' => 'runtime:demo', 'other' => 'live-other-'.$id,
            'email' => 'live-'.$id.'@example.test', 'name' => 'Local HTTP test '.$id, 'agent' => 'vg-live/'.$id,
            'prefix' => 'live_'.$id.':', 'cookie' => 'live_'.$id];
    }

    public static function fromEnvironment(): array
    {
        $path = getenv('VG_LIVE_HTTP_LEASE');
        if (! is_string($path) || basename($path) !== 'vg-live-lease.json' ||
            ! is_file($path) || is_link($path) || filesize($path) > 1024) {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: explicit local fixture lease required.');
        }
        $document = json_decode(file_get_contents($path), true, flags: JSON_THROW_ON_ERROR);
        if (! is_array($document) || array_keys($document) !== ['id'] || ! is_string($document['id'])) {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: invalid fixture lease.');
        }

        return self::profile($document['id']);
    }

    public static function application(array $profile): Application
    {
        if (! in_array(PHP_SAPI, ['cli', 'cli-server'], true) || PHP_VERSION !== '8.2.35') {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: explicit PHP 8.2.35 CLI required.');
        }
        $audit = TestEnvironment::prepare(getenv('VG_USE_TESTING_ENV') === '1');
        $env = MySqlIsolation::processEnvironment();
        MySqlIsolation::assertEnvironment($env);
        $app = TestApplication::create();
        MySqlIsolation::assertEffectiveConfiguration($env,
            $app['config']->get('database.connections.mysql'), $app['config']->get('database.default'));
        MySqlIsolation::assertAncillaryConfiguration($app['config']->get('session'),
            $app['config']->get('cache.stores.database'), $app['config']->get('auth'));
        self::assertConfiguration($app, $profile);
        $pdo = DB::connection('mysql')->getPdo();
        $identity = MySqlIsolation::verify($pdo, $env);
        $app->instance('live-http-test-audit', $audit);
        $app->instance('live-http-test-identity', $identity + ['lease_id' => $profile['id'], 'device' => $profile['device']]);

        return $app;
    }

    public static function assertConfiguration(Application $app, array $profile): void
    {
        if ($profile !== self::profile($profile['id'] ?? '') ||
            $app['config']->get('app.debug') !== false ||
            $app['config']->get('session.driver') !== 'database' ||
            $app['config']->get('cache.default') !== 'database' ||
            $app['config']->get('session.cookie') !== $profile['cookie'] ||
            $app['config']->get('cache.prefix') !== $profile['prefix'] ||
            $app['config']->get('session.secure') !== true ||
            $app['config']->get('session.http_only') !== true ||
            $app['config']->get('session.same_site') !== 'lax' ||
            $app['config']->get('session.path') !== '/' ||
            ! in_array($app['config']->get('session.domain'), [null, ''], true) ||
            $app['config']->get('logging.default') !== 'null' ||
            $app['config']->get('queue.default') !== 'sync') {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: effective HTTP test profile mismatch.');
        }
        // Resolve the real encrypter without ever printing its key.
        $app->make('encrypter');
    }

    /** Fixed categories for the private test listener; never arbitrary view/config values. */
    public static function presentationCategories(mixed $profile, array $data): array
    {
        $state = is_array($data['state'] ?? null) ? $data['state'] : [];
        $freshness = is_array($data['sampleFreshness'] ?? null) ? $data['sampleFreshness'] : [];

        return [
            'Profile' => match ($profile) {
                'continuous_simulation_v11' => 'CONTINUOUS_SIMULATION_V11',
                null, '' => 'UNSET', default => 'OTHER',
            },
            'Presentation' => ($data['simulationPresentation'] ?? null) === true ? 'ENABLED' : 'DISABLED',
            'Source' => match ($state['source_mode'] ?? null) {
                'simulation' => 'SIMULATION', 'physical' => 'PHYSICAL', 'bench_test' => 'BENCH_TEST', default => 'UNKNOWN',
            },
            'Schema' => match ($state['schema_version'] ?? null) {
                '1.1' => 'V1_1', '1.0' => 'V1_0', default => 'UNKNOWN',
            },
            'Freshness' => in_array($freshness['label'] ?? null, ['LIVE', 'STALE', 'OFFLINE'], true)
                ? $freshness['label'] : 'UNKNOWN',
        ];
    }

    /** Every non-migration row must belong to this admitted, initially empty lease. */
    public static function tokenProof(array $profile, string $material): array
    {
        if ($profile !== self::profile($profile['id'] ?? '') || preg_match('/\A[a-f0-9]{64}\z/', $material) !== 1) {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: dedicated fixture ownership proof required.');
        }

        return [$profile['device'] => hash('sha256', $material),
            $profile['other'] => hash('sha256', hash('sha256', 'other:'.$material))];
    }

    public static function assertOwnedRows(array $profile, ?array $proof = null): void
    {
        if ($profile !== self::profile($profile['id'] ?? '')) {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: modified fixture profile.');
        }
        if ($proof === null) {
            $material = getenv('VG_LIVE_DEVICE_TOKEN');
            if (! is_string($material)) {
                throw new RuntimeException('LIVE_HTTP_BLOCKED: fixture ownership proof unavailable.');
            }
            $proof = self::tokenProof($profile, $material);
        }
        if (array_keys($proof) !== [$profile['device'], $profile['other']] ||
            count(array_filter($proof, static fn ($value) => is_string($value) && preg_match('/\A[a-f0-9]{64}\z/', $value) === 1)) !== 2) {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: invalid fixture ownership proof.');
        }
        TestSchema::assertCatalog(DB::connection('mysql')->getPdo());
        $devices = [$profile['device'], $profile['other']];
        $deviceIds = Device::query()->whereIn('device_id', $devices)->pluck('device_id')->all();
        $userIds = User::query()->where('email', $profile['email'])->pluck('id')->all();
        $samples = DB::table('telemetry_samples')->whereIn('device_id', $devices)->select('id');
        $unexpected = Device::query()->whereNotIn('device_id', $devices)->exists()
            || User::query()->where('email', '<>', $profile['email'])->exists()
            || User::query()->where('email', $profile['email'])->where('name', '<>', $profile['name'])->exists()
            || DB::table('telemetry_samples')->whereNotIn('device_id', $devices)->exists()
            || DB::table('monitoring_events')->whereNotIn('device_id', $devices)->exists()
            || DB::table('telemetry_channels')->whereNotIn('telemetry_sample_id', $samples)->exists()
            || DB::table('monitoring_device_access')->where(function ($query) use ($deviceIds, $userIds) {
                $query->whereNotIn('device_id', $deviceIds)->orWhereNotIn('user_id', $userIds);
            })->exists()
            || DB::table('sessions')->where(function ($query) use ($profile, $userIds) {
                $query->whereNull('user_agent')->orWhere('user_agent', '<>', $profile['agent'])
                    ->orWhereNull('ip_address')->orWhere('ip_address', '<>', '127.0.0.1')
                    ->orWhere(function ($query) use ($userIds) {
                        $query->whereNotNull('user_id')->whereNotIn('user_id', $userIds);
                    });
            })->exists();
        // A static wire device name is not ownership. Its immutable token digest
        // must prove membership in this process lease before cleanup is allowed.
        foreach (Device::query()->whereIn('device_id', $devices)->get(['device_id', 'token_digest']) as $device) {
            $unexpected = $unexpected || ! hash_equals($proof[$device->device_id], $device->token_digest);
        }
        foreach (['cache', 'cache_locks'] as $table) {
            // The namespace contains underscores: bind an escaped LIKE prefix.
            $like = str_replace(['\\', '_', '%'], ['\\\\', '\\_', '\\%'], $profile['prefix']).'%';
            $unexpected = $unexpected || DB::table($table)->where('key', 'not like', $like)->exists();
        }
        if ($unexpected) {
            throw new RuntimeException('LIVE_HTTP_BLOCKED: unrelated fixture rows detected; no cleanup permitted.');
        }
    }
}
