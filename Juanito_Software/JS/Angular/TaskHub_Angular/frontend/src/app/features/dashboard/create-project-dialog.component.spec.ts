import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { MatDialogRef } from '@angular/material/dialog';
import { provideNoopAnimations } from '@angular/platform-browser/animations';

import { CreateProjectDialogComponent } from './create-project-dialog.component';

/**
 * Lo que sale de este dialogo es el cuerpo del POST, tal cual. El dashboard no
 * lo toca, asi que cualquier descuido aqui llega al servidor.
 *
 * `MatDialogRef` SI se puede sustituir por un doble, a diferencia de MatDialog o
 * MatSnackBar: MatDialogModule no lo provee —lo crea MatDialog al abrir cada
 * dialogo— y nada de Angular lo lee por dentro. Se comprueba igualmente en el
 * primer test, que falla si el doble no es el que recibe la llamada.
 */
function montar() {
  const close = vi.fn();
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    imports: [CreateProjectDialogComponent],
    providers: [provideNoopAnimations(), { provide: MatDialogRef, useValue: { close } }],
  });
  const fixture = TestBed.createComponent(CreateProjectDialogComponent);
  return { fixture, componente: fixture.componentInstance, close };
}

describe('CreateProjectDialogComponent', () => {
  let m: ReturnType<typeof montar>;
  beforeEach(() => (m = montar()));

  it('devuelve el nombre sin espacios alrededor', () => {
    m.componente.name = '  Informe Q3  ';
    m.componente.submit();

    expect(m.close).toHaveBeenCalledWith({ name: 'Informe Q3' });
  });

  it('una descripcion vacia o de solo espacios no viaja', () => {
    m.componente.name = 'Informe';
    m.componente.description = '   ';
    m.componente.submit();

    // Con la clave ausente, Prisma guarda `description` como NULL, que es como
    // el modelo dice «sin descripción» (`String?` en el esquema). Con '' el
    // validador del backend la aceptaria y la base acabaria con dos formas de
    // decir lo mismo. En pantalla no se nota —las dos son falsy—, y por eso
    // mismo nadie lo veria hasta filtrar por `description IS NULL`.
    const cuerpo = m.close.mock.calls[0][0];
    expect(cuerpo).not.toHaveProperty('description');
  });

  it('una descripcion con texto viaja recortada', () => {
    m.componente.name = 'Informe';
    m.componente.description = '  Cierre trimestral \n';
    m.componente.submit();

    expect(m.close).toHaveBeenCalledWith({ name: 'Informe', description: 'Cierre trimestral' });
  });

  it('con el nombre en blanco, pulsar «Crear» no cierra el dialogo', () => {
    // submit() no comprueba el nombre: la unica barrera es el [disabled] del
    // boton. Por eso este test pulsa el boton de verdad en vez de llamar al
    // metodo, que devolveria { name: '' } sin rechistar.
    m.componente.name = '   ';
    m.fixture.detectChanges();

    const pantalla = m.fixture.nativeElement as HTMLElement;
    const crear = Array.from(pantalla.querySelectorAll('button')).find((b) => b.textContent?.includes('Crear'))!;
    crear.click();

    expect(m.close).not.toHaveBeenCalled();
  });

  it('con un solo caracter «Crear» sigue desactivado: el backend exige 2', () => {
    // Si el boton solo mirara si hay texto, un nombre de 1 letra llegaria al
    // servidor y volveria rechazado (el validador exige min(2)).
    m.componente.name = 'I';
    m.fixture.detectChanges();

    const pantalla = m.fixture.nativeElement as HTMLElement;
    const crear = Array.from(pantalla.querySelectorAll('button')).find((b) => b.textContent?.includes('Crear'))!;
    expect(crear.disabled).toBe(true);
    crear.click();
    expect(m.close).not.toHaveBeenCalled();

    // Con dos caracteres el mismo boton ya deja pasar.
    m.componente.name = 'II';
    m.fixture.detectChanges();
    crear.click();
    expect(m.close).toHaveBeenCalledTimes(1);
  });

  it('con nombre, pulsar «Crear» si cierra el dialogo', () => {
    // Control del anterior: prueba que el clic en ese boton llega a submit(), y
    // que el «no cierra» de arriba se debe al [disabled] y no a un selector que
    // no encuentra nada.
    m.componente.name = 'Informe';
    m.fixture.detectChanges();

    const pantalla = m.fixture.nativeElement as HTMLElement;
    const crear = Array.from(pantalla.querySelectorAll('button')).find((b) => b.textContent?.includes('Crear'))!;
    crear.click();

    expect(m.close).toHaveBeenCalledWith({ name: 'Informe' });
  });
});
