@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100">
                <h1 class="text-2xl font-bold mb-4">Mis Clases</h1>
                <p class="text-gray-600 dark:text-gray-400">
                    Aquí puedes ver todas las clases que impartes junto con el número de alumnos inscritos.
                </p>
            </div>
        </div>

        @if($classes->count() > 0)
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                @foreach($classes as $class)
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                                {{ $class->name }}
                            </h3>
                            
                            @if($class->desc)
                                <p class="text-gray-600 dark:text-gray-400 text-sm mb-3">
                                    {{ $class->desc }}
                                </p>
                            @endif

                            <div class="space-y-2 mb-4">
                                <div class="flex justify-between">
                                    <span class="text-sm text-gray-500 dark:text-gray-400">Días:</span>
                                    <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ $class->days }}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-gray-500 dark:text-gray-400">Horario:</span>
                                    <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                                        {{ $class->init_hour }} - {{ $class->final_hour }}
                                    </span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-gray-500 dark:text-gray-400">Alumnos inscritos:</span>
                                    <span class="text-sm font-bold text-blue-600 dark:text-blue-400">
                                        {{ $class->inscriptions_count }}
                                    </span>
                                </div>
                            </div>

                            <div class="flex space-x-2">
                                <a href="{{ route('coach.classes.show', $class->id) }}" 
                                   class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded text-center text-sm transition duration-300">
                                    Ver Detalles
                                </a>
                            </div>
                        </div>
                    </div>
                @endforeach
            </div>
        @else
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-center">
                    <div class="text-gray-400 dark:text-gray-500 mb-4">
                        <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                        No tienes clases asignadas
                    </h3>
                    <p class="text-gray-600 dark:text-gray-400">
                        Contacta con el administrador para que te asignen clases.
                    </p>
                </div>
            </div>
        @endif

        <div class="mt-6">
            <a href="{{ route('dashboard') }}" 
               class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded transition duration-300">
                ← Volver al Dashboard
            </a>
        </div>
    </div>
</div>
@endsection
