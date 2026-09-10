<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\Route;
use Tests\TestCase;

/**
 * Que cada grupo de rutas lleve puesto el filtro de rol que le toca.
 *
 * RoleMiddlewareTest comprueba que el middleware decide bien. Esto comprueba
 * otra cosa distinta: que esta **aplicado** donde debe. Son fallos separados y
 * el primero no detecta el segundo — un middleware impecable que nadie ha
 * puesto en la ruta deja la seccion abierta igual.
 *
 * Se inspecciona la tabla de rutas en vez de pedir las URL. Asi no hace falta
 * base de datos ni datos sembrados, no se ejecuta ningun controlador, y el test
 * tarda milisegundos. Lo que se afirma es exactamente lo que se quiere afirmar:
 * "esta ruta exige este rol".
 */
class RutasPorRolTest extends TestCase
{
    /**
     * Middleware declarado para la ruta con ese nombre.
     *
     * @return array<int, string>
     */
    private function filtrosDe(string $nombreDeRuta): array
    {
        $ruta = Route::getRoutes()->getByName($nombreDeRuta);

        $this->assertNotNull(
            $ruta,
            "No existe ninguna ruta llamada '{$nombreDeRuta}'. Si se ha renombrado, "
            . 'actualiza este test; si ha desaparecido, mira si fue a proposito.'
        );

        return $ruta->gatherMiddleware();
    }

    /** @return array<string, array<int, string>> */
    public static function rutasDeAdministracion(): array
    {
        return [
            'panel'         => ['admin.dashboard'],
            'clases'        => ['admin.classes.index'],
            'entrenadores'  => ['admin.coaches.index'],
            'clientes'      => ['admin.clients.index'],
            'inscripciones' => ['admin.inscriptions.index'],
            'pagos'         => ['admin.payments.index'],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('rutasDeAdministracion')]
    public function test_las_rutas_de_administracion_exigen_rol_admin(string $nombre): void
    {
        $filtros = $this->filtrosDe($nombre);

        $this->assertContains('auth', $filtros, "'{$nombre}' no exige estar autenticado");
        $this->assertContains('role:admin', $filtros, "'{$nombre}' no exige rol admin");
    }

    public function test_las_rutas_de_coach_exigen_rol_coach(): void
    {
        foreach (['coach.classes.index', 'coach.classes.show'] as $nombre) {
            $filtros = $this->filtrosDe($nombre);

            $this->assertContains('auth', $filtros, "'{$nombre}' no exige estar autenticado");
            $this->assertContains('role:coach', $filtros, "'{$nombre}' no exige rol coach");
        }
    }

    public function test_las_rutas_de_cliente_exigen_rol_client(): void
    {
        foreach (['clients.me', 'clients.inscriptions.index'] as $nombre) {
            $filtros = $this->filtrosDe($nombre);

            $this->assertContains('auth', $filtros, "'{$nombre}' no exige estar autenticado");
            $this->assertContains('role:client', $filtros, "'{$nombre}' no exige rol client");
        }
    }

    /**
     * El reverso: que no se cuele nada sin filtrar en las zonas por rol.
     *
     * Un `Route::resource` que se anada por descuido fuera del grupo, o un
     * `->withoutMiddleware()` puesto para depurar y olvidado, quedaria colgando
     * bajo el mismo prefijo y sin proteccion. Los tests de arriba no lo verian,
     * porque solo miran las rutas que ya conocen.
     */
    public function test_ninguna_ruta_bajo_un_prefijo_por_rol_se_queda_sin_filtro(): void
    {
        $prefijos = ['admin' => 'role:admin', 'coach' => 'role:coach', 'clients' => 'role:client'];

        foreach (Route::getRoutes() as $ruta) {
            $uri = $ruta->uri();
            $prefijo = explode('/', $uri)[0];

            if (! isset($prefijos[$prefijo])) {
                continue;
            }

            $filtros = $ruta->gatherMiddleware();

            $this->assertContains(
                'auth',
                $filtros,
                "La ruta '{$uri}' cuelga de /{$prefijo} y no exige estar autenticado"
            );

            $tieneAlgunRol = (bool) preg_grep('/^role:/', $filtros);

            $this->assertTrue(
                $tieneAlgunRol,
                "La ruta '{$uri}' cuelga de /{$prefijo} y no exige ningun rol"
            );
        }
    }
}
