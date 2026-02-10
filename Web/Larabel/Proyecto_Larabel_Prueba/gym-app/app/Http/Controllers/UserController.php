<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;

class UserController extends Controller
{
    public function destroy($id)
    {
        $user = User::findOrFail($id);

        // ✅ Si existe relación client → borrar (las inscripciones y pagos se eliminan en cascada)
        if ($user->client) {
            // Eliminar pagos asociados a las inscripciones del cliente
            $inscriptionIds = $user->client->inscriptions()->pluck('id');
            \App\Models\Payment::whereIn('inscription_id', $inscriptionIds)->delete();
            // Eliminar inscripciones
            $user->client->inscriptions()->delete();
            // Eliminar cliente
            $user->client->delete();
        }

        // ✅ Si existe relación coach → borrar
        if ($user->coach) {
            // Las clases que dependen del coach se pueden mantener o eliminar según necesidad
            // $user->coach->classes()->delete();
            $user->coach->delete();
        }

        // ✅ Finalmente borrar el usuario
        $user->delete();

        return response()->json([
            'success' => true,
            'message' => 'Usuario y registros asociados eliminados correctamente'
        ]);
    }
}
