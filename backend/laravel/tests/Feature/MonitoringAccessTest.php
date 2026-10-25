<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

class MonitoringAccessTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    public function test_guest_routes_redirect_to_login_without_device_disclosure(): void
    {
        $this->get('/monitoring')->assertRedirect('/login');
        $this->get('/monitoring/unknown-demo')->assertRedirect('/login');
        $this->get('/login')->assertOk()->assertSee('autocomplete="current-password"', false);
        $this->post('/register')->assertNotFound();
    }

    public function test_explicit_grants_filter_listing_and_deny_other_devices(): void
    {
        $user = $this->operator();
        $own = $this->monitoringDevice();
        $other = $this->monitoringDevice('other-demo');
        $disabled = $this->monitoringDevice('disabled-demo', false);
        $this->grant($user, $own);
        $this->grant($user, $disabled);
        $this->grant($this->operator('other@example.com'), $other);
        $response = $this->actingAs($user, 'web')->get('/monitoring')->assertOk()->assertSee('monitor-demo')->assertDontSee('other-demo')->assertDontSee('disabled-demo');
        $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
        $this->get('/monitoring/'.$own->device_id)->assertOk();
        foreach ([$other->device_id, $disabled->device_id, 'unknown-demo'] as $id) {
            $this->get('/monitoring/'.$id)->assertNotFound();
        }
        $this->assertStringNotContainsString($own->token_digest, $response->getContent());
    }

    public function test_no_grants_is_an_explicit_empty_list(): void
    {
        $this->monitoringDevice();
        $this->actingAs($this->operator(), 'web')->get('/monitoring')->assertOk()->assertSee('Tidak ada perangkat yang diizinkan.');
        $this->get('/monitoring/monitor-demo')->assertNotFound();
    }

    public function test_revocation_and_disabled_operator_take_effect_without_new_login(): void
    {
        $user = $this->operator();
        $device = $this->monitoringDevice();
        $this->grant($user, $device);
        $this->actingAs($user, 'web')->get('/monitoring/'.$device->device_id)->assertOk();
        DB::table('monitoring_device_access')->where('user_id', $user->id)->delete();
        $this->get('/monitoring/'.$device->device_id)->assertNotFound();
        $this->grant($user, $device);
        DB::table('users')->where('id', $user->id)->update(['disabled_at' => now()]);
        $this->get('/monitoring')->assertForbidden();
        $this->get('/monitoring/'.$device->device_id)->assertForbidden();
    }

    public function test_successful_login_rotates_session_and_logout_invalidates_it(): void
    {
        $user = $this->operator();
        $secret = bin2hex(random_bytes(20));
        $user->password = $secret;
        $user->save();
        $this->get('/login')->assertOk();
        $before = session()->getId();
        $response = $this->post('/login', ['email' => strtoupper($user->email), 'password' => $secret])->assertRedirect('/monitoring');
        $this->assertAuthenticatedAs($user, 'web');
        $this->assertNotSame($before, session()->getId());
        $this->assertNull(session()->getOldInput('password'));
        $this->assertStringNotContainsString($secret, $response->getContent());
        $this->assertTrue(Hash::check($secret, $user->password));
        $this->post('/logout')->assertRedirect('/login');
        $this->assertGuest('web');
        $this->get('/monitoring')->assertRedirect('/login');
    }

    public function test_disabled_and_wrong_login_use_same_generic_error_without_password_flash(): void
    {
        $user = $this->operator();
        $secret = bin2hex(random_bytes(20));
        $user->password = $secret;
        $user->forceFill(['disabled_at' => now()])->save();
        foreach ([$secret, bin2hex(random_bytes(20))] as $attempt) {
            $this->from('/login')->post('/login', ['email' => $user->email, 'password' => $attempt])
                ->assertRedirect('/login')->assertSessionHasErrors(['email' => 'Sign-in failed.']);
            $this->assertGuest('web');
            $this->assertNull(session()->getOldInput('password'));
        }
    }

    public function test_login_rate_limit_is_enforced(): void
    {
        for ($attempt = 0; $attempt < 5; $attempt++) {
            $this->post('/login', ['email' => 'unknown@example.com', 'password' => bin2hex(random_bytes(20))])->assertRedirect();
        }
        $response = $this->post('/login', ['email' => 'unknown@example.com', 'password' => bin2hex(random_bytes(20))])->assertStatus(429);
        $this->assertNotNull($response->headers->get('Retry-After'));
        $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
    }

    public function test_csrf_is_enforced_when_testing_bypass_is_disabled_only_in_the_test_middleware(): void
    {
        $this->app->bind(\Illuminate\Foundation\Http\Middleware\ValidateCsrfToken::class,
            static fn ($app) => new class($app, $app['encrypter']) extends \Illuminate\Foundation\Http\Middleware\ValidateCsrfToken {
                protected function runningUnitTests() { return false; }
            });
        $denied = $this->post('/login', ['email' => 'unknown@example.com', 'password' => bin2hex(random_bytes(20))])->assertStatus(419);
        $this->assertStringContainsString('no-store', (string) $denied->headers->get('Cache-Control'));
        $token = bin2hex(random_bytes(20));
        $this->withSession(['_token' => $token])->post('/login', ['email' => 'unknown@example.com', 'password' => bin2hex(random_bytes(20)), '_token' => $token])->assertRedirect();
    }

    public function test_database_sessions_cache_and_secure_cookie_path_work_with_real_login(): void
    {
        config(['session.driver' => 'database', 'cache.default' => 'database']);
        $user = $this->operator();
        $secret = bin2hex(random_bytes(20));
        $user->password = $secret;
        $user->save();
        $login = $this->get('https://localhost/login')->assertOk();
        $cookieName = config('session.cookie');
        $cookie = $login->getCookie($cookieName, false);
        $this->assertTrue($cookie->isSecure());
        $this->assertTrue($cookie->isHttpOnly());
        $this->assertSame('lax', $cookie->getSameSite());
        $this->withCookie($cookieName, $login->getCookie($cookieName)->getValue());
        $signedIn = $this->post('https://localhost/login', ['email' => $user->email, 'password' => $secret])->assertRedirect('/monitoring');
        $this->assertGreaterThan(0, DB::table('cache')->count());
        $this->assertSame($user->id, (int) DB::table('sessions')->where('id', $signedIn->getCookie($cookieName)->getValue())->value('user_id'));
        $this->withCookie($cookieName, $signedIn->getCookie($cookieName)->getValue());
        \Illuminate\Support\Facades\Auth::forgetGuards();
        $this->get('https://localhost/monitoring')->assertOk();
    }
}
