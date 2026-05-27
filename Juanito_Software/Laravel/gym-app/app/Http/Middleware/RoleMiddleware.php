<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Symfony\Component\HttpFoundation\Response;

class RoleMiddleware
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @param  string|array  $roles
     */
    public function handle(Request $request, Closure $next, ...$roles)
    {
        if (!Auth::check()) {
            return redirect('/login');
        }

        $user = Auth::user();

        // Si es admin, permitir acceso a todo
        if ($user->role === 'admin') {
            return $next($request);
        }

        // Si no es admin, comprobar roles permitidos
        if (!in_array($user->role, $roles)) {
            abort(403, 'No tienes permiso para acceder a esta sección.');
        }


        return $next($request);
    }
}