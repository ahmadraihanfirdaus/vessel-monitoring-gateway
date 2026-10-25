<?php

namespace App\Support;

/** Opt-in presentation of the documented simulation 1.1 vocabulary only. */
class SimulationChannelPresentation
{
    public const PROFILE = 'continuous_simulation_v11';

    public static function enabled(?array $state, mixed $profile): bool
    {
        return $profile === self::PROFILE && ($state['schema_version'] ?? null) === '1.1'
            && ($state['source_mode'] ?? null) === 'simulation';
    }

    public static function sections(): array
    {
        $engines = [];
        for ($engine = 1; $engine <= 8; $engine++) {
            foreach (['state', 'rpm', 'temperature_c', 'runtime_s', 'alarm', 'comm'] as $field) {
                $engines[] = 'engine_'.$engine.'_'.$field;
            }
        }

        return [
            'safety' => ['hatch_state', 'vapor_state', 'vapor_surrogate', 'bilge_state',
                'compartment_temperature_c', 'local_alarm_active'],
            'propulsion' => $engines,
            'navigation' => ['nav_latitude_deg', 'nav_longitude_deg', 'nav_sog_knots', 'nav_cog_deg',
                'nav_fix', 'nav_age_ms', 'attitude_roll_deg', 'attitude_pitch_deg',
                'acceleration_x_g', 'acceleration_y_g', 'acceleration_z_g', 'vibration_index'],
            'power' => ['power_voltage_v', 'power_current_a', 'power_w'],
        ];
    }

    public static function describe(string $name, mixed $value): ?string
    {
        $enums = [
            'hatch_state' => [0 => 'UNKNOWN', 1 => 'OPEN', 2 => 'CLOSED'],
            'vapor_state' => [0 => 'UNKNOWN', 1 => 'NORMAL', 2 => 'WARNING', 3 => 'ALARM', 4 => 'FAULT'],
            'bilge_state' => [0 => 'UNKNOWN', 1 => 'NORMAL', 2 => 'HIGH', 3 => 'FAULT'],
            'nav_fix' => [0 => 'NO FIX (last sentence)', 1 => 'FIX (last sentence)'],
            'local_alarm_active' => [0 => 'INACTIVE logical request', 1 => 'ACTIVE logical request'],
        ];
        if (preg_match('/\Aengine_[1-8]_(state|alarm|comm)\z/', $name, $match) === 1) {
            $enums[$name] = match ($match[1]) {
                'state' => [0 => 'UNKNOWN', 1 => 'STOPPED', 2 => 'RUNNING', 3 => 'FAULT'],
                'alarm' => [0 => 'INACTIVE engine demo flag', 1 => 'ACTIVE engine demo flag'],
                'comm' => [0 => 'UNKNOWN', 1 => 'GOOD', 2 => 'DEGRADED', 3 => 'LOST'],
            };
        }
        if (isset($enums[$name])) {
            if (! is_numeric($value) || ! is_finite((float) $value) || (float) $value < 0
                || (float) $value > 4 || floor((float) $value) !== (float) $value) {
                return 'UNRECOGNIZED demo code';
            }

            return $enums[$name][(int) $value] ?? 'UNRECOGNIZED demo code';
        }
        if (preg_match('/\Aengine_[1-8]_(rpm|temperature_c|runtime_s)\z/', $name, $match) === 1) {
            return ['rpm' => 'rpm', 'temperature_c' => '°C', 'runtime_s' => 's'][$match[1]];
        }

        return [
            'vapor_surrogate' => 'unitless surrogate; not ppm or %LEL',
            'compartment_temperature_c' => '°C', 'nav_latitude_deg' => 'degrees (synthetic)',
            'nav_longitude_deg' => 'degrees (synthetic)', 'nav_sog_knots' => 'knots',
            'nav_cog_deg' => 'degrees', 'nav_age_ms' => 'ms (boot-relative age)',
            'attitude_roll_deg' => 'degrees; attitude prototype only',
            'attitude_pitch_deg' => 'degrees; attitude prototype only',
            'acceleration_x_g' => 'g; acceleration prototype', 'acceleration_y_g' => 'g; acceleration prototype',
            'acceleration_z_g' => 'g; acceleration prototype', 'vibration_index' => 'development index; no machinery diagnosis',
            'power_voltage_v' => 'V; low-power prototype', 'power_current_a' => 'A; low-power prototype',
            'power_w' => 'W; low-power prototype', 'runtime_journal_retained' => 'retained events (capacity 8)',
            'runtime_journal_rejected' => 'rejected critical-event attempts; incomplete retention',
            'runtime_skipped' => 'missed sampling periods',
        ][$name] ?? null;
    }
}
