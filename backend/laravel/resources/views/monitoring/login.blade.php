<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Monitoring sign-in</title></head>
<body><main><h1>Monitoring sign-in</h1><p>Read-only development monitoring. Akun dan akses perangkat disiapkan melalui CLI lokal.</p>
@if($errors->any())<p role="alert">Sign-in failed.</p>@endif
<form method="post" action="{{ url('/login') }}">@csrf
<label>Email <input type="email" name="email" maxlength="254" required autocomplete="username" value="{{ old('email') }}"></label>
<label>Password <input type="password" name="password" maxlength="72" required autocomplete="current-password"></label>
<button type="submit">Sign in</button></form></main></body></html>
