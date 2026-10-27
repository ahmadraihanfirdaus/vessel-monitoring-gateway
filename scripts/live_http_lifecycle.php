<?php

/** Private harness hook. Never emit the error message, path, trace or request. */
function vgLiveRegisterShutdownDiagnostics(): void
{
    register_shutdown_function(static function (): void {
        $last = error_get_last();
        $category = [E_ERROR => 'FATAL_ERROR', E_PARSE => 'PARSE_ERROR',
            E_CORE_ERROR => 'CORE_ERROR', E_COMPILE_ERROR => 'COMPILE_ERROR',
            E_USER_ERROR => 'USER_ERROR', E_RECOVERABLE_ERROR => 'RECOVERABLE_ERROR'][$last['type'] ?? 0] ?? 'NO_FATAL_REPORTED';
        if ($category === 'FATAL_ERROR' && str_contains($last['message'] ?? '', 'Allowed memory size of')) {
            $category = 'MEMORY_LIMIT';
        }
        error_log('VG_LIVE_SHUTDOWN='.$category);
    });
}
