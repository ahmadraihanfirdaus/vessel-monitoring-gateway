<?php

namespace Tests\Unit;

use App\Support\MonitoringEvidence;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

class MonitoringEvidenceTest extends TestCase
{
    public function test_actual_registry_statuses_are_read_without_qualifications_or_paths(): void
    {
        $data = (new MonitoringEvidence(dirname(__DIR__, 4)))->snapshot();
        $this->assertTrue($data['available']);
        $this->assertCount(15, $data['simulation']);
        $this->assertCount(19, $data['supplemental']);
        $this->assertSame('PASS', $data['simulation']['SIM-001']);
        $this->assertSame('NOT_RUN', $data['simulation']['SIM-010']);
        foreach (array_merge($data['simulation'], $data['supplemental']) as $value) {
            $this->assertContains($value, ['PASS', 'FAIL', 'BLOCKED', 'NOT_RUN', 'PLANNED']);
        }
    }

    #[DataProvider('invalidRegistries')]
    public function test_missing_tampered_or_incomplete_evidence_is_unknown(string $variant): void
    {
        $root = sys_get_temp_dir().'/vg-evidence-'.bin2hex(random_bytes(8));
        $folder = $root.'/docs/testing';
        mkdir($folder, 0700, true);
        $file = $folder.'/formal-scenario-status.csv';
        try {
            $content = "test_id,execution_status\n";
            for ($id = 1; $id <= 15; $id++) {
                $content .= sprintf("SIM-%03d,NOT_RUN\n", $id);
            }
            $content = match ($variant) {
                'duplicate' => $content."SIM-001,PASS\n",
                'unknown' => str_replace('SIM-015', 'SIM-999', $content),
                'status' => str_replace('NOT_RUN', 'synthetic-sensitive-marker', $content),
                'planned_sim' => str_replace('NOT_RUN', 'PLANNED', $content),
                'partial' => "test_id,execution_status\nSIM-001,PASS\n",
                'header' => "test_id,test_id,execution_status\n",
                'oversize' => str_repeat('x', 131073),
                default => $content,
            };
            if ($variant !== 'missing') {
                file_put_contents($file, $content);
            }
            $supplemental = "test_id,execution_status\n";
            for ($id = 1; $id <= 19; $id++) { $supplemental .= sprintf("SUP-%03d,NOT_RUN\n", $id); }
            file_put_contents($folder.'/supplemental-verification-plan.csv', $supplemental);
            $data = (new MonitoringEvidence($root))->snapshot();
            $this->assertSame(['available' => false, 'simulation' => [], 'supplemental' => []], $data);
        } finally {
            if (is_file($file)) { unlink($file); }
            unlink($folder.'/supplemental-verification-plan.csv');
            rmdir($folder); rmdir($root.'/docs'); rmdir($root);
        }
    }

    public static function invalidRegistries(): array
    {
        return array_map(static fn ($name) => [$name], ['missing', 'duplicate', 'unknown', 'status', 'planned_sim', 'partial', 'header', 'oversize']);
    }
}
