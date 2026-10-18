<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class MonitoringEvent extends Model
{
    public $timestamps = false;

    protected $fillable = [
        'device_id',
        'schema_version',
        'boot_id',
        'event_id',
        'linked_alarm_id',
        'source_id',
        'source_mode',
        'event_type',
        'occurred_at_ms',
        'received_at',
    ];

    protected function casts(): array
    {
        return [
            'source_id' => 'integer',
            'received_at' => 'immutable_datetime',
        ];
    }

    public function device(): BelongsTo
    {
        return $this->belongsTo(Device::class, 'device_id', 'device_id');
    }
}
