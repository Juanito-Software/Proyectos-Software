import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideNoopAnimations } from '@angular/platform-browser/animations';
import { HttpErrorResponse } from '@angular/common/http';
import { throwError, of } from 'rxjs';

import { RegisterComponent } from './register.component';
import { AuthService } from '../../core/auth.service';
import { AuthResponse } from '../../core/models';

const SESION = { accessToken: 't', user: { id: 'u1' } } as unknown as AuthResponse;

/**
 * Aqui hay logica de verdad, y no esta en la plantilla: `extractErrorMessage`.
 *
 * El backend puede rechazar un registro de tres formas distintas —un objeto
 * `errors` con los fallos por campo, un `message` suelto, o algo que no encaja
 * en ninguno de los dos— y el componente tiene que sacar un texto util de las
 * tres. Es un metodo privado, asi que se prueba por su efecto: que texto acaba
 * en el aviso.
 */
function montar(errorDelServidor?: unknown) {
  const register = vi.fn(() =>
    errorDelServidor === undefined
      ? of(SESION)
      : throwError(() => new HttpErrorResponse({ status: 400, error: errorDelServidor })),
  );
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    imports: [RegisterComponent],
    providers: [
      provideNoopAnimations(),
      // Igual que en login: la plantilla tiene un `routerLink` y RouterLink
      // inyecta ActivatedRoute, asi que hace falta el enrutador real.
      provideRouter([]),
      { provide: AuthService, useValue: { register } },
    ],
  });

  // El Router real vale espiado desde la raiz: el componente resuelve el mismo
  // objeto, porque provideRouter lo aporta ahi.
  const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);

  const componente = TestBed.createComponent(RegisterComponent).componentInstance;

  // MatSnackBar NO. El componente importa MatSnackBarModule y lo resuelve desde
  // su propio inyector, asi que TestBed.inject(MatSnackBar) devuelve otra
  // instancia y el espia se queda a cero. Se espia el campo del componente, que
  // es la instancia que de verdad recibe la llamada. Ver el comentario largo en
  // login.component.spec.ts.
  const abrirAviso = vi
    .spyOn((componente as unknown as { snackBar: MatSnackBar }).snackBar, 'open')
    .mockReturnValue({} as never);

  return {
    componente,
    register,
    navigate,
    abrirAviso,
    mensaje: () => abrirAviso.mock.calls[0]?.[0] as string,
  };
}

describe('RegisterComponent', () => {
  beforeEach(() => TestBed.resetTestingModule());

  it('envia nombre, email y contraseña', () => {
    const { componente, register } = montar();

    componente.name = 'Juan';
    componente.email = 'juan@test.com';
    componente.password = 'secreto123';
    componente.register();

    expect(register).toHaveBeenCalledWith({
      name: 'Juan',
      email: 'juan@test.com',
      password: 'secreto123',
    });
  });

  it('lleva al inicio cuando la cuenta se crea', () => {
    const { componente, navigate } = montar();

    componente.register();

    expect(navigate).toHaveBeenCalledWith(['/']);
  });

  describe('mensaje de error', () => {
    it('usa el primer fallo del primer campo cuando el backend valida por campos', () => {
      const { componente, mensaje } = montar({
        errors: {
          password: ['La contraseña debe tener al menos 8 caracteres', 'Y una mayúscula'],
          email: ['Ese email ya está en uso'],
        },
      });

      componente.register();

      // El primero del primer campo, no una concatenacion de todos: un aviso
      // con seis reglas dentro no se lee.
      expect(mensaje()).toBe('La contraseña debe tener al menos 8 caracteres');
    });

    it('usa el mensaje suelto cuando no hay errores por campo', () => {
      const { componente, mensaje } = montar({ message: 'El registro está deshabilitado' });

      componente.register();

      expect(mensaje()).toBe('El registro está deshabilitado');
    });

    it('cae en el texto por defecto cuando el error no trae nada util', () => {
      const { componente, mensaje } = montar({ algo: 'inesperado' });

      componente.register();

      expect(mensaje()).toBe('No se pudo crear la cuenta');
    });

    it('cae en el texto por defecto cuando el cuerpo del error es nulo', () => {
      // Pasa de verdad: un 502 del proxy o una caida de red llegan sin cuerpo.
      const { componente, mensaje } = montar(null);

      componente.register();

      expect(mensaje()).toBe('No se pudo crear la cuenta');
    });

    it('no navega cuando el registro falla', () => {
      const { componente, navigate } = montar({ message: 'no' });

      componente.register();

      expect(navigate).not.toHaveBeenCalled();
    });
  });
});
