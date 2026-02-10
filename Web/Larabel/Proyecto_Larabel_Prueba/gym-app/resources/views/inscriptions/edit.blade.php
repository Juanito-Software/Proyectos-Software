@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-2xl mx-auto sm:px-6 lg:px-8">

        @php
            $prefix = auth()->user()->role === 'client' ? 'clients' : 'admin';
        @endphp

        <div class="bg-white dark:bg-gray-800 shadow-sm sm:rounded-lg mb-6">
            <div class="p-6">
                <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Editar Inscripción</h1>
                <p class="text-gray-600 dark:text-gray-400 mt-1">Modifica los datos de la inscripción</p>
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
                <form action="{{ route($prefix.'.inscriptions.update', $inscription->id) }}" method="POST" class="space-y-6">
                    @csrf
                    @method('PUT')

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Cliente *</label>

                        @if(auth()->user()->role === 'admin')
                            <select name="client_id" required
                                    class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300">
                                @foreach($clients as $client)
                                    <option value="{{ $client->id }}" {{ old('client_id', $inscription->client_id) == $client->id ? 'selected' : '' }}>
                                        {{ $client->name }}
                                    </option>
                                @endforeach
                            </select>
                        @else
                            <input type="hidden" name="client_id" value="{{ $inscription->client_id }}">
                            <p class="mt-1 text-gray-500 dark:text-gray-400">
                                {{ $inscription->client->name ?? 'Cliente eliminado' }}
                            </p>
                        @endif
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Clase *</label>
                        <select name="class_id" required
                                class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300">
                            @foreach($classes as $class)
                                <option value="{{ $class->id }}" {{ old('class_id', $inscription->class_id) == $class->id ? 'selected' : '' }}>
                                    {{ $class->name }}
                                </option>
                            @endforeach
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Fecha *</label>
                        <input type="date" name="date" value="{{ old('date', $inscription->date->format('Y-m-d')) }}" required
                               class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300" />
                    </div>

                    <div class="flex justify-between pt-4">
                        <a href="{{ route($prefix.'.inscriptions.index') }}"
                           class="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg">← Cancelar</a>
                        <button type="submit"
                                class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg">
                            Actualizar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
@endsection
