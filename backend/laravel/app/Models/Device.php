<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Device extends Model
{
    protected $fillable = [
        'device_id',
        'token_digest',
        'enabled',
        'last_seen_at',
        'last_boot_id',
        'last_sequence',
    ];

    protected $hidden = [
        'token_digest',
    ];

    protected function casts(): array
    {
        return [
            'enabled' => 'boolean',
            'last_seen_at' => 'datetime',
        ];
    }

    public function telemetrySamples(): HasMany
    {
        return $this->hasMany(
            TelemetrySample::class,
            'device_id',
            'device_id'
        );
    }

    public function monitoringEvents(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(
            MonitoringEvent::class,
            'device_id',
            'device_id'
        );
    }

}
