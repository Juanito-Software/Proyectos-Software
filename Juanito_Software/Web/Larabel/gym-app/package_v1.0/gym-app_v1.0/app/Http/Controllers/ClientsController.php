<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Client;

class ClientsController extends Controller
{
    /**
     * Helper: valida si el usuario puede acceder a este client
     */
    private function canAccess(Client $client)
    {
        return auth()->user()->role === 'admin'
            || auth()->id() === $client->user_id;
    }

    /**
     * Display a listing of the resource.
     * (solo admin debería llegar aquí desde rutas)
     */
    public function index() {
        $clients = Client::all();
        return view('clients.index', compact('clients'));
    }

    public function create() {
        return view('clients.create');
    }

    public function store(Request $request) {
        $data = $request->validate([
            'name'  => 'required|string|max:100',
            'email' => 'required|email|unique:users,email',
            'phone_number' => 'nullable|digits:9',
        ], [
            'phone_number.digits' => 'El número de teléfono debe contener exactamente 9 dígitos.',
        ]);

        // Usar valor por defecto si no se proporciona phone_number
        $phoneNumber = !empty($data['phone_number']) ? $data['phone_number'] : '000000000';

        // Crear el usuario primero
        $user = \App\Models\User::create([
            'name' => $data['name'],
            'email' => $data['email'],
            'password' => bcrypt('password123'),
            'role' => 'client',
            'phone_number' => $phoneNumber,
        ]);

        // Crear el cliente asociado al usuario
        Client::create([
            'name' => $data['name'],
            'email' => $data['email'],
            'phone_number' => $phoneNumber,
            'user_id' => $user->id,
        ]);

        // Redirigir según el rol del usuario
        $prefix = auth()->user()->role === 'admin' ? 'admin.clients.index' : 'clients.index';
        return redirect()->route($prefix)->with('success', 'Cliente creado correctamente');
    }

    public function show($id) {
        $client = Client::findOrFail($id);

        if (!$this->canAccess($client)) {
            abort(403);
        }

        return view('clients.show', compact('client'));
    }

    public function edit($id) {
        $client = Client::findOrFail($id);

        if (!$this->canAccess($client)) {
            abort(403);
        }

        return view('clients.edit', compact('client'));
    }

    public function update(Request $request, $id) {
        $client = Client::findOrFail($id);

        if (!$this->canAccess($client)) {
            abort(403);
        }

        $data = $request->validate([
            'name'  => 'required|string|max:100',
            'email' => 'required|email|unique:users,email,' . $client->user_id,
            'phone_number' => 'required|digits:9',
        ], [
            'phone_number.required' => 'El número de teléfono es obligatorio.',
            'phone_number.digits' => 'El número de teléfono debe contener exactamente 9 dígitos.',
        ]);

        // Actualizar el usuario asociado
        $client->user->update([
            'name' => $data['name'],
            'email' => $data['email'],
            'phone_number' => $data['phone_number'],
        ]);

        // Actualizar el cliente
        $client->update([
            'name' => $data['name'],
            'email' => $data['email'],
            'phone_number' => $data['phone_number'],
        ]);

        // Redirigir según el rol del usuario
        $prefix = auth()->user()->role === 'admin' ? 'admin.clients.index' : 'clients.index';
        return redirect()->route($prefix)->with('success', 'Cliente actualizado correctamente');
    }

    public function destroy($id) {
        $client = Client::findOrFail($id);

        // Solo admin puede borrar
        if (auth()->user()->role !== 'admin') {
            abort(403);
        }

        $user = $client->user;
        
        // Eliminar el cliente
        $client->delete();
        
        if ($user) {
            $user->delete();
        }
        
        // Redirigir según el rol del usuario
        $prefix = auth()->user()->role === 'admin' ? 'admin.clients.index' : 'clients.index';
        return redirect()->route($prefix)->with('success', 'Cliente eliminado correctamente');
    }
}
