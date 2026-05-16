<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Models\Inscription;
use App\Models\Client;
use App\Models\Classe;

class InscriptionsController extends Controller
{
    public function index()
    {
        $user = Auth::user();

        if ($user->role === 'client') {
            $client = $user->client;
            if (!$client) {
                abort(403, 'No tienes un perfil de cliente.');
            }
            $inscriptions = Inscription::with(['client', 'classe', 'payments'])
                ->where('client_id', $client->id)
                ->get();
        } else {
            $inscriptions = Inscription::with(['client', 'classe', 'payments'])->get();
        }

        return view('inscriptions.index', compact('inscriptions'));
    }


    public function create()
    {
        $user = Auth::user();

        $clients = ($user->role !== 'client') ? Client::all() : collect();
        $classes = Classe::all();

        return view('inscriptions.create', compact('clients', 'classes'));
    }


    public function store(Request $request)
    {
        $user = Auth::user();

        // Validaciones base
        $validationRules = [
            'class_id' => 'required|exists:classes,id',
            'date'     => 'required|date',
        ];

        $validationMessages = [
            'class_id.required' => 'Debe seleccionar una clase.',
            'class_id.exists' => 'La clase seleccionada no existe.',
            'date.required' => 'La fecha es obligatoria.',
            'date.date' => 'La fecha debe ser una fecha válida.',
        ];

        // ✅ Forzar client_id según el rol
        if ($user->role === 'client') {
            $client = $user->client;
            if (! $client) {
                abort(403, 'No tienes un perfil de cliente.');
            }
            $clientId = $client->id;
        } else {
            // Admin debe seleccionar cliente
            $validationRules['client_id'] = 'required|exists:clients,id';
            $validationMessages['client_id.required'] = 'Debe seleccionar un cliente.';
            $validationMessages['client_id.exists'] = 'El cliente seleccionado no existe.';
            
            $request->validate($validationRules, $validationMessages);
            $clientId = $request->input('client_id');
        }

        // Validar sin client_id para clientes
        if ($user->role === 'client') {
            $request->validate($validationRules, $validationMessages);
        }

        // Verificar si ya existe una inscripción ACTIVA para esta clase
        $activeInscription = Inscription::where('client_id', $clientId)
            ->where('class_id', $request->class_id)
            ->active()
            ->first();

        if ($activeInscription) {
            return back()->withErrors([
                'class_id' => 'Ya tienes una inscripción activa para esta clase. La inscripción expira el ' . $activeInscription->expires_at->format('d/m/Y') . '. Debes esperar a que expire o renovarla.'
            ])->withInput();
        }

        // Calcular fecha de expiración (1 mes desde la fecha de inscripción)
        $inscriptionDate = \Carbon\Carbon::parse($request->date);
        $expiresAt = $inscriptionDate->copy()->addMonth();

        Inscription::create([
            'client_id' => $clientId,
            'class_id'  => $request->class_id,
            'date'      => $request->date,
            'expires_at' => $expiresAt->toDateString(),
        ]);

        // Redirigir según el rol
        $redirectRoute = $user->role === 'client' 
            ? 'clients.inscriptions.index' 
            : 'admin.inscriptions.index';

        return redirect()->route($redirectRoute)
            ->with('success', 'Inscripción creada correctamente.');
    }


    public function show($id)
    {
        $inscription = Inscription::with(['client', 'classe', 'payments'])->findOrFail($id);

        // ✅ Debe ser dueño
        if (Auth::user()->role === 'client' &&
            $inscription->client_id !== Auth::user()->client->id) {
            abort(403, 'No autorizado');
        }

        $inscription->payments = $inscription->payments->sortByDesc('date');

        return view('inscriptions.show', compact('inscription'));
    }


    public function edit($id)
    {
        $inscription = Inscription::findOrFail($id);

        // ✅ Debe ser dueño
        if (Auth::user()->role === 'client' &&
            $inscription->client_id !== Auth::user()->client->id) {
            abort(403, 'No autorizado');
        }

        $clients = Client::all();
        $classes = Classe::with('coach')->get();

        return view('inscriptions.edit', compact('inscription', 'clients', 'classes'));
    }


    public function update(Request $request, $id)
    {
        $inscription = Inscription::findOrFail($id);

        // ✅ Debe ser dueño
        if (Auth::user()->role === 'client' &&
            $inscription->client_id !== Auth::user()->client->id) {
            abort(403, 'No autorizado');
        }

        $data = $request->validate([
            'client_id' => 'required|exists:clients,id',
            'class_id'  => 'required|exists:classes,id',
            'date'      => 'required|date',
        ], [
            'client_id.required' => 'Debe seleccionar un cliente.',
            'client_id.exists' => 'El cliente seleccionado no existe.',
            'class_id.required' => 'Debe seleccionar una clase.',
            'class_id.exists' => 'La clase seleccionada no existe.',
            'date.required' => 'La fecha es obligatoria.',
            'date.date' => 'La fecha debe ser una fecha válida.',
        ]);

        // ✅ Cliente NO puede manipular client_id
        if (Auth::user()->role === 'client') {
            $data['client_id'] = Auth::user()->client->id;
        }

        // Verificar si hay otra inscripción ACTIVA para esta clase (excluyendo la actual)
        $activeInscription = Inscription::where('client_id', $data['client_id'])
            ->where('class_id', $data['class_id'])
            ->where('id', '!=', $inscription->id)
            ->active()
            ->first();

        if ($activeInscription) {
            return back()->withErrors([
                'class_id' => 'Ya existe otra inscripción activa para esta clase. La inscripción expira el ' . $activeInscription->expires_at->format('d/m/Y') . '.'
            ])->withInput();
        }

        // Recalcular fecha de expiración si se cambió la fecha
        if ($inscription->date != $data['date']) {
            $inscriptionDate = \Carbon\Carbon::parse($data['date']);
            $data['expires_at'] = $inscriptionDate->copy()->addMonth()->toDateString();
        }

        $inscription->update($data);

        // Redirigir según el rol
        $redirectRoute = Auth::user()->role === 'client' 
            ? 'clients.inscriptions.index' 
            : 'admin.inscriptions.index';

        return redirect()->route($redirectRoute)
            ->with('success', 'Inscripción actualizada correctamente.');
    }


    public function destroy($id)
    {
        $inscription = Inscription::findOrFail($id);

        // ✅ Debe ser dueño
        if (Auth::user()->role === 'client' &&
            $inscription->client_id !== Auth::user()->client->id) {
            abort(403, 'No autorizado');
        }

        $inscription->payments()->delete();
        $inscription->delete();

        // Redirigir según el rol
        $redirectRoute = Auth::user()->role === 'client' 
            ? 'clients.inscriptions.index' 
            : 'admin.inscriptions.index';

        return redirect()->route($redirectRoute)
            ->with('success', 'Inscripción y pagos asociados eliminados correctamente.');
    }
}
