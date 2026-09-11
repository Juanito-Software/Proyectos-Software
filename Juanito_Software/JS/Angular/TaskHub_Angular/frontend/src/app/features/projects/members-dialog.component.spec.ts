import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { provideNoopAnimations } from '@angular/platform-browser/animations';

import { MembersDialogComponent } from './members-dialog.component';
import { Project, ProjectMember } from '../../core/models';

const URL = 'http://localhost:3000/api/projects/p1/members';

const miembro = (userId: string, role: ProjectMember['role']): ProjectMember => ({
  id: `m-${userId}`,
  userId,
  role,
  user: { id: userId, name: userId.toUpperCase(), email: `${userId}@test.com` },
});

const PROYECTO: Project = {
  id: 'p1',
  name: 'Informe',
  description: null,
  createdAt: '2026-09-01T00:00:00.000Z',
  updatedAt: '2026-09-01T00:00:00.000Z',
  ownerId: 'ana',
  members: [miembro('ana', 'OWNER'), miembro('eva', 'EDITOR')],
};

/**
 * El dialogo de miembros hace la peticion el mismo, asi que se prueba contra el
 * ProjectService real con HttpTestingController: lo que se comprueba es la
 * peticion que sale y lo que ve el usuario despues. `verify()` en el afterEach
 * hace fallar cualquier peticion no esperada.
 */
function montar() {
  const close = vi.fn();
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    imports: [MembersDialogComponent],
    providers: [
      provideNoopAnimations(),
      provideHttpClient(),
      provideHttpClientTesting(),
      { provide: MatDialogRef, useValue: { close } },
      { provide: MAT_DIALOG_DATA, useValue: { project: PROYECTO } },
    ],
  });
  const fixture = TestBed.createComponent(MembersDialogComponent);
  const control = TestBed.inject(HttpTestingController);
  return { fixture, componente: fixture.componentInstance, control, close };
}

const textoDe = (m: ReturnType<typeof montar>) => {
  m.fixture.detectChanges();
  return (m.fixture.nativeElement as HTMLElement).textContent ?? '';
};

describe('MembersDialogComponent', () => {
  let m: ReturnType<typeof montar>;
  beforeEach(() => (m = montar()));
  afterEach(() => m.control.verify());

  it('enseña a los miembros actuales con su rol en castellano', () => {
    const texto = textoDe(m);

    expect(texto).toContain('ANA');
    expect(texto).toContain('eva@test.com');
    expect(texto).toContain('Propietario');
    expect(texto).toContain('Editor');
  });

  it('sin tocar el rol, añade como Lector (VIEWER) y con el email recortado', () => {
    m.componente.email = '  bob@test.com ';
    m.componente.add();

    const alta = m.control.expectOne(URL);
    expect(alta.request.method).toBe('POST');
    expect(alta.request.body).toEqual({ email: 'bob@test.com', role: 'VIEWER' });
    alta.flush(miembro('bob', 'VIEWER'));
  });

  it('envia el rol elegido', () => {
    m.componente.email = 'bob@test.com';
    m.componente.role = 'EDITOR';
    m.componente.add();

    expect(m.control.expectOne(URL).request.body).toEqual({ email: 'bob@test.com', role: 'EDITOR' });
  });

  it('al añadir, el nuevo miembro aparece en la lista, la caja se vacia y el dialogo sigue abierto', () => {
    m.componente.email = 'bob@test.com';
    m.componente.add();
    m.control.expectOne(URL).flush(miembro('bob', 'VIEWER'));

    const texto = textoDe(m);
    expect(texto).toContain('bob@test.com');
    expect(texto).toContain('Lector');
    expect(m.componente.email).toBe('');
    // Seguir abierto permite añadir a varias personas seguidas.
    expect(m.close).not.toHaveBeenCalled();
  });

  it.each([
    [409, 'Ese usuario ya es miembro del proyecto'],
    [404, 'No existe ningún usuario con ese email'],
  ])('un %i enseña el mensaje del servidor y conserva lo escrito', (status, mensaje) => {
    m.componente.email = 'eva@test.com';
    m.componente.add();
    m.control.expectOne(URL).flush({ message: mensaje }, { status, statusText: 'Error' });

    const texto = textoDe(m);
    expect(texto).toContain(mensaje);
    // Sin esto el propietario tendria que volver a escribir el email para
    // corregir una letra.
    expect(m.componente.email).toBe('eva@test.com');
    expect(m.componente.members).toHaveLength(2);
    expect(m.close).not.toHaveBeenCalled();
  });

  it('un 400 enseña el error del campo email que manda el backend', () => {
    m.componente.email = 'bob';
    m.componente.add();
    m.control
      .expectOne(URL)
      .flush({ message: 'Error de validación', errors: { email: ['Email inválido'] } }, { status: 400, statusText: 'Bad Request' });

    expect(textoDe(m)).toContain('Email inválido');
  });

  it('un 500 NO enseña lo que diga el servidor, sino un mensaje propio', () => {
    m.componente.email = 'bob@test.com';
    m.componente.add();
    m.control.expectOne(URL).flush({ message: 'connect ECONNREFUSED 10.0.3.7' }, { status: 500, statusText: 'Error' });

    const texto = textoDe(m);
    expect(texto).not.toContain('ECONNREFUSED');
    expect(texto).toContain('No se pudo añadir el miembro');
  });

  it('tras un error se puede volver a intentar', () => {
    m.componente.email = 'bob@test.com';
    m.componente.add();
    m.control.expectOne(URL).flush({}, { status: 500, statusText: 'Error' });

    // Si `saving` no se soltara en el error, este segundo intento no saldria.
    m.componente.add();
    m.control.expectOne(URL).flush(miembro('bob', 'VIEWER'));
    expect(m.componente.members).toHaveLength(3);
  });

  it('un doble clic en «Añadir» manda una sola peticion', () => {
    m.componente.email = 'bob@test.com';
    m.componente.add();
    m.componente.add();

    // expectOne falla si hay dos.
    m.control.expectOne(URL).flush(miembro('bob', 'VIEWER'));
  });

  it('con el email en blanco, pulsar «Añadir» no manda nada', () => {
    m.componente.email = '   ';
    m.fixture.detectChanges();

    const boton = Array.from((m.fixture.nativeElement as HTMLElement).querySelectorAll('button')).find((b) =>
      b.textContent?.includes('Añadir'),
    )!;
    boton.click();

    m.control.expectNone(URL);
  });
});
