<?php

namespace Tests\Support;

use Illuminate\Contracts\Console\Kernel;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Bootstrap\LoadEnvironmentVariables;
use RuntimeException;

final class TestApplication
{
    public static function create(): Application
    {
        $app = require dirname(__DIR__, 2).'/bootstrap/app.php';
        // Test processes consume explicit environment only, never local dotenv files.
        $app->bind(LoadEnvironmentVariables::class, static fn () => new class
        {
            public function bootstrap(Application $app): void {}
        });
        foreach ([$app->getCachedConfigPath(), $app->getCachedRoutesPath(), $app->getCachedEventsPath()] as $path) {
            if (is_file($path)) {
                throw new RuntimeException('TEST_BOOT_BLOCKED: cached application state present.');
            }
        }
        $app->make(Kernel::class)->bootstrap();
        if (! $app->environment('testing')) {
            throw new RuntimeException('TEST_BOOT_BLOCKED: effective application environment must be testing.');
        }

        return $app;
    }
}
