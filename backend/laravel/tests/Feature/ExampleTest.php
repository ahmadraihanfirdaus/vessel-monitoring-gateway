<?php

namespace Tests\Feature;

use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\Route;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    /** Keep the original root smoke-test file; verify the actual project entry. */
    public function test_project_entry_redirects_to_monitoring_with_private_security_headers(): void
    {
        $response = $this->get('/')->assertRedirect(route('monitoring.index'))
            ->assertHeader('Pragma', 'no-cache')->assertHeader('X-Content-Type-Options', 'nosniff')
            ->assertHeader('Referrer-Policy', 'no-referrer');
        $this->assertStringContainsString('no-store', $response->headers->get('Cache-Control'));
        $this->assertStringContainsString("frame-ancestors 'none'", $response->headers->get('Content-Security-Policy'));
        $this->assertStringContainsString('Cookie', $response->headers->get('Vary'));
        $response->assertDontSee('fonts.bunny.net', false)->assertDontSee('demo_channel', false);
        $this->assertGuest();
    }

    public function test_project_entry_head_and_query_cannot_change_redirect_target(): void
    {
        $this->head('/')->assertRedirect(route('monitoring.index'))->assertContent('');
        $response = $this->get('/?destination=https%3A%2F%2Funrelated.invalid&status=301&redirect=%2Flogout');
        $response->assertStatus(302)->assertRedirect(route('monitoring.index'));
        $this->assertStringContainsString('no-store', $response->headers->get('Cache-Control'));
    }

    public function test_project_entry_does_not_bypass_login_or_expose_monitoring_data(): void
    {
        $this->get('/')->assertRedirect(route('monitoring.index'));
        $this->get('/monitoring')->assertRedirect(route('login'));
        $this->get('/login')->assertOk()->assertSee('Sign in')->assertDontSee('demo_channel', false);
        $this->assertGuest();
    }

    public function test_project_entry_database_outage_is_sanitized_even_before_route_middleware(): void
    {
        // Negative fault injection into the actual exception renderer, no SQL.
        Route::get('/', static fn () => throw new QueryException('mysql', 'SELECT synthetic_root_outage', [],
            new \PDOException('synthetic root unavailable', 2002)));
        $response = $this->getJson('/')->assertStatus(503)
            ->assertJson(['error' => 'backend_temporarily_unavailable'])->assertHeader('Retry-After', '5');
        $this->assertStringContainsString('no-store', $response->headers->get('Cache-Control'));
        $response->assertHeader('X-Content-Type-Options', 'nosniff')->assertDontSee('SELECT', false)
            ->assertDontSee('synthetic_root_outage', false);
    }

    public function test_project_entry_query_defect_is_not_masked_as_temporary_outage(): void
    {
        config(['app.debug' => false]);
        Route::get('/', static fn () => throw new QueryException('mysql', 'SELECT synthetic_root_defect', [],
            new \PDOException('synthetic root query defect', 1054)));
        $response = $this->getJson('/')->assertStatus(500)->assertDontSee('synthetic_root_defect', false);
        $this->assertStringContainsString('no-store', $response->headers->get('Cache-Control'));
    }
}
