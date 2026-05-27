@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-2xl mx-auto sm:px-6 lg:px-8">
        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100">
                <h1 class="text-2xl font-bold">Editar Clase</h1>
                <p class="text-gray-600 dark:text-gray-400 mt-1">
                    Modifica la información de la clase: {{ $class->name }}
                </p>
            </div>
        </div>

        <!-- Formulario -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
            <div class="p-6">
                <!-- Mostrar mensajes de error -->
                @if ($errors->any())
                    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                        <h4 class="font-bold">Por favor corrige los siguientes errores:</h4>
                        <ul class="list-disc list-inside mt-2">
                            @foreach ($errors->all() as $error)
                                <li>{{ $error }}</li>
                            @endforeach
                        </ul>
                    </div>
                @endif

                <form action="{{ route('admin.classes.update', $class->id) }}" method="POST" class="space-y-6">
                    @csrf
                    @method('PUT')
                    
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Nombre de la Clase *
                        </label>
                        <input id="name" name="name" type="text" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('name', $class->name) }}" required autofocus 
                               placeholder="Ej: Crossfit, Yoga, Spinning..." />
                    </div>

                    <div>
                        <label for="desc" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Descripción
                        </label>
                        <textarea id="desc" name="desc" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400"
                                  placeholder="Describe brevemente la clase...">{{ old('desc', $class->desc) }}</textarea>
                    </div>

                    <div>
                        <label for="coach_id" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Entrenador *
                        </label>
                        <select id="coach_id" name="coach_id" required
                                class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400">
                            <option value="">-- Selecciona un entrenador --</option>
                            @foreach($coaches as $coach)
                                <option value="{{ $coach->id }}" {{ old('coach_id', $class->coach_id) == $coach->id ? 'selected' : '' }}>
                                    {{ $coach->name }} ({{ $coach->sport ?? 'Sin especialidad' }})
                                </option>
                            @endforeach
                        </select>
                    </div>

                    <div>
                        <label for="days" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Días de la Semana *
                        </label>
                        <input id="days" name="days" type="text" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('days', $class->days) }}" required
                               placeholder="Ej: Lunes, Miércoles, Viernes" />
                        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            Especifica los días de la semana
                        </p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label for="init_hour" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                Hora de Inicio *
                            </label>
                            <input id="init_hour" name="init_hour" type="time" 
                                   class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                                   value="{{ old('init_hour', $class->init_hour) }}" required />
                        </div>

                        <div>
                            <label for="final_hour" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                Hora de Fin *
                            </label>
                            <input id="final_hour" name="final_hour" type="time" 
                                   class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                                   value="{{ old('final_hour', $class->final_hour) }}" required />
                        </div>
                    </div>

                    <div class="flex items-center justify-between pt-6">
                        <a href="{{ route('admin.classes.index') }}" 
                           class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            ← Cancelar
                        </a>
                        
                        <button type="submit" 
                                class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            Actualizar Clase
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
@endsection
