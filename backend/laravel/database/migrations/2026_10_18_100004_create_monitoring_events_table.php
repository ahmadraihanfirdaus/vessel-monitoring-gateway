<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('monitoring_events', function (Blueprint $table): void {
            $table->id();
            $table->string('device_id', 48)->collation('utf8mb4_bin');
            $table->string('schema_version', 16);
            $table->string('boot_id', 48)->collation('utf8mb4_bin');
            $table->unsignedBigInteger('event_id');
            $table->unsignedBigInteger('linked_alarm_id');
            $table->unsignedBigInteger('source_id');
            $table->string('source_mode', 16);
            $table->string('event_type', 32);
            $table->unsignedBigInteger('occurred_at_ms');
            $table->timestamp('received_at');

            $table->foreign('device_id')
                ->references('device_id')
                ->on('devices')
                ->cascadeOnDelete();

            $table->unique(
                ['device_id', 'boot_id', 'event_id'],
                'monitoring_events_identity_unique'
            );

            $table->index(
                ['device_id', 'occurred_at_ms'],
                'monitoring_events_device_occurred_idx'
            );

            $table->index(
                ['device_id', 'event_type', 'occurred_at_ms'],
                'monitoring_events_device_type_occurred_idx'
            );
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('monitoring_events');
    }
};
