import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { Router, provideRouter } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideNoopAnimations } from '@angular/platform-browser/animations';
import { of } from 'rxjs';

import { DashboardComponent } from './dashboard.component';
import { Project } from '../../core/models';

const URL = 'http://localhost:3000/api/projects';

const proyecto = (id: string, name = `Proyecto ${id}`): Project => ({
  id,
  name,
  description: null,
  createdAt: '2026-09-01T00:00:00.000Z',
  updatedAt: '2026-09-01T00:00:00.000Z',
  ownerId: 'u1',
});

/**
 * El dashboard no tiene estado propio que merezca la pena mirar: lo que hace
 * es pedir cosas al servidor segun lo que decida el usuario en un dialogo.
 *
 * Por eso el servicio NO se sustituye por un doble. Se usa el ProjectService
 * real y se comprueba lo que sale por la red con HttpTestingController: que
 * peticion se hace, con que cuerpo, y —tan importante como eso— cuales NO se
 * hacen. `control.verify()` en el afterEach convierte cualquier peticion no
 * esperada en un fallo, asi que «cancelar no borra» se comprueba solo.
 *
 * El montaje sigue la regla de la entrada del 11 de septiembre: Router real con
 * espia, y los servicios de Angular Material espiados sobre el campo del
 * propio componente. MatDialog tiene el mismo problema que MatSnackBar —el
 * componente importa MatDialogModule, que aporta su propio proveedor—.
 */
function montar() {
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    imports: [DashboardComponent],
    providers: [provideNoopAnimations(), provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
  });

  const control = TestBed.inject(HttpTestingController);
  const navegar = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
  const fixture = TestBed.createComponent(DashboardComponent);
  const componente = fixture.componentInstance;
  const campos = componente as unknown as { dialog: MatDialog; snackBar: MatSnackBar };

  const abrirAviso = vi.spyOn(campos.snackBar, 'open').mockReturnValue({} as never);

  /** El proximo dialogo que se abra se cerrara devolviendo `resultado`. */
  const alCerrarDialogo = (resultado: unknown) =>
    vi.spyOn(campos.dialog, 'open').mockReturnValue({ afterClosed: () => of(resultado) } as never);

  return { fixture, componente, control, navegar, abrirAviso, alCerrarDialogo };
}

/** Evento de clic con los dos metodos espiados, para las llamadas directas. */
const clic = () => ({ stopPropagation: vi.fn(), preventDefault: vi.fn() }) as unknown as Event;

