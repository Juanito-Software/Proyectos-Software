@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-5xl mx-auto sm:px-6 lg:px-8">

        @php
            // Definimos prefijo dinámico según rol
            $prefix = auth()->user()->role === 'client' ? 'clients' : 'admin';
        @endphp

        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Inscripciones</h1>
                    <p class="text-gray-600 dark:text-gray-400 mt-1">Gestión de inscripciones y pagos</p>
                </div>
                <a href="{{ route($prefix.'.inscriptions.create') }}" 
                   class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                    ➕ Nueva Inscripción
                </a>
            </div>
        </div>

        <!-- Mensajes -->
        @if(session('success'))
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
                {{ session('success') }}
            </div>
        @endif

        <!-- Lista -->
        @if($inscriptions->count())
            <div class="space-y-4">
                @foreach($inscriptions as $ins)
                    <div class="bg-white dark:bg-gray-800 shadow-sm sm:rounded-lg p-6 flex justify-between items-center">
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-2">
                                <h2 class="font-semibold text-lg text-gray-900 dark:text-gray-100">
                                    {{ $ins->client->name ?? 'Cliente eliminado' }}
                                </h2>
                                @if($ins->expires_at)
                                    @if($ins->isActive())
                                        <span class="bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                                            Activa
                                        </span>
                                    @else
                                        <span class="bg-red-100 text-red-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                                            Expirada
                                        </span>
                                    @endif
                                @endif
                            </div>
                            <p class="text-gray-600 dark:text-gray-400 text-sm">
                                Clase: {{ $ins->classe->name ?? 'Clase eliminada' }} —
                                Fecha inscripción: {{ \Carbon\Carbon::parse($ins->date)->format('d/m/Y') }}
                                @if($ins->expires_at)
                                    — Expira: {{ \Carbon\Carbon::parse($ins->expires_at)->format('d/m/Y') }}
                                @endif
                            </p>
                        </div>
                        <div class="flex space-x-2">
                            <a href="{{ route($prefix.'.inscriptions.show', $ins->id) }}" 
                               class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded text-sm">Ver</a>
                            <a href="{{ route($prefix.'.inscriptions.edit', $ins->id) }}" 
                               class="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded text-sm">Editar</a>
                            <form action="{{ route($prefix.'.inscriptions.destroy', $ins->id) }}" method="POST" onsubmit="return confirm('¿Eliminar inscripción?')">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded text-sm">
                                    Eliminar
                                </button>
                            </form>
                        </div>
                    </div>
                @endforeach
            </div>
        @else
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-center text-gray-600 dark:text-gray-400">
                    No hay inscripciones registradas todavía.
                </div>
            </div>
        @endif

        <!-- BOTÓN VOLVER -->
        <div class="mt-6">
            <a href="{{ route('dashboard') }}" 
               class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                ← Volver al Dashboard
            </a>
        </div>

    </div>
</div>
@endsection
