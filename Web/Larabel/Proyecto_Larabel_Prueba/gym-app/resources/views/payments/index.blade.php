@extends('layouts.app')

@section('content')
<div class="py-12">
    <div class="max-w-5xl mx-auto sm:px-6 lg:px-8">
        <div class="bg-white dark:bg-gray-800 shadow sm:rounded-lg p-6">
            <div class="flex justify-between items-center mb-6">
                <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Pagos</h1>
                <a href="{{ route('admin.payments.create') }}"
                   class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg">➕ Nuevo Pago</a>
            </div>

            @if(session('success'))
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                    {{ session('success') }}
                </div>
            @endif

            @if($payments->isEmpty())
                <p class="text-gray-600 dark:text-gray-400">No hay pagos registrados.</p>
            @else
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead class="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Cliente</th>
                            <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Clase</th>
                            <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Monto (€)</th>
                            <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">Fecha</th>
                            <th class="px-4 py-2"></th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                        @foreach($payments as $p)
                            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
                                <td class="px-4 py-2">{{ $p->inscription->client->name ?? 'Cliente eliminado' }}</td>
                                <td class="px-4 py-2">{{ $p->inscription->classe->name ?? 'Clase eliminada' }}</td>
                                <td class="px-4 py-2">{{ number_format($p->amount, 2) }} €</td>
                                <td class="px-4 py-2">{{ $p->date->format('Y-m-d') }}</td>
                                <td class="px-4 py-2 text-right">
                                    <a href="{{ route('admin.payments.show', $p->id) }}" class="text-blue-600 hover:underline">Ver</a> |
                                    <a href="{{ route('admin.payments.edit', $p->id) }}" class="text-yellow-600 hover:underline">Editar</a> |
                                    <form action="{{ route('admin.payments.destroy', $p->id) }}" method="POST" class="inline">
                                        @csrf
                                        @method('DELETE')
                                        <button type="submit" class="text-red-600 hover:underline"
                                                onclick="return confirm('¿Eliminar pago?')">Eliminar</button>
                                    </form>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            @endif
        </div>

        <!-- BOTÓN VOLVER -->
        <div class="mt-6">
            <a href="{{ route('dashboard') }}" 
               class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
                ← Volver al Dashboard
            </a>
        </div>
    </div>
</div>
@endsection
