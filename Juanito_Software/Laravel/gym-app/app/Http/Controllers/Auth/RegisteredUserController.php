<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Client;
use App\Models\Coach;
use App\Providers\RouteServiceProvider;
use Illuminate\Auth\Events\Registered;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rules;
use Illuminate\View\View;

class RegisteredUserController extends Controller
{
    public function create(): View
    {
        return view('auth.register');
    }

    public function store(Request $request): RedirectResponse
    {
        $request->validate([
            'name'          => ['required', 'string', 'max:255'],
            'email'         => ['required', 'string', 'lowercase', 'email', 'max:255', 'unique:users,email'],
            'password' => [
                'required',
                'string',
                'confirmed',
                \Illuminate\Validation\Rules\Password::min(8)
                    ->mixedCase()      // al menos mayúscula y minúscula
                    ->letters()         // al menos una letra
                    ->numbers()         // al menos un número
                    ->symbols()         // al menos un símbolo
                    ->uncompromised(),  // evita contraseñas filtradas
            ],

            'phone_number'  => ['required', 'string', 'size:9'],
            'role'          => ['required', 'in:client,coach'],
            'sport'         => ['nullable', 'string', 'max:50'],
        ]);

        $role = $request->input('role') === 'coach' ? 'coach' : 'client';

        if ($role === 'coach' && ! $request->filled('sport')) {
            return back()
                ->withInput($request->except('password', 'password_confirmation'))
                ->withErrors(['sport' => 'El campo "sport" es obligatorio para entrenadores.']);
        }

        $phone = $request->input('phone_number');

        if (strlen($phone) !== 9) {
            return back()
                ->withInput($request->except('password', 'password_confirmation'))
                ->withErrors(['phone_number' => 'El número de teléfono debe tener exactamente 9 dígitos.']);
        }

        $user = User::create([
            'name'         => $request->name,
            'email'        => $request->email,
            'password'     => Hash::make($request->password),
            'phone_number' => $request->phone_number,
            'role'         => $role,
        ]);

        if ($role === 'client') {
            Client::create([
                'user_id'      => $user->id,
                'name'         => $user->name,
                'email'        => $user->email,
                'phone_number' => $user->phone_number,
            ]);
        } else {
            Coach::create([
                'user_id'      => $user->id,
                'name'         => $user->name,
                'email'        => $user->email,
                'phone_number' => $user->phone_number,
                'sport'        => $request->sport,
            ]);
        }

        event(new Registered($user));
        Auth::login($user);

        return redirect(RouteServiceProvider::HOME);
    }
}
