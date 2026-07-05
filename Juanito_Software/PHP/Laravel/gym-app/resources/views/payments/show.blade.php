@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-2xl mx-auto sm:px-6 lg:px-8">
        <div class="bg-white dark:bg-gray-800 shadow sm:rounded-lg p-6">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">Detalles del Pago</h1>

            <div class="space-y-3 text-gray-800 dark:text-gray-200">
                <p><strong>Cliente:</strong> {{ $payment->inscription->client->name ?? 'Cliente eliminado' }}</p>
                <p><strong>Clase:</strong> {{ $payment->inscription->classe->name ?? 'Clase eliminada' }}</p>
                <p><strong>Fecha Inscripción:</strong> {{ $payment->inscription->date->format('Y-m-d') }}</p>
                <p><strong>Monto:</strong> {{ number_format($payment->amount, 2) }} €</p>
                <p><strong>Fecha Pago:</strong> {{ $payment->date->format('Y-m-d') }}</p>
            </div>

            <div class="flex justify-between pt-6">
                <a href="{{ route('admin.payments.index') }}"
                   class="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg">← Volver</a>
                <a href="{{ route('admin.payments.edit', $payment->id) }}"
                   class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg">Editar</a>
            </div>
        </div>
    </div>
</div>
@endsection
