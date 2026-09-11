import { describe, it, expect, beforeEach } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';
import { provideRouter } from '@angular/router';

import { authGuard } from './auth.guard';
import { AuthService } from './auth.service';

/**
 * El guardia decide si una ruta se puede abrir.
 *
 * Se sustituye AuthService por un doble en vez de montar el de verdad: aqui lo
 * que se prueba es la decision del guardia, no como el servicio averigua si hay
 * sesion. Si se usara el real, un fallo no diria cual de los dos se ha roto.
 */
function montar(autenticado: boolean) {
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    providers: [
      provideRouter([]),
      { provide: AuthService, useValue: { isAuthenticated: () => autenticado } },
    ],
  });

  // Los CanActivateFn usan inject(), asi que necesitan un contexto de inyeccion.
  return TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));
}

describe('authGuard', () => {
  beforeEach(() => TestBed.resetTestingModule());

  it('deja pasar a quien tiene sesion', () => {
    expect(montar(true)).toBe(true);
  });

  it('manda al login a quien no la tiene', () => {
    const resultado = montar(false);

    // No devuelve `false` a secas, y la diferencia importa: `false` cancelaria
    // la navegacion dejando al usuario donde estaba, sin explicacion. Un
    // UrlTree lo redirige.
    expect(resultado).toBeInstanceOf(UrlTree);

    const router = TestBed.inject(Router);
    expect(router.serializeUrl(resultado as UrlTree)).toBe('/login');
  });
});
