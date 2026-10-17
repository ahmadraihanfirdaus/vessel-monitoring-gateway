<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class TelemetrySample extends Model
{
    protected $fillable = [
        'device_id',
        'schema_version',
        'firmware_version',
        'boot_id',
        'sequence',
        'uptime_ms',
        'source_mode',
        'received_at',
    ];

    protected function casts(): array
    {
        return [
            'received_at' => 'datetime',
        ];
    }

    public function device(): BelongsTo
    {
        return $this->belongsTo(
            Device::class,
            'device_id',
            'device_id'
        );
    }

    public function channels(): HasMany
    {
        return $this->hasMany(TelemetryChannel::class);
    }
}
