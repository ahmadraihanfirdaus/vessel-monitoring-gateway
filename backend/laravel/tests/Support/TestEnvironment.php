<?php

namespace Tests\Support;

use Dotenv\Dotenv;
use PHPUnit\TextUI\Configuration\PhpHandler;
use PHPUnit\TextUI\XmlConfiguration\Loader;
use RuntimeException;

/** Explicitly opt in to the approved ignored file; never load the ordinary .env. */
final class TestEnvironment
{
    public static function prepare(bool $localFile): array
    {
        $root = dirname(__DIR__, 2);
        $audit = ['local_testing_file' => $localFile, 'process_override_names' => [], 'phpunit_env' => [],
            'phpunit_server_names' => [], 'secret_values' => 'REDACTED_NOT_EMITTED'];
        $names = array_unique(array_merge(array_keys(getenv()), array_keys($_ENV), array_keys($_SERVER)));
        foreach ($names as $name) {
            if (preg_match('/\A(?:APP_|AUTH_|DB_|MYSQL_|DATABASE_|VG_|CACHE_|SESSION_|QUEUE_|LOG_|MAIL_|REDIS_)/', $name)) {
                $audit['process_override_names'][] = $name;
            }
        }
        sort($audit['process_override_names']);
        if ($localFile) {
            $path = $root.'/.env.testing';
            if (! is_file($path) || is_link($path) || filesize($path) > 65536) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: approved local testing file unavailable.');
            }
            try {
                $values = Dotenv::parse(file_get_contents($path));
            } catch (\Throwable $exception) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: local testing file could not be parsed.');
            }
            self::assertFileAndOverrides($values, getenv(), $_ENV, $_SERVER);
            foreach ($values as $name => $value) {
                if (getenv($name) === false && ! isset($_ENV[$name]) && ! isset($_SERVER[$name])) {
                    putenv($name.'='.$value);
                    $_ENV[$name] = $value;
                }
            }
            if (getenv('VG_MYSQL_TEST_ACK') === false) {
                putenv('VG_MYSQL_TEST_ACK=vessel_gateway_codex_test');
                $_ENV['VG_MYSQL_TEST_ACK'] = 'vessel_gateway_codex_test';
            }
        }
        // Use the installed PHPUnit handler, including force/server precedence,
        // so migration preflight and the subsequent PHPUnit process agree.
        $xml = (new Loader)->load($root.'/phpunit.xml');
        foreach ($xml->php()->envVariables() as $variable) {
            $audit['phpunit_env'][] = ['name' => $variable->name(), 'force' => $variable->force()];
        }
        foreach ($xml->php()->serverVariables() as $variable) {
            $audit['phpunit_server_names'][] = $variable->name();
        }
        (new PhpHandler)->handle($xml->php());

        return $audit;
    }

    public static function assertFileAndOverrides(array $values, array ...$layers): void
    {
        $target = ['APP_ENV' => 'testing', 'DB_CONNECTION' => 'mysql', 'DB_HOST' => '127.0.0.1',
            'DB_PORT' => '3307', 'DB_DATABASE' => 'vessel_gateway_codex_test', 'DB_USERNAME' => 'vgw_codex'];
        foreach ($target as $name => $value) {
            if (($values[$name] ?? null) !== $value) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: testing file target differs from approved target.');
            }
        }
        if (! is_string($values['DB_PASSWORD'] ?? null)) {
            throw new RuntimeException('MYSQL_TEST_BLOCKED: explicit test credential required.');
        }
        $target['DB_PASSWORD'] = $values['DB_PASSWORD'];
        $target['VG_MYSQL_TEST_ACK'] = 'vessel_gateway_codex_test';
        $target['GITHUB_ACTIONS'] = 'false';
        foreach (['DB_URL', 'DATABASE_URL', 'DB_SOCKET'] as $name) {
            if (! empty($values[$name])) {
                throw new RuntimeException('MYSQL_TEST_BLOCKED: testing file connection override prohibited.');
            }
            $target[$name] = '';
        }
        foreach ($layers as $layer) {
            foreach ($target as $name => $value) {
                if (array_key_exists($name, $layer) && (string) $layer[$name] !== $value) {
                    throw new RuntimeException('MYSQL_TEST_BLOCKED: process environment conflicts with approved testing file.');
                }
            }
        }
    }
}
