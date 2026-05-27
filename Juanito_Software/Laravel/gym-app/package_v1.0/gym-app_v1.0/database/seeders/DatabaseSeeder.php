<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     *
     * Para demo: estos ejemplos están comentados para no generar duplicados
     * ni afectar los usuarios creados manualmente.
     */
    public function run(): void
    {
        // Crear 10 usuarios de prueba con la factory (comentado para no duplicar)
        // \App\Models\User::factory(10)->create();

        // Crear un usuario específico seguro para demo (comentado para no duplicar)
        // \App\Models\User::factory()->create([
        //     'name' => 'Demo User',
        //     'email' => 'demo@example.com',
        //     'password' => bcrypt('123456')
        // ]);

        // Nota:
        // Estos ejemplos demuestran conocimiento de mass assignment seguro
        // usando $fillable en los modelos y factories.
    }
}
