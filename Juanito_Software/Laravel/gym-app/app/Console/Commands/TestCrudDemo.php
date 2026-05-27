<?php
namespace App\Console\Commands;

use Illuminate\Console\Command;

use App\Models\User;
use App\Models\Client;
use App\Models\Coach;
use App\Models\Classe;
use App\Models\Inscription;
use App\Models\Payment;


class TestCrudDemo extends Command
{
    protected $signature = 'test:crud-demo';
    protected $description = 'Ejecuta CRUD de prueba';

    public function handle()
    {
            // 🔹 Borrar registros anteriores de forma segura

        // Primero obtenemos el cliente existente (si hay)
        $client = Client::where('email', 'client@example.com')->first();
        if ($client) {
            // Borrar pagos de las inscripciones de este cliente
            $inscriptions = Inscription::where('client_id', $client->id)->pluck('id');
            Payment::whereIn('inscription_id', $inscriptions)->delete();

            // Borrar inscripciones
            Inscription::where('client_id', $client->id)->delete();

            // Borrar cliente
            $client->delete();
        }

        // Borrar otros registros independientes
        Coach::where('email', 'coach@example.com')->delete();
        Classe::where('name', 'Demo Classe')->delete();
        User::where('email', 'demo@example.com')->delete();

        // 1️⃣ CRUD User
        $user = User::updateOrCreate(
            ['email' => 'demo@example.com'], // criterio
            [
                'name' => 'Demo User',
                'password' => bcrypt('123456'),
                'phone_number' => '000000000',
            ]
        );
        echo "User creado/actualizado: {$user->name}\n";

        $user->update(['name' => 'Demo User Updated']);
        echo "User actualizado: {$user->name}\n";

        $fetchedUser = User::find($user->id);
        echo "User leído: {$fetchedUser->name}\n";

        // 2️⃣ CRUD Coach
        $coach = Coach::updateOrCreate(
            ['email' => 'coach@example.com'],
            [
                'name' => 'Demo Coach',
                'user_id' => $user->id,
                'phone_number' => '000000000',
                'sport' => 'Boxeo', // valor temporal para demo
            ]
        );
        $coach->update(['name' => 'Demo Coach Updated']);

        // 3️⃣ CRUD Client
        $client = Client::updateOrCreate(
            ['email' => 'client@example.com'],
            [
                'name' => 'Demo Client',
                'user_id' => $user->id,
                'phone_number' => '000000000',
            ]
        );
        $client->update(['name' => 'Demo Client Updated']);

        // 4️⃣ CRUD Classe
        $classe = Classe::updateOrCreate(
            ['name' => 'Demo Classe'], // criterio
            [
                'description' => 'Clase de prueba',
                'coach_id' => $coach->id, // aquí dentro, junto con description
                'days' => 'Lunes,Miércoles,Viernes', // valor temporal para demo
                'init_hour' => '10:00',              // valor temporal
                'final_hour' => '11:00',               // valor temporal
            ]
        );
        $classe->update(['name' => 'Demo Classe Updated']);

        // 5️⃣ CRUD Inscription
        $inscription = Inscription::updateOrCreate(
            ['client_id' => $client->id, 'class_id' => $classe->id],
            [
                'status' => 'confirmed',
                'date' => now(), // o '2025-11-22' para demo
            ]
        );

        $inscription->update(['status' => 'confirmed']);

        // 6️⃣ CRUD Payment
        $payment = Payment::updateOrCreate(
            ['inscription_id' => $inscription->id, 'amount' => 50],
            [
                'amount' => 100,
                'date' => now(), // obligatorio
            ]
        );

        echo "CRUD completo de prueba ejecutado ✅\n";

    }
}

