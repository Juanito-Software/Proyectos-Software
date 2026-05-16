@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">

        @php
            $prefix = auth()->user()->role === 'client' ? 'clients' : 'admin';
        @endphp

        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100 flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold">Lista de Clientes</h1>
                    <p class="text-gray-600 dark:text-gray-400 mt-1">
                        Gestiona todos los clientes del gimnasio
                    </p>
                </div>
                @if(auth()->user()->role === 'admin')
                <a href="{{ route($prefix.'.clients.create') }}" 
                   class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                    ➕ Nuevo Cliente
                </a>
                @endif
            </div>
        </div>

        <!-- Lista de clientes -->
        @if($clients->count() > 0)
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                @foreach($clients as $client)
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <div class="flex items-center space-x-3 mb-4">
                                <div class="h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center">
                                    <span class="text-white text-lg font-bold">
                                        {{ strtoupper(substr($client->name, 0, 2)) }}
                                    </span>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                                        {{ $client->name }}
                                    </h3>
                                    <p class="text-sm text-gray-600 dark:text-gray-400">
                                        {{ $client->email }}
                                    </p>
                                </div>
                            </div>

                            @if($client->phone_number)
                            <div class="mb-4">
                                <p class="text-sm text-gray-500 dark:text-gray-400">
                                    📞 {{ $client->phone_number }}
                                </p>
                            </div>
                            @endif

                            <div class="flex space-x-2">
                                <a href="{{ route($prefix.'.clients.show', $client->id) }}" 
                                   class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-3 rounded text-center text-sm transition duration-300">
                                    Ver
                                </a>
                                
                                @if(auth()->user()->role === 'admin')
                                <a href="{{ route($prefix.'.clients.edit', $client->id) }}" 
                                   class="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-3 rounded text-center text-sm transition duration-300">
                                    Editar
                                </a>
                                
                                <form action="{{ route($prefix.'.clients.destroy', $client->id) }}" method="POST" class="flex-1">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" 
                                            onclick="return confirm('¿Seguro que deseas eliminar este cliente?')"
                                            class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-3 rounded text-sm transition duration-300">
                                        Eliminar
                                    </button>
                                </form>
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
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                        No hay clientes registrados
                    </h3>
                    <p class="text-gray-600 dark:text-gray-400">
                        @if(auth()->user()->role === 'admin')
                            Comienza agregando tu primer cliente.
                        @else
                            No tienes clientes asignados.
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
