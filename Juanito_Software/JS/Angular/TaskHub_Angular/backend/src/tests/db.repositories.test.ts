import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';

import { prisma } from '../config/prisma';
import { taskRepository } from '../repositories/task.repository';
import { projectRepository } from '../repositories/project.repository';
import { userRepository } from '../repositories/user.repository';

/**
 * Los unicos tests del backend que hablan con PostgreSQL.
 *
 * Los otros 162 doblan `config/prisma`, asi que ninguno ejecuta una sola
 * consulta: comprueban que el codigo llama a Prisma con los argumentos
 * correctos, no que esos argumentos produzcan el resultado correcto. Son dos
 * preguntas distintas y la segunda solo la contesta una base de datos.
 *
 * Lo que este fichero cubre y ningun otro puede:
 *
 *   - Que la migracion `20260704180530_init` se aplique de verdad. Hasta ahora
 *     no se ejecutaba en ninguna parte del CI.
 *   - Que las restricciones existan en el esquema y no solo en el codigo: el
 *     email unico, el par (proyecto, usuario) unico, y los borrados en cascada.
 *     Comprobar eso con un doble es imposible por definicion, porque el doble
 *     no tiene restricciones.
 *   - Que el filtro `visibleTo` de `taskRepository.findMany` haga lo que dice.
 *     Es la consulta que se escribio para cerrar el IDOR de /api/tasks, y su
 *     correccion depende enteramente de como traduzca Prisma ese `OR` anidado a
 *     SQL. Un test con dobles solo puede afirmar que el objeto `where` tiene la
 *     forma esperada, que es justo lo que ya sabemos.
 *
 * Se saltan donde no hay base de datos, con la variable TASKHUB_DB_TESTS que
 * solo define el workflow. El paso que cuenta tests descuenta los saltados, asi
 * que si esa variable dejara de llegar al job el recuento bajaria y el CI
 * fallaria: no pueden dejar de ejecutarse en silencio.
 */
const hayBaseDeDatos = process.env['TASKHUB_DB_TESTS'] === 'true';

/**
 * Seguro contra vaciar la base de datos equivocada.
 *
 * `vaciar()` hace TRUNCATE de las seis tablas antes de CADA test. Si alguien
 * exporta TASKHUB_DB_TESTS teniendo el DATABASE_URL del .env cargado, la base
 * de desarrollo —`taskmanager`, segun .env.example— se queda vacia sin aviso y
 * sin forma de recuperarla. Es un accidente de un solo comando y de efecto
 * irreversible, asi que la suite prefiere negarse a arrancar.
 *
 * La lista es explicita y corta a proposito: `taskhub_ci` la crea el servicio
 * del workflow y `taskhub_test` es la que se crea a mano en local. Cualquier
 * otro nombre aborta antes de tocar una sola fila.
 */
const BASES_PERMITIDAS = ['taskhub_ci', 'taskhub_test'];

