<?php

namespace Tests;

use Illuminate\Support\Facades\DB;
use Tests\Support\MySqlIsolation;

abstract class MySqlTestCase extends TestCase
{
    public function createApplication()
    {
        $env = MySqlIsolation::processEnvironment();
        MySqlIsolation::assertEnvironment($env);
        $app = parent::createApplication();
        $config = $app['config'];
        MySqlIsolation::assertEffectiveConfiguration($env,
            $config->get('database.connections.mysql'), $config->get('database.default'));
        try {
            $pdo = DB::connection('mysql')->getPdo();
            MySqlIsolation::verify($pdo, $env);
            MySqlIsolation::assertMigratedAndEmpty($pdo);
        } catch (\PDOException $exception) {
            throw new \RuntimeException('MYSQL_TEST_BLOCKED: isolated database unavailable.');
        }

        return $app;
    }
}
