<?php

namespace Tests\Feature;

use App\Models\Device;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use RuntimeException;
use Tests\MySqlTestCase;
use Tests\Support\LiveHttpSafety;
use Tests\Support\MonitoringFixtures;
use Tests\Support\TestSchema;

class LiveHttpSafetyTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;
    private array $proof = [];

    private function profile(): array
    {
        return LiveHttpSafety::profile(str_repeat('a', 32));
    }

    private function fixtures(): array
    {
        $profile = $this->profile();
        $user = $this->operator();
        $user->email = $profile['email'];
        $user->name = $profile['name'];
        $user->save();
        $this->proof = LiveHttpSafety::tokenProof($profile, bin2hex(random_bytes(32)));
        $device = Device::query()->create(['device_id' => $profile['device'],
            'token_digest' => $this->proof[$profile['device']], 'enabled' => true]);
        $this->grant($user, $device);

        return [$profile, $user, $device];
    }

    public function test_lease_namespace_is_strict_and_cannot_override_derived_targets(): void
    {
        $profile = $this->profile();
        $this->assertSame('runtime:demo', $profile['device']);
        foreach (['', '../other', str_repeat('a', 31), str_repeat('a', 33), str_repeat('G', 32)] as $invalid) {
            try {
                LiveHttpSafety::profile($invalid);
            } catch (RuntimeException $exception) {
                $this->assertStringContainsString('invalid fixture namespace', $exception->getMessage());
                continue;
            }
            $this->fail('Invalid namespace was admitted.');
        }
        $profile['device'] = 'unrelated';
        $this->expectException(RuntimeException::class);
        LiveHttpSafety::assertOwnedRows($profile, $this->proof);
    }

    public function test_owned_populated_fixture_passes_but_normal_empty_gate_still_rejects_it(): void
    {
        [$profile, $user] = $this->fixtures();
        DB::table('sessions')->insert(['id' => 'synthetic-owned-session', 'user_id' => $user->id,
            'user_agent' => $profile['agent'], 'ip_address' => '127.0.0.1', 'payload' => 'synthetic', 'last_activity' => 1]);
        DB::table('cache')->insert(['key' => $profile['prefix'].'fixture', 'value' => 'synthetic', 'expiration' => 1]);
        LiveHttpSafety::assertOwnedRows($profile, $this->proof);
        TestSchema::assertCatalog(DB::connection('mysql')->getPdo());
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('preexisting application rows prohibited');
        TestSchema::assertMigratedAndEmpty(DB::connection('mysql')->getPdo());
    }

    public function test_unrelated_device_blocks_ownership_without_changing_rows(): void
    {
        [$profile] = $this->fixtures();
        Device::query()->create(['device_id' => 'unrelated-device', 'token_digest' => hash('sha256', random_bytes(32)), 'enabled' => true]);
        $this->expectException(RuntimeException::class);
        LiveHttpSafety::assertOwnedRows($profile, $this->proof);
    }

    public function test_unrelated_user_blocks_ownership(): void
    {
        [$profile] = $this->fixtures();
        $this->operator();
        $this->expectException(RuntimeException::class);
        LiveHttpSafety::assertOwnedRows($profile, $this->proof);
    }

    public function test_unrelated_session_agent_blocks_cleanup_admission(): void
    {
        [$profile] = $this->fixtures();
        DB::table('sessions')->insert(['id' => 'synthetic-unowned-session', 'user_agent' => 'unrelated',
            'ip_address' => '127.0.0.1', 'payload' => 'synthetic', 'last_activity' => 1]);
        $this->expectException(RuntimeException::class);
        LiveHttpSafety::assertOwnedRows($profile, $this->proof);
    }

    public function test_unrelated_session_address_blocks_cleanup_admission(): void
    {
        [$profile] = $this->fixtures();
        DB::table('sessions')->insert(['id' => 'synthetic-unowned-session', 'user_agent' => $profile['agent'],
            'ip_address' => '127.0.0.2', 'payload' => 'synthetic', 'last_activity' => 1]);
        $this->expectException(RuntimeException::class);
        LiveHttpSafety::assertOwnedRows($profile, $this->proof);
    }

    public function test_cache_prefix_underscore_is_literal_not_a_wildcard(): void
    {
        [$profile] = $this->fixtures();
        DB::table('cache')->insert(['key' => str_replace('_', 'X', $profile['prefix']).'foreign',
            'value' => 'synthetic', 'expiration' => 1]);
        $this->expectException(RuntimeException::class);
        LiveHttpSafety::assertOwnedRows($profile, $this->proof);
    }

    public function test_matching_device_name_with_foreign_token_cannot_be_claimed_or_deleted(): void
    {
        [$profile, , $device] = $this->fixtures();
        $device->token_digest = hash('sha256', random_bytes(32));
        $device->save();
        $this->expectException(RuntimeException::class);
        LiveHttpSafety::assertOwnedRows($profile, $this->proof);
    }

    public function test_effective_test_configuration_fails_closed_for_each_changed_boundary(): void
    {
        $profile = $this->profile();
        config(['app.debug' => false, 'session.driver' => 'database', 'cache.default' => 'database',
            'session.cookie' => $profile['cookie'], 'cache.prefix' => $profile['prefix'],
            'session.secure' => true, 'session.http_only' => true, 'session.same_site' => 'lax',
            'session.path' => '/', 'session.domain' => null, 'logging.default' => 'null', 'queue.default' => 'sync']);
        LiveHttpSafety::assertConfiguration($this->app, $profile);
        foreach (['app.debug' => true, 'session.driver' => 'file', 'cache.default' => 'redis',
            'session.cookie' => 'unrelated', 'cache.prefix' => 'unrelated', 'session.secure' => false,
            'session.http_only' => false, 'session.same_site' => 'none', 'session.path' => '/other',
            'session.domain' => 'unrelated.invalid', 'logging.default' => 'stack', 'queue.default' => 'redis'] as $name => $invalid) {
            $before = config($name);
            config([$name => $invalid]);
            try {
                LiveHttpSafety::assertConfiguration($this->app, $profile);
            } catch (RuntimeException $exception) {
                $this->assertStringContainsString('profile mismatch', $exception->getMessage());
                config([$name => $before]);
                continue;
            }
            config([$name => $before]);
            $this->fail('Changed configuration was admitted.');
        }
        LiveHttpSafety::assertConfiguration($this->app, $profile);
    }
}
