import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideNoopAnimations } from '@angular/platform-browser/animations';
import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { of } from 'rxjs';

import { ProjectDetailComponent } from './project-detail.component';
import { Project, Task, TaskStatus } from '../../core/models';

const PROYECTOS = 'http://localhost:3000/api/projects';
const TAREAS = 'http://localhost:3000/api/tasks';

const tarea = (id: string, status: TaskStatus, extra: Partial<Task> = {}): Task => ({
  id,
  title: `Tarea ${id}`,
  description: null,
  status,
  priority: 'MEDIUM',
  deadline: null,
  projectId: 'p1',
  assigneeId: null,
  creatorId: 'u1',
  createdAt: '2026-09-01T00:00:00.000Z',
  updatedAt: '2026-09-01T00:00:00.000Z',
  ...extra,
});

const PROYECTO: Project = {
  id: 'p1',
  name: 'Informe',
  description: null,
  createdAt: '2026-09-01T00:00:00.000Z',
  updatedAt: '2026-09-01T00:00:00.000Z',
  ownerId: 'u1',
  members: [{ id: 'm1', userId: 'u2', role: 'EDITOR', user: { id: 'u2', name: 'Ana', email: 'ana@test.com' } }],
};

/**
 * Se llega al componente navegando de verdad a `/projects/p1` con
 * RouterTestingHarness, en vez de inyectar un ActivatedRoute de mentira.
 *
 * Es la regla de la entrada del 11 de septiembre llevada un paso mas alla: no
 * se sustituye ningun servicio del enrutador. La plantilla lleva un
 * `routerLink`, cuya directiva lee la ruta activa, y un doble de ActivatedRoute
 * con solo `snapshot.paramMap` es exactamente el tipo de doble incompleto que
 * rompe a un tercero. Asi, ademas, el id sale de la URL por el mismo camino
 * que en produccion.
 *
 * La red se comprueba con HttpTestingController, y `verify()` en el afterEach
 * hace fallar cualquier peticion que no se haya esperado.
 */
async function montar(tareas: Task[] = []) {
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    providers: [
      provideNoopAnimations(),
      provideRouter([{ path: 'projects/:id', component: ProjectDetailComponent }]),
      provideHttpClient(),
      provideHttpClientTesting(),
    ],
  });

  const control = TestBed.inject(HttpTestingController);
  const harness = await RouterTestingHarness.create();
  const componente = await harness.navigateByUrl('/projects/p1', ProjectDetailComponent);

  control.expectOne(`${PROYECTOS}/p1`).flush(PROYECTO);
  control.expectOne((r) => r.url === TAREAS && r.params.get('projectId') === 'p1').flush(tareas);
  harness.detectChanges();

  const campos = componente as unknown as { dialog: MatDialog; snackBar: MatSnackBar };
  const abrirAviso = vi.spyOn(campos.snackBar, 'open').mockReturnValue({} as never);
  const alCerrarDialogo = (resultado: unknown) =>
    vi.spyOn(campos.dialog, 'open').mockReturnValue({ afterClosed: () => of(resultado) } as never);

  return { harness, componente, control, abrirAviso, alCerrarDialogo };
}

/** Ids de cada columna, en orden, para comparar el tablero de un vistazo. */
const tablero = (c: ProjectDetailComponent) =>
  Object.fromEntries(c.columns.map((col) => [col.status, col.tasks.map((t) => t.id)])) as Record<TaskStatus, string[]>;

/**
 * Lo que entrega CDK al soltar una tarjeta. Solo se usan estos cuatro campos.
 *
 * Un contenedor por array, y el MISMO objeto si origen y destino coinciden: el
 * componente distingue «misma columna» comparando contenedores por identidad
 * (`previousContainer === container`), no por su `data`. La primera version de
 * este ayudante creaba dos objetos distintos para la misma columna, y el test
 * de reordenar vio un PUT que en la aplicacion real no se hace.
 */
