<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Payment;
use App\Models\Inscription;
use Illuminate\Support\Facades\Auth;

class PaymentsController extends Controller
{
    public function __construct()
    {
        // ✅ Solo admin puede gestionar pagos
        $this->middleware(['auth', 'role:admin']);
    }

    public function index()
    {
        $payments = Payment::with(['inscription.client', 'inscription.classe'])->get();
        return view('payments.index', compact('payments'));
    }

    public function create()
    {
        $inscriptions = Inscription::with(['client', 'classe'])->get();
        return view('payments.create', compact('inscriptions'));
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'inscription_id' => 'required|exists:inscriptions,id',
            'amount'         => 'required|numeric|min:0',
            'date'           => 'required|date',
        ], [
            'inscription_id.required' => 'Debe seleccionar una inscripción.',
            'inscription_id.exists' => 'La inscripción seleccionada no existe.',
            'amount.required' => 'El monto es obligatorio.',
            'amount.numeric' => 'El monto debe ser un número.',
            'amount.min' => 'El monto debe ser mayor o igual a 0.',
            'date.required' => 'La fecha es obligatoria.',
            'date.date' => 'La fecha debe ser una fecha válida.',
        ]);

        Payment::create($validated);

        return redirect()->route('admin.payments.index')->with('success', 'Pago registrado correctamente');
    }

    public function show($id)
    {
        $payment = Payment::with(['inscription.client', 'inscription.classe'])->findOrFail($id);
        return view('payments.show', compact('payment'));
    }

    public function edit($id)
    {
        $payment = Payment::findOrFail($id);
        $inscriptions = Inscription::with(['client', 'classe'])->get();
        return view('payments.edit', compact('payment', 'inscriptions'));
    }

    public function update(Request $request, $id)
    {
        $payment = Payment::findOrFail($id);

        $validated = $request->validate([
            'inscription_id' => 'required|exists:inscriptions,id',
            'amount'         => 'required|numeric|min:0',
            'date'           => 'required|date',
        ], [
            'inscription_id.required' => 'Debe seleccionar una inscripción.',
            'inscription_id.exists' => 'La inscripción seleccionada no existe.',
            'amount.required' => 'El monto es obligatorio.',
            'amount.numeric' => 'El monto debe ser un número.',
            'amount.min' => 'El monto debe ser mayor o igual a 0.',
            'date.required' => 'La fecha es obligatoria.',
            'date.date' => 'La fecha debe ser una fecha válida.',
        ]);

        $payment->update($validated);

        return redirect()->route('admin.payments.index')->with('success', 'Pago actualizado correctamente');
    }

    public function destroy($id)
    {
        Payment::findOrFail($id)->delete();
        return redirect()->route('admin.payments.index')->with('success', 'Pago eliminado correctamente');
    }
}
