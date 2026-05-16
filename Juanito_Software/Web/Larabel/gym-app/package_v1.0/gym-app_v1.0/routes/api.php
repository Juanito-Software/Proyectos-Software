<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ClientsController;
use App\Http\Controllers\CoachesController;
use App\Http\Controllers\ClassesController;
use App\Http\Controllers\InscriptionsController;
use App\Http\Controllers\PaymentsController;
use App\Http\Controllers\UserController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Aquí registramos las rutas de la API del gimnasio, protegidas con
| auth:sanctum y middleware de roles.
|
*/

// Endpoint para ver el perfil del usuario autenticado
Route::middleware(['auth:sanctum'])->get('/user', [UserController::class, 'profile']);

// Rutas para clientes
Route::middleware(['auth:sanctum', 'role:client'])->group(function () {
    Route::get('/clients/me', [ClientsController::class, 'show']);
    Route::put('/clients/me', [ClientsController::class, 'update']);
    // Inscripciones propias
    Route::get('/inscriptions', [InscriptionsController::class, 'index']);
    Route::post('/inscriptions', [InscriptionsController::class, 'store']);
});

// Rutas para coaches
Route::middleware(['auth:sanctum', 'role:coach'])->group(function () {
    // Ver sus clases
    Route::get('/classes', [ClassesController::class, 'index']);
    // Ver alumnos inscritos en una clase concreta
    Route::get('/classes/{id}/inscriptions', [ClassesController::class, 'inscriptions']);
});

// Rutas para admin
Route::middleware(['auth:sanctum', 'role:admin'])->group(function () {
    Route::resource('/coaches', CoachesController::class)->except(['create', 'edit']);
    Route::resource('/payments', PaymentsController::class)->except(['create', 'edit']);
    Route::delete('/users/{id}', [UserController::class, 'destroy']);
    #Route::resource('clients', ClientsController::class)->except(['create', 'edit']);
    #Route::resource('inscriptions', InscriptionsController::class)->except(['create', 'edit']);
    #Route::resource('classes', ClassesController::class)->except(['create', 'edit']);
});

// Puedes añadir más rutas públicas aquí si lo necesitas
