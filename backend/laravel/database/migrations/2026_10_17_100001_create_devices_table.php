<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('devices', function (Blueprint $table): void {
            $table->id();
            $table->string('device_id', 48)->collation('utf8mb4_bin')->unique();
            $table->char('token_digest', 64)->collation('utf8mb4_bin')->unique();
            $table->boolean('enabled')->default(false);
            $table->timestamp('last_seen_at')->nullable();
            $table->string('last_boot_id', 48)->collation('utf8mb4_bin')->nullable();
            $table->unsignedBigInteger('last_sequence')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('devices');
    }
};
