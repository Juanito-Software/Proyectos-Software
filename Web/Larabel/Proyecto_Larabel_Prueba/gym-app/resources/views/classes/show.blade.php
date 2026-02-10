@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-4xl mx-auto sm:px-6 lg:px-8">

        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100">
                <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0">
                        <div class="h-16 w-16 bg-green-600 rounded-full flex items-center justify-center">
                            <span class="text-white text-xl font-bold">
                                {{ strtoupper(substr($class->name, 0, 2)) }}
                            </span>
                        </div>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                            {{ $class->name }}
                        </h1>
                        <p class="text-gray-600 dark:text-gray-400">
                            Detalles de la Clase
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Información de la clase -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

            <!-- Información básica -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6">
                    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                        Información de la Clase
                    </h2>

                    <div class="space-y-4">
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Nombre:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $class->name }}</span>
                        </div>

                        <div class="flex justify-between items-start py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Descripción:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100 text-right max-w-xs">
                                {{ $class->desc ?? 'Sin descripción' }}
                            </span>
                        </div>

                        <div class="flex justify-between items-center py-2">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">ID Clase:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">#{{ $class->id }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Horarios y entrenador -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6">
                    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                        Horarios y Entrenador
                    </h2>

                    <div class="space-y-4">

                        @if($class->coach)
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">👨‍🏫 Entrenador:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $class->coach->name }}</span>
                        </div>

                        @if($class->coach->sport)
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">🏃‍♂️ Especialidad:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $class->coach->sport }}</span>
                        </div>
                        @endif

                        @else
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">👨‍🏫 Entrenador:</span>
                            <span class="text-sm text-gray-500 dark:text-gray-400">Sin entrenador asignado</span>
                        </div>
                        @endif

                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">📅 Días:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $class->days ?? 'No especificado' }}</span>
                        </div>

                        <div class="flex justify-between items-center py-2">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">🕐 Horario:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">
                                {{ $class->init_hour }} - {{ $class->final_hour }}
                            </span>
                        </div>

                    </div>
                </div>
            </div>

        </div>

        <!-- Información adicional -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mt-6">
            <div class="p-6">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                    Información Adicional
                </h2>

                @php
                    $init = \Carbon\Carbon::createFromFormat('H:i:s', $class->init_hour);
                    $final = \Carbon\Carbon::createFromFormat('H:i:s', $class->final_hour);
                    $duration = $init->diffInMinutes($final);
                @endphp

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-2">
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Creada:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">
                                {{ $class->created_at->format('d/m/Y H:i') }}
                            </span>
                        </div>

                        <div class="flex justify-between items-center py-2">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Última actualización:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">
                                {{ $class->updated_at->format('d/m/Y H:i') }}
                            </span>
                        </div>
                    </div>

                    <div class="space-y-2">
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Duración:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">
                                {{ $duration }} minutos
                            </span>
                        </div>

                        <div class="flex justify-between items-center py-2">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Estado:</span>
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                Activa
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Acciones -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mt-6">
            <div class="p-6">

                <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                    Acciones
                </h2>

                <div class="flex flex-wrap gap-4">

                    {{-- ✅ Volver a lista COACH --}}
                    <a href="{{ route('coach.classes.index') }}"
                       class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                        ← Volver a la Lista
                    </a>

                    {{-- ✅ COACH NO EDITA / NO BORRA --}}
                    {{-- Nada más aquí --}}
                </div>

            </div>
        </div>

    </div>
</div>
@endsection
