import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideNoopAnimations } from '@angular/platform-browser/animations';
import { throwError, of } from 'rxjs';

import { LoginComponent } from './login.component';
import { AuthService } from '../../core/auth.service';
import { AuthResponse } from '../../core/models';

const SESION = { accessToken: 't', user: { id: 'u1' } } as unknown as AuthResponse;

/**
 * El componente se prueba llamando a `login()` directamente, sin renderizar.
 *
 * Lo que tiene este componente es una decision: a donde va el usuario segun lo
 * que responda el servidor. Eso no necesita DOM. Meter `detectChanges` y buscar
 * botones anadiria dependencias de Angular Material y de la plantilla sin
 * comprobar nada mas: si el boton cambia de sitio, el test deberia seguir
 * pasando, porque la decision no ha cambiado.
 */
function montar(respuestaDelServidor: 'ok' | 'error') {
  const login = vi.fn(() =>
    respuestaDelServidor === 'ok' ? of(SESION) : throwError(() => new Error('401')),
  );
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    imports: [LoginComponent],
    providers: [
      provideNoopAnimations(),
      // La plantilla lleva un `routerLink` («¿No tienes cuenta? Regístrate»), y
      // la directiva RouterLink inyecta ActivatedRoute. Eso obliga a montar el
      // enrutador de verdad.
      provideRouter([]),
      { provide: AuthService, useValue: { login } },
    ],
  });

  // El Router NO se sustituye por un doble, y el primer intento lo hizo.
  //
  // La fabrica de ActivatedRoute que aporta provideRouter lee
  // `routerState.root` del Router inyectado. Un doble con solo `navigate` deja
  // ese `routerState` en undefined y todo revienta con «Cannot read properties
  // of undefined (reading 'root')» antes de ejecutar el test.
  //
  // Se usa el Router real y se espia el metodo. Ademas de funcionar, es mas
  // fiel: si algun dia la firma de `navigate` cambia, el espia lo nota; un
  // doble escrito a mano no.
  const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);

  const componente = TestBed.createComponent(LoginComponent).componentInstance;

  // El aviso se espia sobre la instancia que tiene el componente, no sobre la
  // que devuelve TestBed.inject(MatSnackBar). Costo tres intentos averiguarlo:
  //
  //   1. Sustituir MatSnackBar por un doble en `providers` -> el componente
  //      importa MatSnackBarModule, que aporta el suyo, y ese gana.
  //   2. Espiar TestBed.inject(MatSnackBar) -> resuelve desde el inyector raiz,
  //      y el componente lo resuelve desde el suyo: son objetos distintos. El
  //      espia se quedaba a cero mientras el componente avisaba de verdad.
  //   3. Esto: alcanzar el campo del componente. Es la misma instancia por
  //      definicion, asi que no hay inyector que adivinar.
  //
  // `snackBar` es privado en TypeScript, no en ejecucion. Meter mano en un
  // privado desde un test es fea, y aqui es la opcion honesta: la alternativa
  // era seguir suponiendo de que inyector sale cada cosa.
  const abrirAviso = vi
    .spyOn((componente as unknown as { snackBar: MatSnackBar }).snackBar, 'open')
    .mockReturnValue({} as never);

  return { componente, login, navigate, abrirAviso };
}

describe('LoginComponent', () => {
  beforeEach(() => TestBed.resetTestingModule());

  it('envia al servicio lo que hay en los campos', () => {
    const { componente, login } = montar('ok');

    componente.email = 'juan@test.com';
    componente.password = 'secreto123';
    componente.login();

    expect(login).toHaveBeenCalledWith({ email: 'juan@test.com', password: 'secreto123' });
  });

  it('lleva al inicio cuando las credenciales son buenas', () => {
    const { componente, navigate, abrirAviso } = montar('ok');

    componente.login();

    expect(navigate).toHaveBeenCalledWith(['/']);
    expect(abrirAviso).not.toHaveBeenCalled();
  });

  it('avisa y NO navega cuando las credenciales son malas', () => {
    const { componente, navigate, abrirAviso } = montar('error');

    componente.login();

    // Las dos mitades importan. Avisar sin quedarse quieto dejaria al usuario
    // dentro de la aplicacion sin sesion; quedarse quieto sin avisar lo dejaria
    // pulsando el boton sin saber por que no pasa nada.
    expect(abrirAviso).toHaveBeenCalled();
    expect(navigate).not.toHaveBeenCalled();
  });

  it('el aviso de error no revela si el email existe', () => {
    const { componente, abrirAviso } = montar('error');

    componente.email = 'juan@test.com';
    componente.login();

    const mensaje = abrirAviso.mock.calls[0][0] as string;

    // 'Credenciales invalidas' a secas es deliberado: distinguir entre "ese
    // usuario no existe" y "la contrasena es incorrecta" convierte el login en
    // un comprobador de cuentas registradas.
    expect(mensaje).toBe('Credenciales inválidas');
    expect(mensaje).not.toContain('juan@test.com');
  });
});
