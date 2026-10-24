<?php

require dirname(__DIR__).'/vendor/autoload.php';

if (getenv('VG_USE_TESTING_ENV') === '1') {
    try {
        \Tests\Support\TestEnvironment::prepare(true);
    } catch (Throwable $exception) {
        fwrite(STDERR, "MYSQL_TEST_BLOCKED: test environment bootstrap refused.\n");
        exit(3);
    }
}
