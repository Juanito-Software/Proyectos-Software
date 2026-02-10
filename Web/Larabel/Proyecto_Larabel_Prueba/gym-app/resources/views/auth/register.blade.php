<x-guest-layout>
    <form method="POST" action="{{ route('register') }}">
        @csrf

        <!-- Name -->
        <div>
            <x-input-label for="name" :value="__('Name')" />
            <x-text-input id="name" class="block mt-1 w-full" type="text" name="name"
                          :value="old('name')" required autofocus autocomplete="name" />
            <x-input-error :messages="$errors->get('name')" class="mt-2" />
        </div>

        <!-- Email Address -->
        <div class="mt-4">
            <x-input-label for="email" :value="__('Email')" />
            <x-text-input id="email" class="block mt-1 w-full" type="email" name="email"
                          :value="old('email')" required autocomplete="username" />
            <x-input-error :messages="$errors->get('email')" class="mt-2" />
        </div>

        <!-- Phone Number -->
        <div class="mt-4">
            <x-input-label for="phone_number" :value="__('Phone Number')" />
            <x-text-input id="phone_number" class="block mt-1 w-full" type="text" name="phone_number"
                          :value="old('phone_number')" required maxlength="20" />
            <x-input-error :messages="$errors->get('phone_number')" class="mt-2" />
        </div>

        <!-- Tipo de usuario -->
        <div class="mt-4">
            <x-input-label :value="__('Tipo de usuario')" />
            <div class="mt-2 flex items-center gap-6">
                <label class="inline-flex items-center">
                    <input type="radio" name="role" value="client" class="form-radio"
                           {{ old('role', 'client') === 'client' ? 'checked' : '' }}>
                    <span class="ml-2">Cliente</span>
                </label>

                <label class="inline-flex items-center">
                    <input type="radio" name="role" value="coach" class="form-radio"
                           {{ old('role') === 'coach' ? 'checked' : '' }}>
                    <span class="ml-2">Entrenador</span>
                </label>
            </div>
            @error('role')
                <p class="text-sm text-red-600 mt-1">{{ $message }}</p>
            @enderror
        </div>

        <!-- Campo sport (visible solo si role=coach) -->
        <div class="mt-4" id="sport-wrapper" style="{{ old('role') === 'coach' ? '' : 'display:none;' }}">
            <x-input-label for="sport" :value="__('Deporte / Especialidad')" />
            <x-text-input id="sport" name="sport" type="text" maxlength="50"
                          class="block mt-1 w-full" :value="old('sport')" />
            <x-input-error :messages="$errors->get('sport')" class="mt-2" />
        </div>

        <!-- Password -->
        <div class="mt-4">
            <x-input-label for="password" :value="__('Password')" />
            <x-text-input id="password" class="block mt-1 w-full"
                          type="password" name="password" required autocomplete="new-password" />
            <x-input-error :messages="$errors->get('password')" class="mt-2" />
        </div>

        <!-- Confirm Password -->
        <div class="mt-4">
            <x-input-label for="password_confirmation" :value="__('Confirm Password')" />
            <x-text-input id="password_confirmation" class="block mt-1 w-full"
                          type="password" name="password_confirmation" required autocomplete="new-password" />
            <x-input-error :messages="$errors->get('password_confirmation')" class="mt-2" />
        </div>

        <div class="flex items-center justify-end mt-4">
            <a class="underline text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100
                      rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
                      dark:focus:ring-offset-gray-800"
               href="{{ route('login') }}">
                {{ __('Already registered?') }}
            </a>

            <x-primary-button class="ms-4">
                {{ __('Register') }}
            </x-primary-button>
        </div>
    </form>

    <!-- Script para mostrar/ocultar campo sport -->
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const roleRadios = document.querySelectorAll('input[name="role"]');
            const sportWrapper = document.getElementById('sport-wrapper');

            function updateSportVisibility() {
                const selected = document.querySelector('input[name="role"]:checked');
                if (selected && selected.value === 'coach') {
                    sportWrapper.style.display = '';
                } else {
                    sportWrapper.style.display = 'none';
                }
            }

            roleRadios.forEach(radio => radio.addEventListener('change', updateSportVisibility));
            updateSportVisibility();
        });
    </script>
</x-guest-layout>
