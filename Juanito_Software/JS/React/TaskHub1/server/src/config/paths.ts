import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// server/src/config -> server/data
const DEFAULT_DATA_DIR = path.join(__dirname, '..', '..', 'data');

// Resueltas de forma perezosa (no al importar el módulo) para que verify.ts
// pueda apuntar los repositorios a una carpeta temporal fijando
// process.env.DATA_DIR antes de la primera lectura/escritura, sin ensuciar
// nunca data/users.json ni data/tasks.json con datos de la suite de pruebas.
export function getDataDir(): string {
  return process.env.DATA_DIR ?? DEFAULT_DATA_DIR;
}

export function getTasksFile(): string {
  return path.join(getDataDir(), 'tasks.json');
}

export function getUsersFile(): string {
  return path.join(getDataDir(), 'users.json');
}
