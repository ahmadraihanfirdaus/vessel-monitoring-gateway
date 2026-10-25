<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // Historical 1.0 events have no immutable alarm snapshot. Leave null;
        // never reconstruct state/reason/times from a later mutable alarm.
        Schema::table('monitoring_events', function (Blueprint $table): void {
            $table->json('alarm_metadata')->nullable();
        });
    }

    public function down(): void
    {
        Schema::table('monitoring_events', function (Blueprint $table): void {
            $table->dropColumn('alarm_metadata');
        });
    }
};
