@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-2xl mx-auto sm:px-6 lg:px-8">
        <div class="bg-white dark:bg-gray-800 shadow sm:rounded-lg p-6">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">Registrar Pago</h1>

            @if ($errors->any())
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    <ul class="list-disc list-inside">
                        @foreach ($errors->all() as $error)
                            <li>{{ $error }}</li>
                        @endforeach
                    </ul>
                </div>
            @endif

            <form action="{{ route('admin.payments.store') }}" method="POST" class="space-y-6">
                @csrf

                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Inscripción *</label>
                    <select name="inscription_id" required
                            class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300">
                        <option value="">-- Selecciona una inscripción --</option>
                        @foreach($inscriptions as $ins)
                            <option value="{{ $ins->id }}" {{ old('inscription_id') == $ins->id ? 'selected' : '' }}>
                                {{ $ins->client->name }} — {{ $ins->classe->name }} ({{ $ins->date->format('Y-m-d') }})
                            </option>
                        @endforeach
                    </select>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Monto (€) *</label>
                    <input type="number" name="amount" step="0.01" value="{{ old('amount') }}" required
                           class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300" />
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Fecha *</label>
                    <input type="date" name="date" value="{{ old('date') }}" required
                           class="w-full mt-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300" />
                </div>

                <div class="flex justify-between pt-4">
                    <a href="{{ route('payments.index') }}"
                       class="bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg">← Cancelar</a>
                    <button type="submit"
                            class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg">Registrar</button>
                </div>
            </form>
        </div>
    </div>
</div>
@endsection
