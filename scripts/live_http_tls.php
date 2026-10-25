<?php

/** Ephemeral local TLS only: no database, existing keys, credentials or publication. */
try {
    if (PHP_SAPI !== 'cli' || PHP_VERSION !== '8.2.35' || ! extension_loaded('openssl')) {
        throw new RuntimeException;
    }
    $directory = realpath($argv[1] ?? '');
    if (! is_string($directory) || dirname($directory) !== realpath(sys_get_temp_dir()) ||
        ! str_starts_with(basename($directory), 'vg-live-http-')) {
        throw new RuntimeException;
    }
    foreach (['openssl.cnf', 'ca.pem', 'server.pem', 'server-key.pem'] as $file) {
        if (file_exists($directory.'/'.$file) || is_link($directory.'/'.$file)) {
            throw new RuntimeException;
        }
    }
    $config = <<<'CONFIG'
[req]
distinguished_name=dn
prompt=no
[dn]
CN=Local Gateway Test
[ca_ext]
basicConstraints=critical,CA:TRUE
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
[server_ext]
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:localhost,IP:127.0.0.1
CONFIG;
    $configPath = $directory.'/openssl.cnf';
    if (file_put_contents($configPath, $config."\n", LOCK_EX) === false) {
        throw new RuntimeException;
    }
    $options = ['config' => $configPath, 'private_key_bits' => 2048,
        'private_key_type' => OPENSSL_KEYTYPE_RSA, 'digest_alg' => 'sha256'];
    $root = openssl_pkey_new($options);
    $rootRequest = openssl_csr_new(['commonName' => 'Local Gateway Test Root'], $root, $options);
    $rootCertificate = openssl_csr_sign($rootRequest, null, $root, 1,
        $options + ['x509_extensions' => 'ca_ext'], random_int(1, PHP_INT_MAX));
    $server = openssl_pkey_new($options);
    $request = openssl_csr_new(['commonName' => 'localhost'], $server, $options);
    $certificate = openssl_csr_sign($request, $rootCertificate, $root, 1,
        $options + ['x509_extensions' => 'server_ext'], random_int(1, PHP_INT_MAX));
    if (! openssl_x509_export($rootCertificate, $ca) || ! openssl_x509_export($certificate, $leaf) ||
        ! openssl_pkey_export($server, $encoded, null, $options)) {
        throw new RuntimeException;
    }
    foreach (['ca.pem' => $ca, 'server.pem' => $leaf, 'server-key.pem' => $encoded] as $file => $bytes) {
        if (file_put_contents($directory.'/'.$file, $bytes, LOCK_EX) === false) {
            throw new RuntimeException;
        }
        chmod($directory.'/'.$file, 0600);
    }
    echo "LIVE_HTTP_TLS_MATERIAL=PASS_EPHEMERAL_LOCAL_ONLY\n";
} catch (Throwable $exception) {
    fwrite(STDERR, "LIVE_HTTP_TLS_MATERIAL=BLOCKED\n");
    exit(3);
}
