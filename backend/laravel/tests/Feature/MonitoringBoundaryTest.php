<?php

namespace Tests\Feature;

use App\Services\MonitoringAccess;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\DatabaseTransactions;
use Mockery;
use Tests\MySqlTestCase;
use Tests\Support\MonitoringFixtures;

class MonitoringBoundaryTest extends MySqlTestCase
{
    use DatabaseTransactions, MonitoringFixtures;

    public function test_monitoring_storage_failure_is_sanitized_and_uncacheable(): void
    {
        $user = $this->operator();
        $service = Mockery::mock(MonitoringAccess::class);
        $service->shouldReceive('enabled')->once()->andThrow(new QueryException('mysql', 'SELECT synthetic_private_marker', [], new \PDOException('synthetic outage detail', 2002)));
        $this->app->instance(MonitoringAccess::class, $service);
        $response = $this->actingAs($user, 'web')->get('/monitoring')->assertStatus(503)
            ->assertExactJson(['error' => 'backend_temporarily_unavailable'])->assertHeader('Retry-After', '5');
        $this->assertStringContainsString('no-store', (string) $response->headers->get('Cache-Control'));
        $this->assertStringContainsString('Cookie', (string) $response->headers->get('Vary'));
        $this->assertStringContainsString("frame-ancestors 'none'", (string) $response->headers->get('Content-Security-Policy'));
        $response->assertDontSee('synthetic_private_marker')->assertDontSee('synthetic outage detail');
    }

    public function test_login_storage_failure_outside_device_controller_is_sanitized(): void
    {
        $provider = Mockery::mock(\Illuminate\Contracts\Auth\UserProvider::class);
        $provider->shouldReceive('retrieveByCredentials')->once()->andThrow(new QueryException('mysql', 'SELECT synthetic_auth_marker', [], new \PDOException('synthetic auth outage', 2002)));
        \Illuminate\Support\Facades\Auth::guard('web')->setProvider($provider);
        $this->post('/login', ['email' => 'unknown@example.com', 'password' => bin2hex(random_bytes(20))])
            ->assertStatus(503)->assertExactJson(['error' => 'backend_temporarily_unavailable'])->assertDontSee('synthetic_auth_marker');
    }

    public function test_unicode_password_over_byte_limit_never_reaches_auth_provider(): void
    {
        $provider = Mockery::mock(\Illuminate\Contracts\Auth\UserProvider::class);
        $provider->shouldNotReceive('retrieveByCredentials');
        \Illuminate\Support\Facades\Auth::guard('web')->setProvider($provider);
        $attempt = str_repeat("\xC3\xA9", 40);
        $this->assertLessThan(72, mb_strlen($attempt));
        $this->assertGreaterThan(72, strlen($attempt));
        $this->from('/login')->post('/login', ['email' => 'unknown@example.com', 'password' => $attempt])
            ->assertRedirect('/login')->assertSessionHasErrors(['email' => 'Sign-in failed.']);
    }
}
