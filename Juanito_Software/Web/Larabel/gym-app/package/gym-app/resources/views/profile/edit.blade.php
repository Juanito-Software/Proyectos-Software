@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-4xl mx-auto sm:px-6 lg:px-8 space-y-6">
        <!-- Información del perfil -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
            <div class="p-6">
                <header class="mb-6">
                    <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                        Información del Perfil
                    </h2>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        Actualiza la información de tu cuenta y dirección de email.
                    </p>
                </header>

                <form method="post" action="{{ route('profile.update') }}" class="space-y-6">
                    @csrf
                    @method('patch')

                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Nombre
                        </label>
                        <input id="name" name="name" type="text" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('name', $user->name) }}" required autofocus autocomplete="name" />
                        @error('name')
                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Email
                        </label>
                        <input id="email" name="email" type="email" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('email', $user->email) }}" required autocomplete="username" />
                        @error('email')
                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                        @enderror

                        @if ($user instanceof \Illuminate\Contracts\Auth\MustVerifyEmail && ! $user->hasVerifiedEmail())
                            <div class="mt-2">
                                <p class="text-sm text-gray-800 dark:text-gray-200">
                                    Tu dirección de email no está verificada.
                                    <button form="send-verification" class="underline text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:focus:ring-offset-gray-800">
                                        Haz clic aquí para reenviar el email de verificación.
                                    </button>
                                </p>

                                @if (session('status') === 'verification-link-sent')
                                    <p class="mt-2 font-medium text-sm text-green-600 dark:text-green-400">
                                        Se ha enviado un nuevo enlace de verificación a tu dirección de email.
                                    </p>
                                @endif
                            </div>
                        @endif
                    </div>

                    @if(auth()->user()->phone_number !== null)
                    <div>
                        <label for="phone_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Número de Teléfono
                        </label>
                        <input id="phone_number" name="phone_number" type="tel" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('phone_number', $user->phone_number) }}" autocomplete="tel" />
                        @error('phone_number')
                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                        @enderror
                    </div>
                    @endif

                    @if(auth()->user()->role === 'coach' && auth()->user()->coach)
                    <div>
                        <label for="sport" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Deporte/Especialidad
                        </label>
                        <input id="sport" name="sport" type="text" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               value="{{ old('sport', auth()->user()->coach->sport) }}" placeholder="Ej: Fútbol, Natación, Crossfit..." />
                        @error('sport')
                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                        @enderror
                    </div>
                    @endif

                    <div class="flex items-center gap-4">
                        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            Guardar
                        </button>

                        @if (session('status') === 'profile-updated')
                            <p class="text-sm text-green-600 dark:text-green-400">
                                ¡Guardado!
                            </p>
                        @endif
                    </div>
                </form>

                <form id="send-verification" method="post" action="{{ route('verification.send') }}">
                    @csrf
                </form>
            </div>
        </div>

        <!-- Cambiar contraseña -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
            <div class="p-6">
                <header class="mb-6">
                    <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                        Cambiar Contraseña
        </h2>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        Asegúrate de que tu cuenta esté usando una contraseña larga y aleatoria para mantenerla segura.
                    </p>
                </header>

                <form method="post" action="{{ route('password.update') }}" class="space-y-6">
                    @csrf
                    @method('put')

                    <div>
                        <label for="current_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Contraseña Actual
                        </label>
                        <input id="current_password" name="current_password" type="password" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               autocomplete="current-password" />
                        @error('current_password')
                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Nueva Contraseña
                        </label>
                        <input id="password" name="password" type="password" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               autocomplete="new-password" />
                        @error('password')
                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                        @enderror
                    </div>

                    <div>
                        <label for="password_confirmation" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Confirmar Nueva Contraseña
                        </label>
                        <input id="password_confirmation" name="password_confirmation" type="password" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               autocomplete="new-password" />
                        @error('password_confirmation')
                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                        @enderror
                    </div>

                    <div class="flex items-center gap-4">
                        <button type="submit" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            Actualizar Contraseña
                        </button>

                        @if (session('status') === 'password-updated')
                            <p class="text-sm text-green-600 dark:text-green-400">
                                Contraseña actualizada.
                            </p>
                        @endif
                </div>
                </form>
            </div>
        </div>

        <!-- Eliminar cuenta -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
            <div class="p-6">
                <header class="mb-6">
                    <h2 class="text-lg font-medium text-red-600 dark:text-red-400">
                        Eliminar Cuenta
                    </h2>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        Una vez que se elimine tu cuenta, todos sus recursos y datos se eliminarán permanentemente. Antes de eliminar tu cuenta, descarga cualquier dato o información que desees conservar.
                    </p>
                </header>

                <button type="button" 
                        class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
                        onclick="confirmDelete()">
                    Eliminar Cuenta
                </button>

                <form id="delete-form" method="post" action="{{ route('profile.destroy') }}" class="hidden">
                    @csrf
                    @method('delete')
                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Contraseña
                        </label>
                        <input id="password" name="password" type="password" 
                               class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:focus:border-indigo-400 dark:focus:ring-indigo-400" 
                               placeholder="Contraseña" />
                        @error('password')
                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">{{ $message }}</p>
                        @enderror
                    </div>
                    <div class="mt-4">
                        <button type="submit" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                            Eliminar Cuenta
                        </button>
                </div>
                </form>
            </div>
        </div>

        <!-- Navegación -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
            <div class="p-6">
                <div class="flex flex-wrap gap-4">
                    <a href="{{ route('perfil') }}" 
                       class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                        ← Volver al Perfil
                    </a>
                    
                    <a href="{{ route('dashboard') }}" 
                       class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                        Ir al Dashboard
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function confirmDelete() {
    if (confirm('¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.')) {
        document.getElementById('delete-form').classList.remove('hidden');
    }
}
</script>
@endsection
