import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { TaskService } from './task.service';
import { Comment, Task } from './models';

const URL = 'http://localhost:3000/api/tasks';

/**
 * Igual que ProjectService: lo que se fija aqui es el contrato con el backend
 * —verbo, ruta y forma del cuerpo—, no logica de negocio.
 *
 * Merece la pena porque son los detalles que se rompen en silencio al
 * refactorizar: un PUT que pasa a PATCH, un id que deja de ir en la ruta y
 * empieza a ir en el cuerpo. El compilador no ve nada de eso.
 */
describe('TaskService', () => {
  let servicio: TaskService;
  let control: HttpTestingController;

  beforeEach(() => {
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [TaskService, provideHttpClient(), provideHttpClientTesting()],
    });
    servicio = TestBed.inject(TaskService);
    control = TestBed.inject(HttpTestingController);
  });

  afterEach(() => control.verify());

  it('lista las tareas de un proyecto filtrando por projectId', () => {
    servicio.listByProject('p1').subscribe();

    const peticion = control.expectOne((r) => r.url === URL);
    expect(peticion.request.method).toBe('GET');
    expect(peticion.request.params.get('projectId')).toBe('p1');
    // El backend recortaria a 20 en silencio; el tablero pide el maximo que
    // acepta (100) y lo enseña entero.
    expect(peticion.request.params.get('limit')).toBe('100');
    peticion.flush([]);
  });

  it('pide una tarea por su id', () => {
    servicio.getTask('t1').subscribe();

    const peticion = control.expectOne(`${URL}/t1`);
    expect(peticion.request.method).toBe('GET');
    peticion.flush({ id: 't1' } as unknown as Task);
  });

  it('crea con POST y el cuerpo intacto', () => {
    const nueva = { projectId: 'p1', title: 'Escribir tests', priority: 'HIGH' };

    servicio.createTask(nueva as never).subscribe();

    const peticion = control.expectOne(URL);
    expect(peticion.request.method).toBe('POST');
    expect(peticion.request.body).toEqual(nueva);
    peticion.flush({ id: 't1', ...nueva } as unknown as Task);
  });

  it('actualiza con PUT sobre el id, no con PATCH', () => {
    // PUT y PATCH no son intercambiables: con PUT el backend recibe el recurso
    // entero y los campos ausentes se interpretan como borrados.
    servicio.updateTask('t1', { status: 'DONE' } as never).subscribe();

    const peticion = control.expectOne(`${URL}/t1`);
    expect(peticion.request.method).toBe('PUT');
    expect(peticion.request.body).toEqual({ status: 'DONE' });
    peticion.flush({ id: 't1' } as unknown as Task);
  });

  it('borra con DELETE sobre el id', () => {
    servicio.deleteTask('t1').subscribe();

    const peticion = control.expectOne(`${URL}/t1`);
    expect(peticion.request.method).toBe('DELETE');
    peticion.flush(null);
  });

  it('añade un comentario en la subruta de la tarea', () => {
    servicio.addComment('t1', 'Falta el caso de error').subscribe();

    const peticion = control.expectOne(`${URL}/t1/comments`);
    expect(peticion.request.method).toBe('POST');
    // El texto viaja envuelto en un objeto, no como cadena suelta.
    expect(peticion.request.body).toEqual({ text: 'Falta el caso de error' });
    peticion.flush({ id: 'c1' } as unknown as Comment);
  });

  it('propaga el error al llamante en vez de tragarselo', () => {
    let recibido: unknown;
    servicio.getTask('inexistente').subscribe({ error: (e) => (recibido = e) });

    control
      .expectOne(`${URL}/inexistente`)
      .flush('no existe', { status: 404, statusText: 'Not Found' });

    expect(recibido).toBeTruthy();
  });
});
