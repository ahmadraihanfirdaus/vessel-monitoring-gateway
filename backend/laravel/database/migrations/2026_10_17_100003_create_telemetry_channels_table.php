<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('telemetry_channels', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('telemetry_sample_id')
                ->constrained('telemetry_samples')
                ->cascadeOnDelete();
            $table->string('name', 32)->collation('utf8mb4_bin');
            $table->string('quality', 16);
            $table->double('value')->nullable();
            $table->timestamps();

            $table->unique(
                ['telemetry_sample_id', 'name'],
                'telemetry_channels_sample_name_unique'
            );
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('telemetry_channels');
    }
};
