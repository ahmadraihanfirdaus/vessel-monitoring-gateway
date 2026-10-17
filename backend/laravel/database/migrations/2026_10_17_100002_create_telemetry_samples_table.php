<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('telemetry_samples', function (Blueprint $table): void {
            $table->id();
            $table->string('device_id', 48)->collation('utf8mb4_bin');
            $table->string('schema_version', 16);
            $table->string('firmware_version', 48)->collation('utf8mb4_bin');
            $table->string('boot_id', 48)->collation('utf8mb4_bin');
            $table->unsignedBigInteger('sequence');
            $table->unsignedBigInteger('uptime_ms');
            $table->string('source_mode', 16);
            $table->timestamp('received_at');
            $table->timestamps();

            $table->foreign('device_id', 'telemetry_samples_device_id_foreign')
                ->references('device_id')
                ->on('devices')
                ->cascadeOnDelete();

            $table->unique(
                ['device_id', 'boot_id', 'sequence'],
                'telemetry_samples_identity_unique'
            );
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('telemetry_samples');
    }
};
