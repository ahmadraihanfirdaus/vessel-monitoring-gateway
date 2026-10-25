<?php

namespace Tests\Unit;

use App\Support\SimulationChannelPresentation as Presentation;
use PHPUnit\Framework\TestCase;

class SimulationChannelPresentationTest extends TestCase
{
    public function test_only_explicit_profile_and_simulation_new_version_enable_labels(): void
    {
        $state = ['schema_version' => '1.1', 'source_mode' => 'simulation'];
        $this->assertTrue(Presentation::enabled($state, Presentation::PROFILE));
        foreach ([null, '', 'physical', true] as $profile) {
            $this->assertFalse(Presentation::enabled($state, $profile));
        }
        $this->assertFalse(Presentation::enabled(['schema_version' => '1.0', 'source_mode' => 'simulation'], Presentation::PROFILE));
        $this->assertFalse(Presentation::enabled(['schema_version' => '1.1', 'source_mode' => 'physical'], Presentation::PROFILE));
        $this->assertFalse(Presentation::enabled(null, Presentation::PROFILE));
    }

    public function test_enum_codes_and_unknowns_are_never_silently_safe(): void
    {
        $this->assertSame('STOPPED', Presentation::describe('engine_1_state', 1));
        $this->assertSame('UNKNOWN', Presentation::describe('engine_1_state', 0));
        $this->assertSame('LOST', Presentation::describe('engine_8_comm', '3.0'));
        foreach ([2.5, -1, 100, INF, NAN, null, '<script>'] as $value) {
            $this->assertSame('UNRECOGNIZED demo code', Presentation::describe('hatch_state', $value));
        }
    }

    public function test_channel_vocabulary_is_exact_and_units_do_not_invent_hardware_meaning(): void
    {
        $this->assertNull(Presentation::describe('engine_9_rpm', 1));
        $this->assertNull(Presentation::describe('foreign<script>', 1));
        $this->assertSame('rpm', Presentation::describe('engine_8_rpm', 2000));
        $this->assertStringContainsString('not ppm', Presentation::describe('vapor_surrogate', 0));
        $this->assertStringContainsString('no machinery diagnosis', Presentation::describe('vibration_index', 1));
        $this->assertCount(48, Presentation::sections()['propulsion']);
        $this->assertSame(['power_voltage_v', 'power_current_a', 'power_w'], Presentation::sections()['power']);
    }
}
