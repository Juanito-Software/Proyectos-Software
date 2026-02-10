@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-2xl mx-auto sm:px-6 lg:px-8">

        @php
            $storeRoute = auth()->user()->role === 'client'
                ? 'clients.inscriptions.store'
                : 'admin.inscriptions.store';

            $cancelRoute = auth()->user()->role === 'client'
                ? 'clients.inscriptions.index'
                : 'admin.inscriptions.index';
        @endphp

        <div class="bg-white dark:bg-gray-800 shadow-sm sm:rounded-lg mb-6">
            <div class="p-6">
                <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Crear Nueva Inscripción</h1>
                <p class="text-gray-600 dark:text-gray-400 mt-1">Completa la información de la inscripción</p>
            </div>
        </div>

        @if ($errors->any())
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                <ul class="list-disc list-inside">
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif


        <div class="bg-white dark:bg-gray-800 shadow-sm sm:rounded-lg">
            <div class="p-6">

                <form action="{{ route($storeRoute) }}" method="POST" class="space-y-6">
                    @csrf

                    <!-- ADMIN elige cliente — CLIENT no envía client_id (se obtiene del usuario) -->
                    @if(auth()->user()->role !== 'client')
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Cliente *</label>
                            <select name="client_id" required
                                    class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300">
                                <option value="">-- Selecciona un cliente --</option>
                                @foreach($clients as $client)
                                    <option value="{{ $client->id }}" {{ old('client_id') == $client->id ? 'selected' : '' }}>
                                        {{ $client->name }} ({{ $client->email }})
                                    </option>
                                @endforeach
                            </select>
                        </div>
                    @endif

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Clase *</label>
                        <select name="class_id" required
                                class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300">
                            <option value="">-- Selecciona una clase --</option>
                            @foreach($classes as $class)
                                <option value="{{ $class->id }}" {{ old('class_id') == $class->id ? 'selected' : '' }}>
                                    {{ $class->name }} (Coach: {{ $class->coach->name ?? '—' }})
                                </option>
                            @endforeach
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Fecha *</label>
                        <input type="date" name="date" value="{{ old('date') }}" required
                               class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300" />
                    </div>

                    <div class="flex justify-between pt-4">
                        <a href="{{ route($cancelRoute) }}"
                           class="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg">
                            ← Cancelar
                        </a>

                        <button type="submit"
                                class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg">
                            Crear Inscripción
                        </button>
                    </div>

                </form>

            </div>
        </div>

    </div>
</div>
@endsection
