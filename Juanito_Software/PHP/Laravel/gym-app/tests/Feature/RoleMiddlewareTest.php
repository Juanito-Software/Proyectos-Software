<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Route;
use Tests\TestCase;

/**
 * Contrato de RoleMiddleware.
 *
 * Hasta ahora el proyecto tenia 25 tests y los 25 los genero Laravel Breeze al
 * instalarlo: registro, login, verificacion de correo, perfil. Ninguno tocaba
 * nada propio de gym-app, y en particular ninguno tocaba la autorizacion por
 * rol, que es lo que separa a un admin de un cliente en toda la aplicacion.
 *
 * Las rutas se definen aqui dentro y no se usan las reales a proposito: asi lo
 * que se prueba es el middleware y solo el middleware. Si se atacaran las rutas
 * de verdad, cada test dependeria ademas de su controlador, de sus modelos y de
 * que haya datos sembrados, y un fallo no diria si se ha roto la autorizacion o
 * la consulta. El cableado de las rutas reales se comprueba aparte, en
 * RutasPorRolTest.
 */
class RoleMiddlewareTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        // Tres rutas de usar y tirar, una por forma de declarar el filtro.
        Route::middleware(['web', 'role:admin'])
            ->get('/_test/solo-admin', fn () => response('ok'));

        Route::middleware(['web', 'role:coach'])
            ->get('/_test/solo-coach', fn () => response('ok'));

        Route::middleware(['web', 'role:coach,client'])
            ->get('/_test/coach-o-client', fn () => response('ok'));
    }

    private function usuarioCon(string $rol): User
    {
        return User::factory()->create(['role' => $rol]);
    }

    // ── Sin autenticar ────────────────────────────────────────────────────────

    public function test_un_visitante_es_redirigido_al_login_y_no_recibe_un_403(): void
    {
        $respuesta = $this->get('/_test/solo-admin');

        // La distincion importa: un 403 le diria a quien no ha entrado que el
        // recurso existe y que le esta vetado. La redireccion no afirma nada.
        $respuesta->assertRedirect('/login');
    }

    // ── Rol correcto ──────────────────────────────────────────────────────────

    public function test_el_rol_exigido_pasa(): void
    {
        $this->actingAs($this->usuarioCon('coach'))
            ->get('/_test/solo-coach')
            ->assertOk();
    }

    public function test_cualquiera_de_los_roles_listados_pasa(): void
    {
        $this->actingAs($this->usuarioCon('coach'))
            ->get('/_test/coach-o-client')
            ->assertOk();

        $this->actingAs($this->usuarioCon('client'))
            ->get('/_test/coach-o-client')
            ->assertOk();
    }

    // ── Rol incorrecto ────────────────────────────────────────────────────────

    public function test_un_rol_que_no_esta_en_la_lista_recibe_403(): void
    {
        $this->actingAs($this->usuarioCon('client'))
            ->get('/_test/solo-coach')
            ->assertForbidden();
    }

    public function test_un_cliente_no_entra_en_la_zona_de_administracion(): void
    {
        $this->actingAs($this->usuarioCon('client'))
            ->get('/_test/solo-admin')
            ->assertForbidden();
    }

    public function test_un_coach_no_entra_en_la_zona_de_administracion(): void
    {
        $this->actingAs($this->usuarioCon('coach'))
            ->get('/_test/solo-admin')
            ->assertForbidden();
    }

    // ── El admin como comodin ─────────────────────────────────────────────────

    /**
     * Esta es la regla que mas conviene tener escrita, porque no se ve en las
     * rutas. En routes/web.php, /coach/classes dice role:coach y nada mas: nadie
     * que lea esa linea deduce que un admin tambien entra. Vive en un if dentro
     * del middleware.
     *
     * No se prueba porque este bien o mal, se prueba porque es deliberado. Si
     * alguien quita ese if para "simplificar", tres tests se ponen en rojo y
     * dicen exactamente que se ha cambiado.
     */
    public function test_el_admin_entra_en_rutas_que_no_lo_mencionan(): void
    {
        $admin = $this->usuarioCon('admin');

        $this->actingAs($admin)->get('/_test/solo-coach')->assertOk();
        $this->actingAs($admin)->get('/_test/coach-o-client')->assertOk();
        $this->actingAs($admin)->get('/_test/solo-admin')->assertOk();
    }
}
