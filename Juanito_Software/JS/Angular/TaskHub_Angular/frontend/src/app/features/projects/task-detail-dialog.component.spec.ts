import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideNoopAnimations } from '@angular/platform-browser/animations';

import { TaskDetailDialogComponent, TaskDetailDialogData } from './task-detail-dialog.component';
import { Comment, Task } from '../../core/models';

const TAREAS = 'http://localhost:3000/api/tasks';

const TAREA: Task = {
  id: 't1',
  title: 'Revisar informe',
  description: 'Antes del viernes',
  status: 'IN_PROGRESS',
  priority: 'HIGH',
  deadline: '2026-09-30T00:00:00.000Z',
  projectId: 'p1',
  assigneeId: 'u2',
  creatorId: 'u1',
  createdAt: '2026-09-01T00:00:00.000Z',
  updatedAt: '2026-09-01T00:00:00.000Z',
};

const comentario = (id: string, text: string): Comment => ({
  id,
  text,
  taskId: 't1',
  authorId: 'u1',
  author: { id: 'u1', name: 'Juan', email: 'juan@test.com' },
  createdAt: '2026-09-02T00:00:00.000Z',
});

/**
 * El dialogo de edicion es el unico sitio de la aplicacion que manda un PUT con
 * todos los campos, y el unico que convierte formatos por el camino: la fecha
 * llega del servidor como ISO completo, se edita como `yyyy-mm-dd` en un
 * `<input type="date">`, y tiene que volver como ISO porque el validador del
 * backend es `z.string().datetime()` y rechaza una fecha a secas.
 *
 * `MatDialogRef` y `MAT_DIALOG_DATA` se sustituyen: los crea MatDialog al abrir,
 * no ningun modulo. `MatSnackBar` se espia en el campo del componente, como en
 * el resto de la carpeta.
 */
function montar(tarea: Task = TAREA) {
  const close = vi.fn();
  const data: TaskDetailDialogData = { task: tarea, members: [] };
  TestBed.resetTestingModule();
  TestBed.configureTestingModule({
    imports: [TaskDetailDialogComponent],
    providers: [
      provideNoopAnimations(),
      provideHttpClient(),
      provideHttpClientTesting(),
      { provide: MatDialogRef, useValue: { close } },
      { provide: MAT_DIALOG_DATA, useValue: data },
    ],
  });
  const control = TestBed.inject(HttpTestingController);
  const componente = TestBed.createComponent(TaskDetailDialogComponent).componentInstance;
  const abrirAviso = vi
    .spyOn((componente as unknown as { snackBar: MatSnackBar }).snackBar, 'open')
    .mockReturnValue({} as never);
  return { componente, control, close, abrirAviso };
}

/**
 * Ejecuta `fn` con el reloj del proceso en otra zona horaria.
 *
 * Los runners de GitHub estan en UTC, y en UTC los errores de zona horaria no
 * existen. Comprobado provocandolo, sin esta funcion: cambiar la escritura a
 * `new Date(fecha + 'T00:00')` —medianoche LOCAL— salia verde con TZ=UTC y
 * rojo con TZ=Europe/Madrid ('2026-09-29T22:00:00.000Z'). Es decir, el test
 * habria pasado en CI y fallado solo en un portatil en Madrid.
 *
 * Con la zona forzada, las dos regresiones salen rojas tambien con TZ=UTC:
 * escribir en hora local da '2026-09-30T07:00:00.000Z', y leer en hora local
 * (`toLocaleDateString`) da '2026-09-29'.
 *
 * Se elige una zona al OESTE de Greenwich porque ahi el fallo de lectura
 * tambien se ve —medianoche UTC del dia 30 es todavia dia 29—; al este solo se
 * veria el de escritura. Node aplica el cambio de `TZ` en caliente.
 * `process` se alcanza por globalThis porque tsconfig.spec no carga los tipos
 * de Node.
 */
function enZonaHoraria(zona: string, fn: () => void) {
  const env = (globalThis as unknown as { process: { env: Record<string, string | undefined> } }).process.env;
  const anterior = env['TZ'];
  env['TZ'] = zona;
  try {
    fn();
  } finally {
    if (anterior === undefined) delete env['TZ'];
    else env['TZ'] = anterior;
  }
}

/** ngOnInit + la carga de comentarios que dispara, ya contestada. */
function abierto(tarea: Task = TAREA, comentarios: Comment[] = []) {
  const m = montar(tarea);
  m.componente.ngOnInit();
  m.control.expectOne(`${TAREAS}/${tarea.id}`).flush({ ...tarea, comments: comentarios });
  return m;
}

