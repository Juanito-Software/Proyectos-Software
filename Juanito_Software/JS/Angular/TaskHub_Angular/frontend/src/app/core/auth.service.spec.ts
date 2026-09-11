import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { PLATFORM_ID } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { AuthService } from './auth.service';
import { AuthResponse } from './models';

const RESPUESTA: AuthResponse = {
  accessToken: 'token-de-acceso',
  user: { id: 'u1', email: 'juan@test.com', name: 'Juan' },
} as AuthResponse;

/**
 * Monta AuthService declarando en qué plataforma cree estar Angular.
 *
 * El parámetro no es un detalle: con 'server' se simula el renderizado en el
 * servidor (SSR), donde `localStorage` no existe. Los tests de abajo dependen
 * de poder cambiarlo.
 */
function montar(plataforma: 'browser' | 'server') {
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    providers: [
      AuthService,
      provideHttpClient(),
      provideHttpClientTesting(),
      { provide: PLATFORM_ID, useValue: plataforma },
    ],
  });

  return {
    servicio: TestBed.inject(AuthService),
    http: TestBed.inject(HttpTestingController),
  };
}

describe('AuthService', () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => localStorage.clear());

  describe('en el navegador', () => {
    it('login guarda la sesion y publica el usuario', () => {
      const { servicio, http } = montar('browser');

      let publicado: unknown = 'sin-emitir';
      servicio.currentUser$.subscribe((u) => (publicado = u));

      servicio.login({ email: 'juan@test.com', password: 'secreto123' } as never).subscribe();
      http.expectOne('http://localhost:3000/api/auth/login').flush(RESPUESTA);

      expect(localStorage.getItem('taskhub:accessToken')).toBe('token-de-acceso');
      expect(servicio.isAuthenticated()).toBe(true);
      expect(publicado).toEqual(RESPUESTA.user);

      http.verify();
    });

    it('logout limpia la sesion aunque la peticion falle', () => {
      const { servicio, http } = montar('browser');

      localStorage.setItem('taskhub:accessToken', 'token-viejo');
      localStorage.setItem('taskhub:user', JSON.stringify(RESPUESTA.user));

      servicio.logout().subscribe();
      // Un 500 del servidor no debe dejar al usuario con una sesion a medias
      // en el navegador: el finalize() limpia igualmente.
      http
        .expectOne('http://localhost:3000/api/auth/logout')
        .flush('error', { status: 500, statusText: 'Server Error' });

      expect(localStorage.getItem('taskhub:accessToken')).toBeNull();
      expect(localStorage.getItem('taskhub:user')).toBeNull();
      expect(servicio.isAuthenticated()).toBe(false);

      http.verify();
    });

    it('recupera el usuario guardado al construirse', () => {
      localStorage.setItem('taskhub:user', JSON.stringify(RESPUESTA.user));

      const { servicio } = montar('browser');

      expect(servicio.isAuthenticated()).toBe(true);
    });
  });

  /**
   * Regresion del fallo de SSR.
   *
   * Durante el renderizado en servidor no hay `localStorage`. Tocarlo lanza
   * ReferenceError y tumba la respuesta entera, asi que cada acceso esta
   * protegido con `isPlatformBrowser`.
   *
   * Estos tests no comprueban que "no explote" —en jsdom `localStorage` existe
   * y no explotaria—, sino el **comportamiento** que impone la proteccion: en
   * servidor no se lee ni se escribe, aunque haya datos delante. Si alguien
   * quita los `isBrowser()` por parecer redundantes, esto se pone en rojo.
   */
  describe('durante el renderizado en servidor (SSR)', () => {
    it('no lee el token aunque este guardado', () => {
      localStorage.setItem('taskhub:accessToken', 'token-de-acceso');

      const { servicio } = montar('server');

      expect(servicio.getAccessToken()).toBeNull();
    });

    it('no restaura la sesion aunque haya un usuario guardado', () => {
      localStorage.setItem('taskhub:user', JSON.stringify(RESPUESTA.user));

      const { servicio } = montar('server');

      expect(servicio.isAuthenticated()).toBe(false);
    });

    it('login no escribe en almacenamiento, pero si publica el usuario', () => {
      const { servicio, http } = montar('server');

      servicio.login({ email: 'juan@test.com', password: 'secreto123' } as never).subscribe();
      http.expectOne('http://localhost:3000/api/auth/login').flush(RESPUESTA);

      expect(localStorage.getItem('taskhub:accessToken')).toBeNull();
      // El estado en memoria si se actualiza: es lo que necesita el render.
      expect(servicio.isAuthenticated()).toBe(true);

      http.verify();
    });
  });
});
