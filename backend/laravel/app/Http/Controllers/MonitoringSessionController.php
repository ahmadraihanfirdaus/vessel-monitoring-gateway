<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class MonitoringSessionController extends Controller
{
    public function create()
    {
        return view('monitoring.login');
    }

    public function store(Request $request)
    {
        $data = $request->validate(['email' => ['required', 'string', 'email', 'max:254'], 'password' => ['required', 'string', 'max:72']]);
        // Bcrypt accepts only 72 bytes, independent of Unicode character count.
        if (strlen($data['password']) > 72) {
            return back()->withErrors(['email' => 'Sign-in failed.'])->onlyInput('email');
        }
        $credentials = ['email' => strtolower($data['email']), 'password' => $data['password'],
            static fn ($query) => $query->whereNull('disabled_at')];
        if (! Auth::guard('web')->attempt($credentials, false)) {
            // One message for unknown, disabled and incorrect credentials.
            return back()->withErrors(['email' => 'Sign-in failed.'])->onlyInput('email');
        }
        $request->session()->regenerate();

        return redirect()->route('monitoring.index');
    }

    public function destroy(Request $request)
    {
        Auth::guard('web')->logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect()->route('login');
    }
}
