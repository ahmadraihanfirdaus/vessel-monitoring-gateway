<?php

namespace Tests;

use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

abstract class TestCase extends BaseTestCase
{
    public function createApplication()
    {
        $this->traitsUsedByTest = array_flip(class_uses_recursive(static::class));

        return \Tests\Support\TestApplication::create();
    }
}
