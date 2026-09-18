import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { MatDialogRef } from '@angular/material/dialog';
import { provideNoopAnimations } from '@angular/platform-browser/animations';

import { CreateTaskDialogComponent } from './create-task-dialog.component';

/**
 * Mismo contrato que el dialogo de proyecto —lo que devuelve es casi el cuerpo
 * del POST; ProjectDetail solo le añade `projectId`—, con una pieza mas: la
 * prioridad, que siempre viaja.
 */
function montar() {
  const close = vi.fn();
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    imports: [CreateTaskDialogComponent],
    providers: [provideNoopAnimations(), { provide: MatDialogRef, useValue: { close } }],
  });
  const fixture = TestBed.createComponent(CreateTaskDialogComponent);
  return { fixture, componente: fixture.componentInstance, close };
}

describe('CreateTaskDialogComponent', () => {
  let m: ReturnType<typeof montar>;
  beforeEach(() => (m = montar()));

  it('si no se toca la prioridad, la tarea sale como MEDIUM', () => {
    m.componente.title = 'Revisar informe';
    m.componente.submit();

    expect(m.close).toHaveBeenCalledWith({ title: 'Revisar informe', priority: 'MEDIUM' });
  });

  it('devuelve la prioridad elegida y el titulo recortado', () => {
    m.componente.title = '  Revisar informe ';
    m.componente.priority = 'URGENT';
    m.componente.submit();

    expect(m.close).toHaveBeenCalledWith({ title: 'Revisar informe', priority: 'URGENT' });
  });

  it('la descripcion solo viaja si tiene texto, y recortada', () => {
    m.componente.title = 'T1';
    m.componente.description = '  ';
    m.componente.submit();
    expect(m.close.mock.calls[0][0]).not.toHaveProperty('description');

    m.componente.description = ' con detalle ';
    m.componente.submit();
    expect(m.close.mock.calls[1][0]).toEqual({ title: 'T1', priority: 'MEDIUM', description: 'con detalle' });
  });

  it('con un solo caracter en el titulo, «Crear» no cierra el dialogo', () => {
    // La validacion del backend pide min(2); un boton que solo mirara si hay
    // texto dejaria pasar titulos que el servidor rechaza.
    m.componente.title = 'a';
    m.fixture.detectChanges();

    const crear = Array.from((m.fixture.nativeElement as HTMLElement).querySelectorAll('button')).find((b) =>
      b.textContent?.includes('Crear'),
    )!;
    crear.click();
    expect(m.close).not.toHaveBeenCalled();

    m.componente.title = 'ab';
    m.fixture.detectChanges();
    crear.click();
    expect(m.close).toHaveBeenCalledTimes(1);
  });

  it('con el titulo en blanco, pulsar «Crear» no cierra el dialogo', () => {
    m.componente.title = '   ';
    m.fixture.detectChanges();

    const crear = Array.from((m.fixture.nativeElement as HTMLElement).querySelectorAll('button')).find((b) =>
      b.textContent?.includes('Crear'),
    )!;
    crear.click();
    expect(m.close).not.toHaveBeenCalled();

    // Control en el mismo test: con titulo, el mismo boton si cierra.
    m.componente.title = 'T1';
    m.fixture.detectChanges();
    crear.click();
    expect(m.close).toHaveBeenCalledTimes(1);
  });
});