function soltar(desde: Task[], hasta: Task[], previousIndex: number, currentIndex: number) {
  const origen = { data: desde };
  const destino = desde === hasta ? origen : { data: hasta };
  return { previousContainer: origen, container: destino, previousIndex, currentIndex } as unknown as CdkDragDrop<Task[]>;
}

describe('ProjectDetailComponent', () => {
  let control: HttpTestingController | undefined;
  beforeEach(() => (control = undefined));
  afterEach(() => control?.verify());

  it('carga el proyecto de la URL y reparte sus tareas por estado', async () => {
    const m = await montar([tarea('t1', 'TODO'), tarea('t2', 'DONE'), tarea('t3', 'TODO'), tarea('t4', 'IN_REVIEW')]);
    control = m.control;

    expect(m.componente.projectId).toBe('p1');
    expect(tablero(m.componente)).toEqual({ TODO: ['t1', 't3'], IN_PROGRESS: [], IN_REVIEW: ['t4'], DONE: ['t2'] });
  });

  it('si el proyecto no carga, avisa', async () => {
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [
        provideNoopAnimations(),
        provideRouter([{ path: 'projects/:id', component: ProjectDetailComponent }]),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    control = TestBed.inject(HttpTestingController);
    // El espia tiene que estar puesto ANTES de navegar, porque la carga ocurre
    // en ngOnInit. No hay campo del componente al que llegar todavia, asi que
    // se espia el prototipo: cubre cualquier instancia, salga del inyector que
    // salga.
    const abrirAviso = vi.spyOn(MatSnackBar.prototype, 'open').mockReturnValue({} as never);

    try {
      const harness = await RouterTestingHarness.create();
      await harness.navigateByUrl('/projects/p1', ProjectDetailComponent);
      control.expectOne(`${PROYECTOS}/p1`).flush(null, { status: 404, statusText: 'Not Found' });
      control.expectOne((r) => r.url === TAREAS).flush([]);

      expect(abrirAviso).toHaveBeenCalledWith('No se pudo cargar el proyecto', 'Cerrar', expect.anything());
    } finally {
      // Un espia en el prototipo afecta a todas las instancias. Si se quedara
      // puesto al fallar este test, los siguientes heredarian un aviso mudo.
      abrirAviso.mockRestore();
    }
  });

  describe('arrastrar tarjetas', () => {
    it('a otra columna: guarda SOLO el estado nuevo', async () => {
      const m = await montar([tarea('t1', 'TODO', { title: 'Original', priority: 'HIGH' })]);
      control = m.control;
      const [todo, , , done] = m.componente.columns;

      m.componente.drop(soltar(todo.tasks, done.tasks, 0, 0), 'DONE');

      const cambio = m.control.expectOne(`${TAREAS}/t1`);
      expect(cambio.request.method).toBe('PUT');
      // Un PUT con la tarea entera pisaria lo que otro usuario haya cambiado
      // entretanto —titulo, responsable— con la copia vieja de esta pantalla.
      expect(cambio.request.body).toEqual({ status: 'DONE' });
      cambio.flush(tarea('t1', 'DONE'));

      expect(tablero(m.componente)).toMatchObject({ TODO: [], DONE: ['t1'] });
    });

    it('dentro de la misma columna: reordena y no llama al servidor', async () => {
      const m = await montar([tarea('t1', 'TODO'), tarea('t2', 'TODO'), tarea('t3', 'TODO')]);
      control = m.control;
      const todo = m.componente.columns[0];

      m.componente.drop(soltar(todo.tasks, todo.tasks, 0, 2), 'TODO');

      // El orden dentro de una columna no se persiste: el modelo no tiene campo
      // de posicion. Se fija aqui para que nadie crea que se guarda.
      expect(tablero(m.componente).TODO).toEqual(['t2', 't3', 't1']);
      m.control.expectNone(`${TAREAS}/t1`);
    });

    it('si el servidor rechaza el cambio, avisa y el tablero vuelve a lo que dice el servidor', async () => {
      const m = await montar([tarea('t1', 'TODO')]);
      control = m.control;
      const [todo, , , done] = m.componente.columns;

      m.componente.drop(soltar(todo.tasks, done.tasks, 0, 0), 'DONE');
      // El movimiento es optimista: la tarjeta ya esta en «Hecho» antes de
      // que conteste el servidor.
      expect(tablero(m.componente).DONE).toEqual(['t1']);

      m.control.expectOne(`${TAREAS}/t1`).flush(null, { status: 403, statusText: 'Forbidden' });

      expect(m.abrirAviso).toHaveBeenCalledWith('No se pudo mover la tarea', 'Cerrar', expect.anything());
      // Sin esta recarga, la tarjeta se quedaria en «Hecho» en pantalla y en
      // «Por hacer» en la base de datos, y el usuario no tendria forma de saberlo.
      m.control.expectOne((r) => r.url === TAREAS && r.params.get('projectId') === 'p1').flush([tarea('t1', 'TODO')]);
      expect(tablero(m.componente)).toMatchObject({ TODO: ['t1'], DONE: [] });
    });
  });

  describe('crear tarea', () => {
    it('añade al cuerpo el proyecto de la URL, avisa y recarga', async () => {
      const m = await montar();
      control = m.control;
      m.alCerrarDialogo({ title: 'Nueva', priority: 'HIGH' });

      m.componente.openCreateTaskDialog();

      // El dialogo no sabe en que proyecto esta; si el componente olvidara
      // añadirlo, el backend rechazaria la tarea (projectId es obligatorio).
      const alta = m.control.expectOne((r) => r.url === TAREAS && r.method === 'POST');
      expect(alta.request.body).toEqual({ title: 'Nueva', priority: 'HIGH', projectId: 'p1' });
      alta.flush(tarea('t9', 'TODO'));

      expect(m.abrirAviso).toHaveBeenCalledWith('Tarea creada', 'Cerrar', expect.anything());
      m.control.expectOne((r) => r.url === TAREAS && r.method === 'GET').flush([tarea('t9', 'TODO')]);
      expect(tablero(m.componente).TODO).toEqual(['t9']);
    });

    it('cancelar el dialogo no envia nada', async () => {
      const m = await montar();
      control = m.control;
      m.alCerrarDialogo(undefined);

      m.componente.openCreateTaskDialog();

      m.control.expectNone((r) => r.method === 'POST');
    });
  });

  describe('eliminar tarea', () => {
    it('confirmado: la borra en el servidor y la quita de su columna', async () => {
      const m = await montar([tarea('t1', 'TODO'), tarea('t2', 'TODO')]);
      control = m.control;
      m.alCerrarDialogo(true);

      m.componente.deleteTask(m.componente.columns[0].tasks[0], m.componente.columns[0]);

      const baja = m.control.expectOne(`${TAREAS}/t1`);
      expect(baja.request.method).toBe('DELETE');
      baja.flush(null);

      expect(tablero(m.componente).TODO).toEqual(['t2']);
      expect(m.abrirAviso).toHaveBeenCalledWith('Tarea eliminada', 'Cerrar', expect.anything());
    });

    it('si el servidor falla, la tarea sigue en el tablero', async () => {
      const m = await montar([tarea('t1', 'TODO')]);
      control = m.control;
      m.alCerrarDialogo(true);

      m.componente.deleteTask(m.componente.columns[0].tasks[0], m.componente.columns[0]);
      m.control.expectOne(`${TAREAS}/t1`).flush(null, { status: 403, statusText: 'Forbidden' });

      // Quitarla antes de que conteste el servidor haria desaparecer una tarea
      // que sigue existiendo.
      expect(tablero(m.componente).TODO).toEqual(['t1']);
      expect(m.abrirAviso).toHaveBeenCalledWith('No se pudo eliminar la tarea', 'Cerrar', expect.anything());
    });

    it('cancelado: no borra nada', async () => {
      const m = await montar([tarea('t1', 'TODO')]);
      control = m.control;
      m.alCerrarDialogo(false);

      m.componente.deleteTask(m.componente.columns[0].tasks[0], m.componente.columns[0]);

      m.control.expectNone(`${TAREAS}/t1`);
      expect(tablero(m.componente).TODO).toEqual(['t1']);
    });
  });

  /**
   * El boton «Miembros» y lo que pasa al cerrar su dialogo.
   *
   * Quien esta conectado lo decide AuthService, que lo lee de localStorage al
   * crearse; por eso la sesion se escribe ahi ANTES de montar. El PROYECTO de
   * este fichero pertenece a 'u1'.
   */
  describe('miembros', () => {
    const conSesionDe = (id: string) => localStorage.setItem('taskhub:user', JSON.stringify({ id, name: id, email: `${id}@test.com`, role: 'MEMBER', avatarUrl: null }));
    const botonMiembros = (m: Awaited<ReturnType<typeof montar>>) =>
      Array.from((m.harness.routeNativeElement as HTMLElement).querySelectorAll('button')).find((b) => b.textContent?.includes('Miembros'));

    afterEach(() => localStorage.removeItem('taskhub:user'));

    it('el propietario ve el boton «Miembros»', async () => {
      conSesionDe('u1');
      const m = await montar();
      control = m.control;

      expect(botonMiembros(m)).toBeDefined();
    });

    it('alguien que no es el propietario no lo ve', async () => {
      conSesionDe('u2');
      const m = await montar();
      control = m.control;

      expect(botonMiembros(m)).toBeUndefined();
    });

    it('al cerrar el dialogo se recarga el proyecto, para que el miembro nuevo salga en «Responsable»', async () => {
      conSesionDe('u1');
      const m = await montar();
      control = m.control;
      const abrir = m.alCerrarDialogo(undefined);

      m.componente.openMembersDialog();

      expect((abrir.mock.calls[0][1] as { data: { project: Project } }).data.project.id).toBe('p1');
      // Cerrar con Esc o pulsando fuera devuelve `undefined`; tambien recarga.
      const nuevoMiembro = { id: 'm2', userId: 'u3', role: 'EDITOR' as const, user: { id: 'u3', name: 'Luis', email: 'luis@test.com' } };
      m.control.expectOne(`${PROYECTOS}/p1`).flush({ ...PROYECTO, members: [...PROYECTO.members!, nuevoMiembro] });

      expect(m.componente.project?.members?.map((x) => x.userId)).toEqual(['u2', 'u3']);
    });
  });

  describe('editar tarea', () => {
    it('abre el detalle con los miembros del proyecto, para poder asignarla', async () => {
      const m = await montar([tarea('t1', 'TODO')]);
      control = m.control;
      const abrir = m.alCerrarDialogo(undefined);

      m.componente.openTaskDetail(m.componente.columns[0].tasks[0], m.componente.columns[0]);

      const { data } = abrir.mock.calls[0][1] as { data: { members: unknown[] } };
      expect(data.members).toEqual(PROYECTO.members);
    });

    it('si al guardar cambio de estado, la tarjeta pasa a la columna nueva', async () => {
      const m = await montar([tarea('t1', 'TODO'), tarea('t2', 'TODO')]);
      control = m.control;
      m.alCerrarDialogo(tarea('t1', 'IN_PROGRESS', { title: 'Editada' }));

      m.componente.openTaskDetail(m.componente.columns[0].tasks[0], m.componente.columns[0]);

      expect(tablero(m.componente)).toMatchObject({ TODO: ['t2'], IN_PROGRESS: ['t1'] });
      expect(m.componente.columns[1].tasks[0].title).toBe('Editada');
    });

    it('cerrar sin guardar no toca el tablero', async () => {
      const m = await montar([tarea('t1', 'TODO')]);
      control = m.control;
      m.alCerrarDialogo(undefined);

      m.componente.openTaskDetail(m.componente.columns[0].tasks[0], m.componente.columns[0]);

      expect(tablero(m.componente)).toMatchObject({ TODO: ['t1'] });
      expect(m.abrirAviso).not.toHaveBeenCalled();
    });
  });
});
