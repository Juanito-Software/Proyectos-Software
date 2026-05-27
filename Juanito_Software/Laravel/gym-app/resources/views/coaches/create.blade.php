@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-2xl mx-auto sm:px-6 lg:px-8">
        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100">
                <h1 class="text-2xl font-bold">Crear Nuevo Entrenador</h1>
                <p class="text-gray-600 dark:text-gray-400 mt-1">
                    Agrega un nuevo entrenador al equipo del gimnasio
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

                <form action="{{ route('admin.coaches.store') }}" method="POST" class="space-y-6">
                    @csrf
                    
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Nombre Completo *
                        </label>
                        <input id="name" name="name" type="text" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('name') }}" required autofocus />
                    </div>

                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Email *
                        </label>
                        <input id="email" name="email" type="email" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('email') }}" required />
                    </div>

                    <div>
                        <label for="phone_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Número de Teléfono
                        </label>
                        <input id="phone_number" name="phone_number" type="tel" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('phone_number') }}" 
                               placeholder="Ej: 123456789" />
                        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            Número de teléfono opcional
                        </p>
                    </div>

                    <div>
                        <label for="sport" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Especialidad / Deporte
                        </label>
                        <input id="sport" name="sport" type="text" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('sport') }}" 
                               placeholder="Ej: Crossfit, Natación, Fútbol, Yoga..." />
                        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            Especialidad deportiva del entrenador
                        </p>
                    </div>

                    <div class="flex items-center justify-between pt-6">
                        <a href="{{ route('admin.coaches.index') }}" 
                           class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            ← Cancelar
                        </a>
                        
                        <button type="submit" 
                                class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            Crear Entrenador
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
@endsection
