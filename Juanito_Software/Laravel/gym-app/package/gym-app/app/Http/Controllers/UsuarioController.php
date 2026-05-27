<?php
/**
 * * No se usa
 * */
namespace App\Http\Controllers;

use Illuminate\Http\Request;

class UsuarioController extends Controller
{
    public function mostrarPerfil()
    {
        $usuario = auth()->user();
        return view('perfil', compact('usuario'));
    }
}
