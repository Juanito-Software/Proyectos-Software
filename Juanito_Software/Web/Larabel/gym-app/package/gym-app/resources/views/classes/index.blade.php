@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100">
                <div class="flex justify-between items-center">
                    <div>
                        <h1 class="text-2xl font-bold">Clases del Gimnasio</h1>
                        <p class="text-gray-600 dark:text-gray-400 mt-1">
                            Gestiona todas las clases disponibles
                        </p>
                    </div>
                    @if(auth()->user()->role === 'admin' || auth()->user()->role === 'coach')
                    <a href="{{ route('admin.classes.create') }}" 
                       class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                        ➕ Nueva Clase
                    </a>
                    @endif
                </div>
            </div>
        </div>

        <!-- Mensaje de éxito -->
        @if(session('success'))
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
                {{ session('success') }}
            </div>
        @endif

        <!-- Lista de clases -->
        @if($classes->count() > 0)
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                @foreach($classes as $class)
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <div class="mb-4">
                                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                                    {{ $class->name }}
                                </h3>
                                
                                @if($class->desc)
                                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                                    {{ $class->desc }}
                                </p>
                                @endif

                                <div class="space-y-2">
                                    @if($class->coach)
                                    <div class="flex items-center">
                                        <span class="text-sm text-gray-500 dark:text-gray-400 mr-2">👨‍🏫</span>
                                        <span class="text-sm text-gray-900 dark:text-gray-100">{{ $class->coach->name }}</span>
                                    </div>
                                    @endif
                                    
                                    <div class="flex items-center">
                                        <span class="text-sm text-gray-500 dark:text-gray-400 mr-2">📅</span>
                                        <span class="text-sm text-gray-900 dark:text-gray-100">{{ $class->days }}</span>
                                    </div>
                                    
                                    <div class="flex items-center">
                                        <span class="text-sm text-gray-500 dark:text-gray-400 mr-2">🕐</span>
                                        <span class="text-sm text-gray-900 dark:text-gray-100">
                                            {{ $class->init_hour }} - {{ $class->final_hour }}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div class="flex space-x-2">
                                <a href="{{ route('admin.classes.show', $class->id) }}" 
                                   class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-3 rounded text-center text-sm transition duration-300">
                                    Ver
                                </a>
                                
                                @if(auth()->user()->role === 'admin' || auth()->user()->role === 'coach')
                                <a href="{{ route('admin.classes.edit', $class->id) }}" 
                                   class="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-3 rounded text-center text-sm transition duration-300">
                                    Editar
                                </a>
                                
                                @if(auth()->user()->role === 'admin')
                                <form action="{{ route('admin.classes.destroy', $class->id) }}" method="POST" class="flex-1">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" 
                                            onclick="return confirm('¿Eliminar clase?')"
                                            class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-3 rounded text-sm transition duration-300">
                                        Eliminar
                                    </button>
                                </form>
                                @endif
                                @endif
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
                        No hay clases registradas
                    </h3>
                    <p class="text-gray-600 dark:text-gray-400">
                        @if(auth()->user()->role === 'admin' || auth()->user()->role === 'coach')
                            Comienza agregando tu primera clase.
                        @else
                            No hay clases disponibles en este momento.
                        @endif
                    </p>
                </div>
            </div>
        @endif

        <!-- Navegación -->
        <div class="mt-6">
            <a href="{{ route('dashboard') }}" 
               class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                ← Volver al Dashboard
            </a>
        </div>
    </div>
</div>
@endsection
