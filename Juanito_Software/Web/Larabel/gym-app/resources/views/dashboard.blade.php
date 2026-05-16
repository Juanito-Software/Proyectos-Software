@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
        <!-- Mensaje de bienvenida -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
            <div class="p-6 text-gray-900 dark:text-gray-100">
                <h3 class="text-lg font-semibold mb-2">¡Bienvenido, {{ auth()->user()->name }}!</h3>
                <p class="text-gray-600 dark:text-gray-400">
                    Has iniciado sesión como <span class="font-semibold text-blue-600 dark:text-blue-400">{{ ucfirst(auth()->user()->role) }}</span>
                </p>
            </div>
        </div>


        <!-- Botones de navegación según el rol -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                
                @if(auth()->user()->role === 'admin')
                    <!-- Botones para Admin -->
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Gestión de Clases</h3>
                            <a href="{{ route('admin.classes.index') }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300 mb-2">
                                Ver Clases
                            </a>
                            <a href="{{ route('admin.classes.create') }}" class="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Crear Clase
                            </a>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Gestión de Entrenadores</h3>
                            <a href="{{ route('admin.coaches.index') }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300 mb-2">
                                Ver Entrenadores
                            </a>
                            <a href="{{ route('admin.coaches.create') }}" class="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Crear Entrenador
                            </a>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Gestión de Clientes</h3>
                            <a href="{{ route('admin.clients.index') }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300 mb-2">
                                Ver Clientes
                            </a>
                            <a href="{{ route('admin.clients.create') }}" class="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Crear Cliente
                            </a>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Inscripciones</h3>
                            <a href="{{ route('admin.inscriptions.index') }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300 mb-2">
                                Ver Inscripciones
                            </a>
                            <a href="{{ route('admin.inscriptions.create') }}" class="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Crear Inscripción
                            </a>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Pagos</h3>
                            <a href="{{ route('admin.payments.index') }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300 mb-2">
                                Ver Pagos
                            </a>
                            <a href="{{ route('admin.payments.create') }}" class="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Crear Pago
                            </a>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Configuración</h3>
                            <a href="{{ route('perfil') }}" class="block w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Ver Mi Perfil
                            </a>
                        </div>
                    </div>

                @elseif(auth()->user()->role === 'coach')
                    <!-- Botones para Coach -->
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mis Clases</h3>
                            <a href="{{ route('coach.classes.index') }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Ver Mis Clases
                            </a>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Configuración</h3>
                            <a href="{{ route('perfil') }}" class="block w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Ver Mi Perfil
                            </a>
                        </div>
                    </div>

                @elseif(auth()->user()->role === 'client')
                    <!-- Botones para Cliente -->
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Mis Inscripciones</h3>
                            <a href="{{ route('clients.inscriptions.index') }}" class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300 mb-2">
                                Ver Inscripciones
                            </a>
                            <a href="{{ route('clients.inscriptions.create') }}" class="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Nueva Inscripción
                            </a>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Configuración</h3>
                            <a href="{{ route('perfil') }}" class="block w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg text-center transition duration-300">
                                Ver Mi Perfil
                            </a>
                        </div>
                    </div>
                @endif

        </div>
    </div>
</div>
@endsection