describe('TaskDetailDialogComponent', () => {
  let control: HttpTestingController | undefined;
  beforeEach(() => (control = undefined));
  afterEach(() => control?.verify());

  it('al abrir, rellena el formulario con la tarea y la fecha en formato de calendario', () => {
    enZonaHoraria('America/Los_Angeles', () => {
      const m = montar();
      control = m.control;

      m.componente.ngOnInit();
      m.control.expectOne(`${TAREAS}/t1`).flush({ ...TAREA, comments: [] });

      expect(m.componente).toMatchObject({
        title: 'Revisar informe',
        description: 'Antes del viernes',
        status: 'IN_PROGRESS',
        priority: 'HIGH',
        assigneeId: 'u2',
        // Dia 30, aunque en Los Angeles ese instante sea todavia dia 29.
        deadline: '2026-09-30',
      });
    });
  });

  it('pide la tarea completa para traer los comentarios, y deja de cargar aunque falle', () => {
    const m = montar();
    control = m.control;

    m.componente.ngOnInit();
    expect(m.componente.loadingComments).toBe(true);
    m.control.expectOne(`${TAREAS}/t1`).flush(null, { status: 500, statusText: 'Server Error' });

    // Sin el `loadingComments = false` del camino de error, el spinner giraria
    // para siempre y el usuario no sabria si esperar.
    expect(m.componente.loadingComments).toBe(false);
  });

  describe('guardar', () => {
    it('envia todos los campos, recortados, y la fecha de vuelta en ISO', () => {
      const m = abierto();
      control = m.control;
      m.componente.title = '  Revisar informe final ';
      m.componente.description = ' Antes del lunes ';
      m.componente.status = 'IN_REVIEW';

      enZonaHoraria('America/Los_Angeles', () => m.componente.save());

      const cambio = m.control.expectOne(`${TAREAS}/t1`);
      expect(cambio.request.method).toBe('PUT');
      expect(cambio.request.body).toEqual({
        title: 'Revisar informe final',
        description: 'Antes del lunes',
        status: 'IN_REVIEW',
        priority: 'HIGH',
        assigneeId: 'u2',
        // Ida y vuelta sin cambiar de dia: '2026-09-30T00:00:00.000Z' ->
        // '2026-09-30' en el calendario -> el mismo instante al guardar.
        deadline: '2026-09-30T00:00:00.000Z',
      });
      cambio.flush({ ...TAREA, status: 'IN_REVIEW' });
    });

    it('vaciar la fecha y quitar el responsable envia null, no los omite', () => {
      const m = abierto();
      control = m.control;
      m.componente.deadline = '';
      m.componente.assigneeId = null;

      m.componente.save();

      // Con la clave ausente el backend entenderia «no cambies esto» y la tarea
      // conservaria la fecha y el responsable que el usuario acaba de quitar.
      const cuerpo = m.control.expectOne(`${TAREAS}/t1`).request.body;
      expect(cuerpo).toHaveProperty('deadline', null);
      expect(cuerpo).toHaveProperty('assigneeId', null);
    });

    it('al guardar, cierra devolviendo la tarea del servidor con los comentarios ya cargados', () => {
      const m = abierto(TAREA, [comentario('c1', 'Hecho a medias')]);
      control = m.control;

      m.componente.save();
      m.control.expectOne(`${TAREAS}/t1`).flush({ ...TAREA, title: 'Del servidor' });

      // El PUT no devuelve comentarios. Si el dialogo cerrara con la respuesta
      // tal cual, la tarjeta del tablero se quedaria sin ellos.
      expect(m.close).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Del servidor', comments: [expect.objectContaining({ id: 'c1' })] }),
      );
    });

    it('un doble clic en «Guardar» manda una sola peticion', () => {
      const m = abierto();
      control = m.control;

      m.componente.save();
      m.componente.save();

      // expectOne falla si hay dos.
      m.control.expectOne(`${TAREAS}/t1`).flush(TAREA);
    });

    it('con el titulo en blanco no manda nada', () => {
      const m = abierto();
      control = m.control;
      m.componente.title = '   ';

      m.componente.save();

      m.control.expectNone(`${TAREAS}/t1`);
    });

    it('si el servidor falla, avisa, NO cierra, y deja volver a intentarlo', () => {
      const m = abierto();
      control = m.control;

      m.componente.save();
      m.control.expectOne(`${TAREAS}/t1`).flush(null, { status: 400, statusText: 'Bad Request' });

      expect(m.abrirAviso).toHaveBeenCalledWith('No se pudo guardar la tarea', 'Cerrar', expect.anything());
      // Cerrar aqui tiraria lo que el usuario acaba de escribir.
      expect(m.close).not.toHaveBeenCalled();

      // Si el candado de `saving` no se soltara en el error, este segundo intento
      // no saldria y el boton quedaria deshabilitado para siempre.
      m.componente.save();
      m.control.expectOne(`${TAREAS}/t1`).flush(TAREA);
      expect(m.close).toHaveBeenCalledTimes(1);
    });
  });

  describe('comentar', () => {
    it('envia el texto recortado, lo añade a la lista y vacia la caja', () => {
      const m = abierto(TAREA, [comentario('c1', 'Primero')]);
      control = m.control;
      m.componente.newComment = '  Segundo  ';

      m.componente.addComment();

      const alta = m.control.expectOne(`${TAREAS}/t1/comments`);
      expect(alta.request.method).toBe('POST');
      expect(alta.request.body).toEqual({ text: 'Segundo' });
      alta.flush(comentario('c2', 'Segundo'));

      expect(m.componente.comments.map((c) => c.id)).toEqual(['c1', 'c2']);
      expect(m.componente.newComment).toBe('');
    });

    it('un comentario de solo espacios no se envia', () => {
      const m = abierto();
      control = m.control;
      m.componente.newComment = '  \n ';

      m.componente.addComment();

      m.control.expectNone(`${TAREAS}/t1/comments`);
    });

    it('si falla, avisa y conserva lo escrito', () => {
      const m = abierto();
      control = m.control;
      m.componente.newComment = 'Un parrafo largo que costo escribir';

      m.componente.addComment();
      m.control.expectOne(`${TAREAS}/t1/comments`).flush(null, { status: 500, statusText: 'Server Error' });

      expect(m.abrirAviso).toHaveBeenCalledWith('No se pudo enviar el comentario', 'Cerrar', expect.anything());
      expect(m.componente.newComment).toBe('Un parrafo largo que costo escribir');
      expect(m.componente.comments).toEqual([]);
    });
  });
});
