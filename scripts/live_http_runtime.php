<?php

/** Private CLI-server fingerprint: fixed names and scrubbed numeric versions only. */
function vgLiveRuntimeFingerprint(): array
{
    $extensions = [];
    foreach (['PDO', 'pdo_mysql', 'mysqlnd', 'openssl', 'mbstring', 'intl', 'FFI', 'Zend OPcache', 'xdebug', 'pcov'] as $name) {
        $version = phpversion($name);
        $extensions[$name] = $version === false ? 'NOT_LOADED'
            : (preg_match('/\A[0-9]+(?:\.[0-9]+){0,3}\z/', $version) === 1 ? $version : 'OTHER');
    }
    $setting = static function (string $name): string {
        $value = ini_get($name);
        return is_string($value) && strlen($value) <= 20 &&
            preg_match('/\A(?:-1|[0-9]+[KMG]?|off|on|tracing|function)?\z/i', $value) === 1 ? $value : 'OTHER';
    };
    $handler = static function (int $number): string {
        if (! function_exists('pcntl_signal_get_handler')) {
            return 'UNAVAILABLE';
        }
        $value = pcntl_signal_get_handler($number);
        return $value === SIG_DFL ? 'DEFAULT' : ($value === SIG_IGN ? 'IGNORED' : 'CUSTOM');
    };
    return ['php_version' => PHP_VERSION === '8.2.35' ? '8.2.35' : 'OTHER',
        'sapi' => PHP_SAPI === 'cli-server' ? 'CLI_SERVER' : (PHP_SAPI === 'cli' ? 'CLI' : 'OTHER'),
        'debug_build' => (bool) PHP_DEBUG, 'zts' => (bool) PHP_ZTS, 'int_bytes' => PHP_INT_SIZE,
        'extensions' => $extensions, 'opcache_enable_cli' => $setting('opcache.enable_cli'),
        'opcache_jit' => $setting('opcache.jit'), 'opcache_jit_buffer_size' => $setting('opcache.jit_buffer_size'),
        'memory_limit' => $setting('memory_limit'), 'segv_handler' => $handler(11), 'term_handler' => $handler(15)];
}
