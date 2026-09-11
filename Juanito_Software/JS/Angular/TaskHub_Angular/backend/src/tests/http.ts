import type { AddressInfo } from 'node:net';
import type { Server } from 'node:http';
import type { Application } from 'express';
import jwt from 'jsonwebtoken';
import { createApp } from '../app';

/**
 * Utilidades para los tests que atacan la API por HTTP.
 *
 * Los tests de `*.service.test.ts` llaman a los servicios directamente, y por
 * eso no ven nada de lo que ocurre antes de llegar a ellos: rutas, middlewares,
 * validacion, controladores y el manejador de errores. Ahi es donde vive la
 * autenticacion y donde estaba el fallo de autorizacion de las tareas.
 *
 * Estos tests levantan la aplicacion real (`createApp()`) en un puerto libre y
 * le hacen peticiones con el `fetch` de Node. Lo unico sustituido es la capa de
 * repositorios, con `vi.mock` en cada fichero de test, asi que todo lo que hay
 * entre el socket y la base de datos es el codigo de produccion.
 *
 * Sin supertest a proposito: `fetch` viene con Node 22 y no añade dependencias
 * ni cambios en el lock.
 */

/** El mismo secreto que `setup.ts` pone en JWT_SECRET. */
export const SECRETO_DE_TEST = 'test-access-secret';

/**
 * `app` se puede pasar para los tests que necesitan una aplicacion recien
 * importada (tras `vi.resetModules()`), como los del limite de peticiones, cuyo
 * contador vive en el modulo y se compartiria entre tests.
 */
export async function arrancar(app: Application = createApp()) {
  const server: Server = app.listen(0);
  await new Promise<void>((resolve) => server.once('listening', resolve));
  const { port } = server.address() as AddressInfo;
  return {
    url: `http://127.0.0.1:${port}`,
    cerrar: () => new Promise<void>((resolve) => server.close(() => resolve())),
  };
}

export function tokenDe(
  id: string,
  opciones: { role?: 'ADMIN' | 'MANAGER' | 'MEMBER'; secreto?: string; expiresIn?: jwt.SignOptions['expiresIn'] } = {},
) {
  return jwt.sign({ sub: id, email: `${id}@test.com`, role: opciones.role ?? 'MEMBER' }, opciones.secreto ?? SECRETO_DE_TEST, {
    expiresIn: opciones.expiresIn ?? '15m',
  });
}

export function peticion(
  base: string,
  metodo: string,
  ruta: string,
  { token, cuerpo, cabeceras = {} }: { token?: string; cuerpo?: unknown; cabeceras?: Record<string, string> } = {},
) {
  return fetch(`${base}${ruta}`, {
    method: metodo,
    headers: {
      ...(cuerpo !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...cabeceras,
    },
    body: cuerpo !== undefined ? JSON.stringify(cuerpo) : undefined,
  });
}

/** Usuario tal como lo devuelve Prisma, con la contraseña dentro. */
export function usuarioCrudo(id: string) {
  return {
    id,
    name: id,
    email: `${id}@test.com`,
    role: 'MEMBER' as const,
    avatarUrl: null,
    createdAt: new Date('2026-01-01'),
    password: 'NO-DEBE-SALIR',
  };
}
