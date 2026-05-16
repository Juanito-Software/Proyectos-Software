@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">

        @php
            $prefix = auth()->user()->role === 'client' ? 'clients' : 'admin';
        @endphp

        <div class="bg-white dark:bg-gray-800 shadow-sm sm:rounded-lg mb-6">
            <div class="p-6">
                <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                    Detalles de la Inscripción
                </h1>

                <div class="space-y-4">
                    <p><strong class="text-gray-700 dark:text-gray-300">Cliente:</strong> 
                        {{ $inscription->client->name ?? 'Cliente eliminado' }}</p>
                    <p><strong class="text-gray-700 dark:text-gray-300">Clase:</strong> 
                        {{ $inscription->classe->name ?? 'Clase eliminada' }}</p>
                    <p><strong class="text-gray-700 dark:text-gray-300">Fecha de inscripción:</strong> 
                        {{ \Carbon\Carbon::parse($inscription->date)->format('d/m/Y') }}</p>
                    @if($inscription->expires_at)
                        <p><strong class="text-gray-700 dark:text-gray-300">Fecha de expiración:</strong> 
                            {{ \Carbon\Carbon::parse($inscription->expires_at)->format('d/m/Y') }}
                            @if($inscription->isActive())
                                <span class="ml-2 bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                                    Activa
                                </span>
                            @else
                                <span class="ml-2 bg-red-100 text-red-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                                    Expirada
                                </span>
                            @endif
                        </p>
                    @endif
                </div>

                <div class="mt-6">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Pagos asociados</h3>
                    @if($inscription->payments->isEmpty())
                        <p class="text-gray-600 dark:text-gray-400 mt-2">No hay pagos registrados.</p>
                    @else
                        <ul class="mt-2 space-y-2">
                            @foreach($inscription->payments as $pago)
                                <li class="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg flex justify-between">
                                    <span>💶 {{ number_format($pago->amount, 2, ',', '.') }} €</span>
                                    <span>{{ \Carbon\Carbon::parse($pago->date)->format('Y-m-d') }}</span>
                                </li>
                            @endforeach
                        </ul>
                    @endif
                </div>

                <div class="mt-6">
                    <a href="{{ route($prefix.'.inscriptions.index') }}"
                       class="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg">
                        ← Volver
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
