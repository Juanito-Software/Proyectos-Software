@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-4xl mx-auto sm:px-6 lg:px-8">

        @php
            $prefix = auth()->user()->role === 'client' ? 'clients' : 'admin';
        @endphp

        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100 flex items-center space-x-4">
                <div class="flex-shrink-0">
                    <div class="h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center">
                        <span class="text-white text-xl font-bold">
                            {{ strtoupper(substr($client->name, 0, 2)) }}
                        </span>
                    </div>
                </div>
                <div>
                    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {{ $client->name }}
                    </h1>
                    <p class="text-gray-600 dark:text-gray-400">
                        Detalles del Cliente
                    </p>
                </div>
            </div>
        </div>

        <!-- Información del cliente -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6">
                    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Información Personal</h2>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Nombre:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $client->name }}</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Email:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $client->email }}</span>
                        </div>
                        <div class="flex justify-between items-center py-2">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Teléfono:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $client->phone_number ?? 'No proporcionado' }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6">
                    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Información Adicional</h2>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">ID Cliente:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">#{{ $client->id }}</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Registrado:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $client->created_at->format('d/m/Y') }}</span>
                        </div>
                        <div class="flex justify-between items-center py-2">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Última actualización:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ $client->updated_at->format('d/m/Y H:i') }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Acciones -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mt-6">
            <div class="p-6 flex flex-wrap gap-4">
                <a href="{{ route($prefix.'.clients.index') }}" 
                   class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                    ← Volver a la Lista
                </a>
                
                @if(auth()->user()->role === 'admin')
                <a href="{{ route($prefix.'.clients.edit', $client->id) }}" 
                   class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                    Editar Cliente
                </a>
                
                <form action="{{ route($prefix.'.clients.destroy', $client->id) }}" method="POST" class="inline">
                    @csrf
                    @method('DELETE')
                    <button type="submit" 
                            onclick="return confirm('¿Seguro que deseas eliminar este cliente?')"
                            class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                        Eliminar Cliente
                    </button>
                </form>
                @endif
            </div>
        </div>
    </div>
</div>
@endsection
