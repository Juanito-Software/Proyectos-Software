<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Coach;

class CoachesController extends Controller
{
    public function index()
    {
        $coaches = Coach::all();
        return view('coaches.index', compact('coaches'));
    }

    public function create()
    {
        return view('coaches.create');
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'name'         => 'required|string|max:100',
            'email'        => 'required|email|unique:users,email',
            'phone_number' => 'required|digits:9',
            'sport'        => 'required|string|max:50',
        ], [
            'phone_number.required' => 'El número de teléfono es obligatorio.',
            'phone_number.digits' => 'El número de teléfono debe contener exactamente 9 dígitos.',
            'sport.required' => 'El deporte es obligatorio para entrenadores.',
        ]);

        // Crear el usuario primero
        $user = \App\Models\User::create([
            'name' => $data['name'],
            'email' => $data['email'],
            'password' => bcrypt('password123'),
            'role' => 'coach',
            'phone_number' => $data['phone_number'],
        ]);

        // Crear el entrenador asociado al usuario
        Coach::create([
            'user_id' => $user->id,
            'name' => $data['name'],
            'email' => $data['email'],
            'phone_number' => $data['phone_number'],
            'sport' => $data['sport'],
        ]);

        return redirect()->route('coaches.index')->with('success', 'Entrenador creado correctamente.');
    }

    public function show($id)
    {
        $coach = Coach::findOrFail($id);
        return view('coaches.show', compact('coach'));
    }

    public function edit($id)
    {
        $coach = Coach::findOrFail($id);
        return view('coaches.edit', compact('coach'));
    }

    public function update(Request $request, $id)
    {
        $coach = Coach::findOrFail($id);

        $data = $request->validate([
            'name'         => 'required|string|max:100',
            'email'        => 'required|email|unique:users,email,' . $coach->user_id,
            'phone_number' => 'required|digits:9',
            'sport'        => 'required|string|max:50',
        ], [
            'phone_number.required' => 'El número de teléfono es obligatorio.',
            'phone_number.digits' => 'El número de teléfono debe contener exactamente 9 dígitos.',
            'sport.required' => 'El deporte es obligatorio para entrenadores.',
        ]);

        // Actualizar el usuario asociado
        if ($coach->user) {
            $coach->user->update([
                'name' => $data['name'],
                'email' => $data['email'],
                'phone_number' => $data['phone_number'],
            ]);
        }

        // Actualizar el entrenador
        $coach->update([
            'name' => $data['name'],
            'email' => $data['email'],
            'phone_number' => $data['phone_number'],
            'sport' => $data['sport'],
        ]);

        return redirect()->route('coaches.index')->with('success', 'Entrenador actualizado correctamente.');
    }

    public function destroy($id)
    {
        $coach = Coach::findOrFail($id);
        $coach->delete();

        return redirect()->route('coaches.index')->with('success', 'Entrenador eliminado correctamente.');
    }
}
