<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class TelemetryChannel extends Model
{
    protected $fillable = [
        'telemetry_sample_id',
        'name',
        'quality',
        'value',
    ];

    protected function casts(): array
    {
        return [
            'value' => 'float',
        ];
    }

    public function telemetrySample(): BelongsTo
    {
        return $this->belongsTo(TelemetrySample::class);
    }
}
