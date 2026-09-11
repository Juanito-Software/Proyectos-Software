import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { ProjectService } from './project.service';
import { Project } from './models';

const URL = 'http://localhost:3000/api/projects';

/**
 * Un servicio que solo envuelve llamadas HTTP no tiene logica que probar... casi.
 *
 * Lo que si tiene, y es donde se equivoca la gente, son los detalles del
 * contrato: que verbo se usa, que parametros viajan y cuales se omiten. Estos
 * tests fijan eso. Un `search` que viaja siempre, aunque venga vacio, hace que
 * el backend filtre por cadena vacia y devuelva cero resultados.
 */
describe('ProjectService', () => {
  let servicio: ProjectService;
  let control: HttpTestingController;

  beforeEach(() => {
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [ProjectService, provideHttpClient(), provideHttpClientTesting()],
    });
    servicio = TestBed.inject(ProjectService);
    control = TestBed.inject(HttpTestingController);
  });

  afterEach(() => control.verify());

  it('lista con paginacion por defecto', () => {
    servicio.listProjects().subscribe();

    const peticion = control.expectOne((r) => r.url === URL);
    expect(peticion.request.method).toBe('GET');
    expect(peticion.request.params.get('page')).toBe('1');
    expect(peticion.request.params.get('limit')).toBe('10');
    peticion.flush([]);
  });

  it('respeta la pagina y el limite que se le pasan', () => {
    servicio.listProjects(3, 25).subscribe();

    const peticion = control.expectOne((r) => r.url === URL);
    expect(peticion.request.params.get('page')).toBe('3');
    expect(peticion.request.params.get('limit')).toBe('25');
    peticion.flush([]);
  });

  it('envia el parametro de busqueda cuando lo hay', () => {
    servicio.listProjects(1, 10, 'informe').subscribe();

    const peticion = control.expectOne((r) => r.url === URL);
    expect(peticion.request.params.get('search')).toBe('informe');
    peticion.flush([]);
  });

  it('NO envia el parametro de busqueda cuando viene vacio', () => {
    // El servicio usa `if (search)`, asi que la cadena vacia no viaja. Si
    // viajara, el backend filtraria por '' y la lista saldria vacia.
    servicio.listProjects(1, 10, '').subscribe();

    const peticion = control.expectOne((r) => r.url === URL);
    expect(peticion.request.params.has('search')).toBe(false);
    peticion.flush([]);
  });

  it('crea enviando el cuerpo tal cual', () => {
    const nuevo = { name: 'Proyecto nuevo', description: 'con descripcion' };

    servicio.createProject(nuevo as never).subscribe();

    const peticion = control.expectOne(URL);
    expect(peticion.request.method).toBe('POST');
    expect(peticion.request.body).toEqual(nuevo);
    peticion.flush({ id: 'p1', ...nuevo } as unknown as Project);
  });

  it('pide un proyecto por su id', () => {
    servicio.getProject('p1').subscribe();

    const peticion = control.expectOne(`${URL}/p1`);
    expect(peticion.request.method).toBe('GET');
    peticion.flush({ id: 'p1' } as unknown as Project);
  });

  it('borra con DELETE sobre el id', () => {
    servicio.deleteProject('p1').subscribe();

    const peticion = control.expectOne(`${URL}/p1`);
    expect(peticion.request.method).toBe('DELETE');
    peticion.flush(null);
  });
});
