@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-4xl mx-auto sm:px-6 lg:px-8">
        <!-- Header del perfil -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100">
                <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0">
                        <div class="h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center">
                            <span class="text-white text-xl font-bold">
                                {{ strtoupper(substr(auth()->user()->name, 0, 2)) }}
                            </span>
                        </div>
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                            {{ auth()->user()->name }}
                        </h1>
                        <p class="text-gray-600 dark:text-gray-400">
                            {{ ucfirst(auth()->user()->role) }}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Información del perfil -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Información personal -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6">
                    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                        Información Personal
                    </h2>
                    
                    <div class="space-y-4">
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Nombre:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ auth()->user()->name }}</span>
                        </div>
                        
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Email:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ auth()->user()->email }}</span>
                        </div>
                        
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Rol:</span>
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                                {{ ucfirst(auth()->user()->role) }}
                            </span>
                        </div>
                        
                        @if(auth()->user()->phone_number)
                        <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Teléfono:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">{{ auth()->user()->phone_number }}</span>
                        </div>
                        @endif
                        
                        <div class="flex justify-between items-center py-2">
                            <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Miembro desde:</span>
                            <span class="text-sm text-gray-900 dark:text-gray-100">
                                {{ auth()->user()->created_at->format('d/m/Y') }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Información específica del rol -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6">
                    <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                        Información de {{ ucfirst(auth()->user()->role) }}
                    </h2>
                    
                    @if(auth()->user()->role === 'client')
                        @if(auth()->user()->client)
                            <div class="space-y-4">
                                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                                    <span class="text-sm font-medium text-gray-500 dark:text-gray-400">ID Cliente:</span>
                                    <span class="text-sm text-gray-900 dark:text-gray-100">#{{ auth()->user()->client->id }}</span>
                                </div>
                                
                                @if(auth()->user()->client->birth_date)
                                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                                    <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Fecha de Nacimiento:</span>
                                    <span class="text-sm text-gray-900 dark:text-gray-100">
                                        {{ \Carbon\Carbon::parse(auth()->user()->client->birth_date)->format('d/m/Y') }}
                                    </span>
                                </div>
                                @endif
                                
                                @if(auth()->user()->client->address)
                                <div class="flex justify-between items-center py-2">
                                    <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Dirección:</span>
                                    <span class="text-sm text-gray-900 dark:text-gray-100">{{ auth()->user()->client->address }}</span>
                                </div>
                                @endif
                            </div>
                        @else
                            <div class="text-center py-8">
                                <div class="text-gray-400 dark:text-gray-500 mb-4">
                                    <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                </div>
                                <p class="text-gray-600 dark:text-gray-400">
                                    No se encontró información adicional del cliente.
                                </p>
                            </div>
                        @endif
                        
                    @elseif(auth()->user()->role === 'coach')
                        @if(auth()->user()->coach)
                            <div class="space-y-4">
                                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                                    <span class="text-sm font-medium text-gray-500 dark:text-gray-400">ID Entrenador:</span>
                                    <span class="text-sm text-gray-900 dark:text-gray-100">#{{ auth()->user()->coach->id }}</span>
                                </div>
                                
                                @if(auth()->user()->coach->sport)
                                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                                    <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Deporte:</span>
                                    <span class="text-sm text-gray-900 dark:text-gray-100">{{ auth()->user()->coach->sport }}</span>
                                </div>
                                @endif
                                
                                @if(auth()->user()->coach->specialization)
                                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                                    <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Especialización:</span>
                                    <span class="text-sm text-gray-900 dark:text-gray-100">{{ auth()->user()->coach->specialization }}</span>
                                </div>
                                @endif
                                
                                @if(auth()->user()->coach->experience_years)
                                <div class="flex justify-between items-center py-2">
                                    <span class="text-sm font-medium text-gray-500 dark:text-gray-400">Años de Experiencia:</span>
                                    <span class="text-sm text-gray-900 dark:text-gray-100">{{ auth()->user()->coach->experience_years }}</span>
                                </div>
                                @endif
                            </div>
                        @else
                            <div class="text-center py-8">
                                <div class="text-gray-400 dark:text-gray-500 mb-4">
                                    <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                </div>
                                <p class="text-gray-600 dark:text-gray-400">
                                    No se encontró información adicional del entrenador.
                                </p>
                            </div>
                        @endif
                        
                    @elseif(auth()->user()->role === 'admin')
                        <div class="text-center py-8">
                            <div class="text-blue-400 dark:text-blue-500 mb-4">
                                <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                </svg>
                            </div>
                            <p class="text-gray-600 dark:text-gray-400">
                                Tienes acceso completo al sistema como administrador.
                            </p>
                        </div>
                    @endif
                </div>
            </div>
        </div>

        <!-- Acciones del perfil -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mt-6">
            <div class="p-6">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                    Acciones
                </h2>
                
                <div class="flex flex-wrap gap-4">
                    <a href="{{ route('profile.edit') }}" 
                       class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                        Editar Perfil
                    </a>
                    
                    <a href="{{ route('dashboard') }}" 
                       class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                        Volver al Dashboard
                    </a>
                    
                    @if(auth()->user()->role === 'client')
                        <a href="{{ route('clients.inscriptions.index') }}" 
                           class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            Mis Inscripciones
                        </a>
                    @elseif(auth()->user()->role === 'coach')
                        <a href="{{ route('coach.classes.index') }}" 
                           class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            Mis Clases
                        </a>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
