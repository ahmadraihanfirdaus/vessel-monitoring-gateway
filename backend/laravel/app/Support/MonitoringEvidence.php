<?php

namespace App\Support;

/** Public status fields only; never exposes evidence bodies, paths or free text. */
final class MonitoringEvidence
{
    public function __construct(private readonly ?string $root = null)
    {
    }

    public function snapshot(): array
    {
        try {
            return ['available' => true,
                'simulation' => $this->read('formal-scenario-status.csv', 'SIM', 15),
                'supplemental' => $this->read('supplemental-verification-plan.csv', 'SUP', 19)];
        } catch (\Throwable) {
            return ['available' => false, 'simulation' => [], 'supplemental' => []];
        }
    }

    private function read(string $file, string $prefix, int $count): array
    {
        $path = ($this->root ?? dirname(base_path(), 2)).'/docs/testing/'.$file;
        if (is_link($path) || ! is_file($path) || filesize($path) > 131072) {
            throw new \RuntimeException('Evidence registry unavailable.');
        }
        $handle = fopen($path, 'rb');
        if ($handle === false) {
            throw new \RuntimeException('Evidence registry unavailable.');
        }
        try {
            $header = fgetcsv($handle);
            if (! is_array($header) || count($header) !== count(array_unique($header))
                || ! in_array('test_id', $header, true) || ! in_array('execution_status', $header, true)) {
                throw new \RuntimeException('Invalid registry header.');
            }
            $rows = [];
            while (($values = fgetcsv($handle)) !== false) {
                if (count($values) !== count($header)) {
                    throw new \RuntimeException('Invalid registry row.');
                }
                $row = array_combine($header, $values);
                $id = $row['test_id'];
                $allowed = $prefix === 'SIM' ? ['PASS', 'FAIL', 'BLOCKED', 'NOT_RUN'] : ['PASS', 'FAIL', 'BLOCKED', 'NOT_RUN', 'PLANNED'];
                if (isset($rows[$id]) || ! in_array($row['execution_status'], $allowed, true)) {
                    throw new \RuntimeException('Invalid registry status.');
                }
                $rows[$id] = $row['execution_status'];
            }
            ksort($rows);
            $expected = array_map(static fn ($n) => sprintf('%s-%03d', $prefix, $n), range(1, $count));
            if (array_keys($rows) !== $expected) {
                throw new \RuntimeException('Incomplete registry.');
            }
            return $rows;
        } finally {
            fclose($handle);
        }
    }
}
