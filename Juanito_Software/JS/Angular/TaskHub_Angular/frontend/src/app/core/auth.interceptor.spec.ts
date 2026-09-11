import { describe, it, expect } from 'vitest';
import { TestBed } from '@angular/core/testing';
import {
  HTTP_INTERCEPTORS,
  HttpClient,
  provideHttpClient,
  withInterceptorsFromDi,
} from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { Subject } from 'rxjs';

import { AuthInterceptor } from './auth.interceptor';
import { AuthService } from './auth.service';
import { AuthResponse } from './models';

/**
 * El interceptor: pone el token en cada peticion y gestiona el 401.
 *
 * AuthService se sustituye por un doble. Lo que se prueba aqui es la
 * coreografia del interceptor -cuando reintenta, cuando renueva, cuando se
 * rinde-, no como el servicio guarda el token. Si se usara el real, un fallo no
 * diria cual de los dos se ha roto.
 *
 * El doble cuenta las renovaciones y las deja en suspenso hasta que el test
 * decide resolverlas. Eso es lo que permite comprobar el caso interesante: dos
 * peticiones que reciben 401 a la vez.
 */
function montar(tokenInicial: string | null = 'token-viejo') {
  const renovaciones: Subject<AuthResponse>[] = [];
  let sesionesLimpiadas = 0;

  const doble: Partial<AuthService> = {
    getAccessToken: () => tokenInicial,
    clearSession: () => {
      sesionesLimpiadas++;
    },
    refresh: () => {
      const pendiente = new Subject<AuthResponse>();
      renovaciones.push(pendiente);
      return pendiente.asObservable();
    },
  };

  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    providers: [
      provideRouter([]),
      provideHttpClient(withInterceptorsFromDi()),
      provideHttpClientTesting(),
      { provide: AuthService, useValue: doble },
      { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    ],
  });

  return {
    http: TestBed.inject(HttpClient),
    control: TestBed.inject(HttpTestingController),
    renovaciones,
    sesionesLimpiadas: () => sesionesLimpiadas,
  };
}

const NO_AUTORIZADO = { status: 401, statusText: 'Unauthorized' };

describe('AuthInterceptor', () => {
  it('añade el token a la cabecera cuando hay sesion', () => {
    const { http, control } = montar('token-viejo');

    http.get('http://localhost:3000/api/projects').subscribe();

    const peticion = control.expectOne('http://localhost:3000/api/projects');
    expect(peticion.request.headers.get('Authorization')).toBe('Bearer token-viejo');

    peticion.flush([]);
    control.verify();
  });

  it('no añade cabecera cuando no hay token', () => {
    const { http, control } = montar(null);

    http.get('http://localhost:3000/api/projects').subscribe();

    const peticion = control.expectOne('http://localhost:3000/api/projects');
    expect(peticion.request.headers.has('Authorization')).toBe(false);

    peticion.flush([]);
    control.verify();
  });

  /**
   * Un 401 del propio login NO debe disparar una renovacion.
   *
   * Es el bucle clasico: credenciales malas -> 401 -> intento renovar -> el
   * refresh tambien falla -> 401 -> vuelta a empezar. Por eso el interceptor
   * lleva la lista de endpoints de autenticacion.
   */
  it('no intenta renovar cuando el 401 viene del propio login', () => {
    const { http, control, renovaciones } = montar(null);

    http.post('http://localhost:3000/api/auth/login', {}).subscribe({ error: () => undefined });
    control.expectOne('http://localhost:3000/api/auth/login').flush('malas', NO_AUTORIZADO);

    expect(renovaciones.length).toBe(0);
    control.verify();
  });

  it('ante un 401 renueva y reintenta la peticion con el token nuevo', () => {
    const { http, control, renovaciones } = montar('token-viejo');

    let respuesta: unknown;
    http.get('http://localhost:3000/api/projects').subscribe((r) => (respuesta = r));

    control.expectOne('http://localhost:3000/api/projects').flush('caducado', NO_AUTORIZADO);

    expect(renovaciones.length).toBe(1);
    renovaciones[0].next({ accessToken: 'token-nuevo', user: {} } as AuthResponse);

    const reintento = control.expectOne('http://localhost:3000/api/projects');
    expect(reintento.request.headers.get('Authorization')).toBe('Bearer token-nuevo');

    reintento.flush([{ id: 'p1' }]);
    expect(respuesta).toEqual([{ id: 'p1' }]);

    control.verify();
  });

  /**
   * Dos peticiones que caducan a la vez deben provocar **una sola** renovacion.
   *
   * Sin el candado `isRefreshing`, cada 401 dispararia su propio refresh. Con
   * rotacion de tokens eso es peor que ineficiente: el segundo refresh llega
   * con un token que el primero acaba de invalidar, el servidor lo toma por
   * reutilizacion y revoca la sesion entera. El usuario se ve expulsado por
   * haber abierto dos pestañas.
   */
  it('dos 401 simultaneos solo renuevan una vez', () => {
    const { http, control, renovaciones } = montar('token-viejo');

    http.get('http://localhost:3000/api/projects').subscribe();
    http.get('http://localhost:3000/api/tasks').subscribe();

    control.expectOne('http://localhost:3000/api/projects').flush('caducado', NO_AUTORIZADO);
    control.expectOne('http://localhost:3000/api/tasks').flush('caducado', NO_AUTORIZADO);

    expect(renovaciones.length).toBe(1);

    renovaciones[0].next({ accessToken: 'token-nuevo', user: {} } as AuthResponse);

    // Las dos se reintentan con el mismo token nuevo.
    for (const url of ['http://localhost:3000/api/projects', 'http://localhost:3000/api/tasks']) {
      const reintento = control.expectOne(url);
      expect(reintento.request.headers.get('Authorization')).toBe('Bearer token-nuevo');
      reintento.flush([]);
    }

    control.verify();
  });

  it('si la renovacion falla, cierra la sesion', () => {
    const { http, control, renovaciones, sesionesLimpiadas } = montar('token-viejo');

    http.get('http://localhost:3000/api/projects').subscribe({ error: () => undefined });
    control.expectOne('http://localhost:3000/api/projects').flush('caducado', NO_AUTORIZADO);

    expect(renovaciones.length).toBe(1);
    renovaciones[0].error(new Error('refresh rechazado'));

    expect(sesionesLimpiadas()).toBe(1);
    control.verify();
  });
});