describe('DashboardComponent', () => {
  let m: ReturnType<typeof montar>;

  beforeEach(() => (m = montar()));
  afterEach(() => m.control.verify());

  it('al entrar pide la lista de proyectos y la muestra', () => {
    m.componente.ngOnInit();

    const peticion = m.control.expectOne((r) => r.url === URL && r.method === 'GET');
    expect(peticion.request.params.get('page')).toBe('1');
    // Pedir en grande: con el limite de 10 por defecto el panel ocultaria
    // proyectos sin avisar.
    expect(peticion.request.params.get('limit')).toBe('100');
    peticion.flush([proyecto('p1'), proyecto('p2')]);

    expect(m.componente.projects.map((p) => p.id)).toEqual(['p1', 'p2']);
  });

  it('si la lista no carga, lo dice en vez de fingir que no hay proyectos', () => {
    m.fixture.detectChanges();
    m.control.expectOne((r) => r.url === URL).flush(null, { status: 500, statusText: 'Server Error' });
    m.fixture.detectChanges();

    expect(m.componente.loadError).toBe(true);
    const pantalla = m.fixture.nativeElement as HTMLElement;
    expect(pantalla.textContent).toContain('No se pudieron cargar los proyectos');
    expect(pantalla.textContent).not.toContain('No tienes proyectos aún');
  });

  describe('crear proyecto', () => {
    it('envia lo que devuelve el dialogo, avisa y recarga la lista', () => {
      m.alCerrarDialogo({ name: 'Informe', description: 'Q3' });

      m.componente.openCreateDialog();

      const alta = m.control.expectOne((r) => r.url === URL && r.method === 'POST');
      expect(alta.request.body).toEqual({ name: 'Informe', description: 'Q3' });
      alta.flush(proyecto('p9', 'Informe'));

      expect(m.abrirAviso).toHaveBeenCalledWith('Proyecto creado', 'Cerrar', expect.anything());
      // Sin esta recarga el proyecto recien creado no aparece hasta refrescar.
      m.control.expectOne((r) => r.url === URL && r.method === 'GET').flush([proyecto('p9', 'Informe')]);
      expect(m.componente.projects.map((p) => p.id)).toEqual(['p9']);
    });

    it('cancelar el dialogo no envia nada', () => {
      m.alCerrarDialogo(undefined);

      m.componente.openCreateDialog();

      m.control.expectNone(URL);
      expect(m.abrirAviso).not.toHaveBeenCalled();
    });

    it('si el servidor lo rechaza, avisa del fallo y no recarga', () => {
      m.alCerrarDialogo({ name: 'X' });

      m.componente.openCreateDialog();
      m.control
        .expectOne((r) => r.method === 'POST')
        .flush({ message: 'nombre corto' }, { status: 400, statusText: 'Bad Request' });

      // El aviso es el motivo que manda el servidor, no un «no se pudo» generico.
      expect(m.abrirAviso).toHaveBeenCalledWith('nombre corto', 'Cerrar', expect.anything());
      m.control.expectNone((r) => r.method === 'GET');
    });
  });

  describe('eliminar proyecto', () => {
    it('pide confirmacion nombrando el proyecto antes de borrar nada', () => {
      const abrir = m.alCerrarDialogo(false);

      m.componente.deleteProject(clic(), proyecto('p1', 'Informe Q3'));

      const opciones = abrir.mock.calls[0][1] as { data: { message: string } };
      expect(opciones.data.message).toContain('Informe Q3');
    });

    it('confirmado: borra ese proyecto, avisa y recarga la lista', () => {
      m.alCerrarDialogo(true);

      m.componente.deleteProject(clic(), proyecto('p1'));

      const baja = m.control.expectOne(`${URL}/p1`);
      expect(baja.request.method).toBe('DELETE');
      baja.flush(null);

      expect(m.abrirAviso).toHaveBeenCalledWith('Proyecto eliminado', 'Cerrar', expect.anything());
      m.control.expectOne((r) => r.url === URL && r.method === 'GET').flush([]);
    });

    it('cancelado: no borra nada', () => {
      m.alCerrarDialogo(false);

      m.componente.deleteProject(clic(), proyecto('p1'));

      m.control.expectNone(`${URL}/p1`);
    });

    it('si el servidor falla, avisa y no recarga', () => {
      m.alCerrarDialogo(true);

      m.componente.deleteProject(clic(), proyecto('p1'));
      m.control.expectOne(`${URL}/p1`).flush(null, { status: 403, statusText: 'Forbidden' });

      expect(m.abrirAviso).toHaveBeenCalledWith('No se pudo eliminar el proyecto', 'Cerrar', expect.anything());
      m.control.expectNone((r) => r.method === 'GET');
    });
  });

  /**
   * Los dos unicos tests que renderizan, y es a proposito.
   *
   * El boton «Eliminar» esta DENTRO del elemento de lista que lleva el
   * `routerLink` al proyecto. Sin el `stopPropagation` de `deleteProject`, el
   * clic sube hasta el enlace y el usuario sale disparado a la pantalla del
   * proyecto que acaba de pedir borrar, con el dialogo de confirmacion abierto
   * encima. Eso depende de como esta anidada la plantilla, asi que solo se
   * puede comprobar con la plantilla delante.
   *
   * El primer test es el control del segundo: demuestra que el espia de
   * navegacion SI ve un clic en la fila. Sin el, «no navega» podria estar
   * pasando porque el espia no detecta nada.
   */
  describe('en pantalla', () => {
    function pintarConUnProyecto() {
      m.fixture.detectChanges();
      m.control.expectOne((r) => r.url === URL).flush([proyecto('p1', 'Informe')]);
      m.fixture.detectChanges();
      return m.fixture.nativeElement as HTMLElement;
    }

    it('pulsar la fila lleva al proyecto', () => {
      const pantalla = pintarConUnProyecto();

      pantalla.querySelector<HTMLElement>('mat-list-item.clickable')!.click();

      expect(m.navegar).toHaveBeenCalledTimes(1);
      expect(String(m.navegar.mock.calls[0][0])).toBe('/projects/p1');
    });

    it('pulsar «Eliminar» abre la confirmacion y NO lleva al proyecto', () => {
      const pantalla = pintarConUnProyecto();
      const abrir = m.alCerrarDialogo(false);

      const botones = Array.from(pantalla.querySelectorAll<HTMLButtonElement>('mat-list-item.clickable button'));
      botones.find((b) => b.textContent?.includes('Eliminar'))!.click();

      expect(abrir).toHaveBeenCalledTimes(1);
      expect(m.navegar).not.toHaveBeenCalled();
    });
  });
});
