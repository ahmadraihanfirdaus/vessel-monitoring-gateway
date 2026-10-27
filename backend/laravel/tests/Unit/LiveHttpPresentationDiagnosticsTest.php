<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use Tests\Support\LiveHttpSafety;

class LiveHttpPresentationDiagnosticsTest extends TestCase
{
    public function test_private_dashboard_categories_report_actual_context_without_changing_it(): void
    {
        $data = ['state' => ['source_mode' => 'simulation', 'schema_version' => '1.1'],
            'simulationPresentation' => true, 'sampleFreshness' => ['label' => 'LIVE']];
        $before = $data;
        $this->assertSame(['Profile' => 'CONTINUOUS_SIMULATION_V11', 'Presentation' => 'ENABLED',
            'Source' => 'SIMULATION', 'Schema' => 'V1_1', 'Freshness' => 'LIVE'],
            LiveHttpSafety::presentationCategories('continuous_simulation_v11', $data));
        $this->assertSame($before, $data);
        foreach (['simulation' => 'SIMULATION', 'physical' => 'PHYSICAL', 'bench_test' => 'BENCH_TEST'] as $source => $label) {
            $data['state']['source_mode'] = $source;
            $this->assertSame($label, LiveHttpSafety::presentationCategories(null, $data)['Source']);
        }
        foreach (['LIVE', 'STALE', 'OFFLINE', 'UNKNOWN'] as $label) {
            $data['sampleFreshness']['label'] = $label;
            $this->assertSame($label, LiveHttpSafety::presentationCategories(null, $data)['Freshness']);
        }
    }

    public function test_private_categories_never_echo_arbitrary_values_or_coerce_schema_and_flags(): void
    {
        foreach (['synthetic-private', "injected\r\nheader", [], false, 1.1] as $invalid) {
            $data = ['state' => ['source_mode' => $invalid, 'schema_version' => $invalid],
                'simulationPresentation' => 'true', 'sampleFreshness' => ['label' => $invalid]];
            $this->assertSame(['Profile' => 'OTHER', 'Presentation' => 'DISABLED',
                'Source' => 'UNKNOWN', 'Schema' => 'UNKNOWN', 'Freshness' => 'UNKNOWN'],
                LiveHttpSafety::presentationCategories($invalid, $data));
        }
        $this->assertSame(['Profile' => 'UNSET', 'Presentation' => 'DISABLED',
            'Source' => 'UNKNOWN', 'Schema' => 'UNKNOWN', 'Freshness' => 'UNKNOWN'],
            LiveHttpSafety::presentationCategories(null, []));
        $this->assertSame('V1_0', LiveHttpSafety::presentationCategories('', [
            'state' => ['schema_version' => '1.0']])['Schema']);
    }
}
