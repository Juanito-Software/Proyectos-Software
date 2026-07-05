<?php

use App\Http\Controllers\ProfileController;
use App\Http\Controllers\UsuarioController;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\ClientsController;
use App\Http\Controllers\CoachesController;
use App\Http\Controllers\ClassesController;
use App\Http\Controllers\InscriptionsController;
use App\Http\Controllers\PaymentsController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Aquí registramos las rutas web de la aplicación del gimnasio, protegidas
| con middleware de autenticación y roles.
|
*/

// Ruta pública
Route::get('/', function () {
    return view('welcome');
});

// Dashboard accesible solo para usuarios autenticados y verificados
Route::get('/dashboard', function () {
    return view('dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

// Rutas de perfil disponibles para todos los usuarios autenticados
Route::middleware('auth')->group(function () {
    Route::get('profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
    Route::get('perfil', [UsuarioController::class, 'mostrarPerfil'])->name('perfil');
});

// Rutas protegidas por roles

// Admin
Route::middleware(['auth','role:admin'])
    ->prefix('admin')
    ->name('admin.')
    ->group(function () {

        Route::get('dashboard', [AdminController::class, 'index'])->name('dashboard');
        // Admin puede gestionar TODO

        Route::resource('classes', ClassesController::class);
        Route::resource('coaches', CoachesController::class);
        Route::resource('clients', ClientsController::class);
        Route::resource('inscriptions', InscriptionsController::class);
        Route::resource('payments', PaymentsController::class);
    });

// Coach
Route::middleware(['auth','role:coach'])
    ->prefix('coach')
    ->name('coach.')
    ->group(function () {
        // Ver solo sus clases
        Route::get('classes', [ClassesController::class, 'myClasses'])->name('classes.index');
        // Ver detalle de una clase
        Route::get('classes/{class}', [ClassesController::class, 'show'])->name('classes.show');
    });


// Cliente
Route::middleware(['auth', 'role:client'])
    ->prefix('clients')
    ->as('clients.') // <-- esto añade "clients." a todos los nombres del grupo
    ->group(function () {
        Route::get('me', [ClientsController::class, 'show'])->name('me');
        Route::put('me', [ClientsController::class, 'update']);
        Route::resource('inscriptions', InscriptionsController::class)
            ->only(['index', 'create', 'store', 'show','edit', 'update', 'destroy']);
    });


// Rutas de autenticación de Breeze
require __DIR__.'/auth.php';