function nombreDeLaBase(url: string): string {
  return new URL(url).pathname.replace(/^\//, '');
}

/** Deja las seis tablas vacias entre tests, respetando las claves ajenas. */
async function vaciar() {
  await prisma.$executeRawUnsafe(
    'TRUNCATE TABLE comments, tasks, project_members, projects, refresh_tokens, users CASCADE',
  );
}

let contador = 0;
function crearUsuario(nombre: string) {
  contador += 1;
  return prisma.user.create({
    data: { name: nombre, email: `${nombre}-${contador}@test.local`, password: 'hash-irrelevante' },
  });
}

describe.skipIf(!hayBaseDeDatos)('el esquema real de PostgreSQL', () => {
  beforeAll(async () => {
    const base = nombreDeLaBase(process.env['DATABASE_URL'] ?? '');
    if (!BASES_PERMITIDAS.includes(base)) {
      throw new Error(
        `Estos tests vacian las tablas antes de cada test y se niegan a hacerlo sobre "${base}". ` +
          `Apunta DATABASE_URL a una de estas: ${BASES_PERMITIDAS.join(', ')}.`,
      );
    }
    await prisma.$connect();
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  beforeEach(vaciar);

  describe('lo que crea la migracion', () => {
    it('las seis tablas del modelo existen', async () => {
      // Por nombre y no «hay tablas»: una migracion futura que se deje una sin
      // crear se aplicaria sin error, y el fallo saldria en la primera peticion
      // que la usara.
      const filas = await prisma.$queryRawUnsafe<{ table_name: string }[]>(
        `select table_name from information_schema.tables where table_schema = 'public'`,
      );
      const nombres = filas.map((f) => f.table_name);

      for (const tabla of ['users', 'refresh_tokens', 'projects', 'project_members', 'tasks', 'comments']) {
        expect(nombres, `falta la tabla ${tabla}`).toContain(tabla);
      }
    });

    it('los valores por defecto los pone la base de datos, no el codigo', async () => {
      // `role`, `status` y `priority` tienen default en el esquema. Si una
      // migracion futura los perdiera, el codigo seguiria funcionando en los
      // tests con dobles y en produccion llegarian nulos.
      const autor = await crearUsuario('ana');
      const proyecto = await prisma.project.create({ data: { name: 'Proyecto', ownerId: autor.id } });
      const tarea = await prisma.task.create({
        data: { title: 'Tarea', projectId: proyecto.id, creatorId: autor.id },
      });

      expect(autor.role).toBe('MEMBER');
      expect(tarea.status).toBe('TODO');
      expect(tarea.priority).toBe('MEDIUM');
      expect(tarea.createdAt).toBeInstanceOf(Date);
    });
  });

  describe('las restricciones que solo existen en el esquema', () => {
    it('dos usuarios no pueden compartir email', async () => {
      await prisma.user.create({ data: { name: 'Ana', email: 'repe@test.local', password: 'x' } });

      // El codigo comprueba el duplicado antes de insertar, pero esa comprobacion
      // no cubre dos altas simultaneas. La unica defensa real es el indice unico,
      // y esto prueba que la migracion lo creo.
      await expect(
        prisma.user.create({ data: { name: 'Bea', email: 'repe@test.local', password: 'x' } }),
      ).rejects.toMatchObject({ code: 'P2002' });
    });

    it('un usuario no puede ser miembro dos veces del mismo proyecto', async () => {
      const duenyo = await crearUsuario('duenyo');
      const otro = await crearUsuario('otro');
      const proyecto = await prisma.project.create({ data: { name: 'Proyecto', ownerId: duenyo.id } });
      await projectRepository.addMember(proyecto.id, otro.id, 'EDITOR');

      await expect(projectRepository.addMember(proyecto.id, otro.id, 'VIEWER')).rejects.toMatchObject({
        code: 'P2002',
      });
    });

    it('borrar un proyecto arrastra sus tareas', async () => {
      // `onDelete: Cascade` esta declarado en schema.prisma, pero quien lo
      // ejecuta es PostgreSQL. Si la migracion hubiera creado la clave ajena sin
      // la cascada, borrar un proyecto fallaria en produccion por violacion de
      // integridad, y ningun test con dobles lo veria.
      const autor = await crearUsuario('ana');
      const proyecto = await prisma.project.create({ data: { name: 'Proyecto', ownerId: autor.id } });
      await prisma.task.create({ data: { title: 'Tarea', projectId: proyecto.id, creatorId: autor.id } });

      await prisma.project.delete({ where: { id: proyecto.id } });

      expect(await prisma.task.count()).toBe(0);
    });

    it('borrar un usuario arrastra sus refresh tokens', async () => {
      // Importa por seguridad y no solo por limpieza: un refresh token que
      // sobreviviera a su usuario seria una credencial huerfana con siete dias
      // de vida por delante.
      const usuario = await crearUsuario('ana');
      await prisma.refreshToken.create({
        data: { token: 'token-de-prueba', userId: usuario.id, expiresAt: new Date(Date.now() + 86_400_000) },
      });

      await prisma.user.delete({ where: { id: usuario.id } });

      expect(await prisma.refreshToken.count()).toBe(0);
    });
  });

  describe('el filtro visibleTo, contra SQL de verdad', () => {
    /** Dos proyectos de dos duenyos distintos, con una tarea cada uno. */
    async function dosProyectos() {
      const ana = await crearUsuario('ana');
      const bea = await crearUsuario('bea');
      const ajeno = await crearUsuario('ajeno');
      const deAna = await prisma.project.create({ data: { name: 'De Ana', ownerId: ana.id } });
      const deBea = await prisma.project.create({ data: { name: 'De Bea', ownerId: bea.id } });
      await prisma.task.create({ data: { title: 'Tarea de Ana', projectId: deAna.id, creatorId: ana.id } });
      await prisma.task.create({ data: { title: 'Tarea de Bea', projectId: deBea.id, creatorId: bea.id } });
      return { ana, bea, ajeno, deAna, deBea };
    }

    it('el duenyo ve las tareas de su proyecto', async () => {
      const { ana } = await dosProyectos();

      const tareas = await taskRepository.findMany({ visibleTo: ana.id });

      expect(tareas.map((t) => t.title)).toEqual(['Tarea de Ana']);
    });

    it('un miembro tambien las ve', async () => {
      const { ana, ajeno, deAna } = await dosProyectos();
      await projectRepository.addMember(deAna.id, ajeno.id, 'VIEWER');

      const tareas = await taskRepository.findMany({ visibleTo: ajeno.id });

      expect(tareas.map((t) => t.title)).toEqual(['Tarea de Ana']);
      expect(ana.id).not.toBe(ajeno.id);
    });

    it('quien no es duenyo ni miembro no ve ninguna', async () => {
      // Este es el IDOR, comprobado contra la consulta real. Antes del arreglo,
      // una peticion sin filtros devolvia las tareas de todos los proyectos de
      // la base de datos.
      const { ajeno } = await dosProyectos();

      expect(await taskRepository.findMany({ visibleTo: ajeno.id })).toEqual([]);
    });

    it('pedir explicitamente el proyecto de otro tampoco lo salta', async () => {
      // El intento directo: conozco el id del proyecto ajeno y lo pido. El
      // filtro de visibilidad se combina con el de proyecto en la MISMA consulta,
      // asi que no hay forma de puentearlo desde los parametros.
      const { ajeno, deBea } = await dosProyectos();

      expect(await taskRepository.findMany({ visibleTo: ajeno.id, projectId: deBea.id })).toEqual([]);
    });

    it('los filtros opcionales se aplican ademas de la visibilidad, no en su lugar', async () => {
      const { ana, deAna } = await dosProyectos();
      await prisma.task.create({
        data: { title: 'Ya terminada', projectId: deAna.id, creatorId: ana.id, status: 'DONE' },
      });

      const terminadas = await taskRepository.findMany({ visibleTo: ana.id, status: 'DONE' });

      expect(terminadas.map((t) => t.title)).toEqual(['Ya terminada']);
    });

    it('el recuento por estado solo mira las tareas propias', async () => {
      // groupBy es otra consulta que solo una base de datos puede validar: con un
      // doble, el agrupamiento lo decide el doble.
      const { ana, bea, deAna } = await dosProyectos();
      await prisma.task.create({
        data: { title: 'Otra de Ana', projectId: deAna.id, creatorId: ana.id, status: 'DONE' },
      });

      const recuento = await taskRepository.countByStatusForUser(ana.id);
      const porEstado = Object.fromEntries(recuento.map((r) => [r.status, r._count]));

      expect(porEstado['TODO']).toBe(1);
      expect(porEstado['DONE']).toBe(1);
      expect(await taskRepository.countByStatusForUser(bea.id)).toHaveLength(1);
    });
  });

  describe('lectura por los repositorios reales', () => {
    it('un usuario va y vuelve por su repositorio', async () => {
      const creado = await userRepository.create({
        name: 'Ana',
        email: 'ida-y-vuelta@test.local',
        password: 'hash',
      });

      const leido = await userRepository.findByEmail('ida-y-vuelta@test.local');

      expect(leido?.id).toBe(creado.id);
      expect(leido?.name).toBe('Ana');
    });
  });
});
