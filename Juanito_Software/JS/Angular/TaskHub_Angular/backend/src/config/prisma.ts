import { PrismaClient } from '@prisma/client';
import { isProduction } from './env';

// Patrón singleton: evita crear múltiples conexiones en desarrollo (hot-reload).
declare global {
   
  var __prisma__: PrismaClient | undefined;
}

/**
 * `test` no es un entorno de ejecución, es el banco de pruebas, y para el
 * registro se comporta como producción. Ver el comentario del `log`.
 */
const enTests = process.env.NODE_ENV === 'test';

export const prisma =
  global.__prisma__ ??
  new PrismaClient({
    // En desarrollo se registra cada consulta, que es justo lo que uno quiere
    // mientras depura un endpoint. En los tests no: db.repositories.test.ts
    // ejecuta cerca de cien consultas entre TRUNCATEs, inserciones y lecturas,
    // y cada una sale por stdout con su SELECT entero. En local eso tapa el
    // resumen de vitest; en el CI deja el log del job con miles de líneas de
    // SQL y el recuento de tests —lo único que hay que mirar cuando algo
    // falla— enterrado al final. Los errores y avisos sí se mantienen.
    log: isProduction || enTests ? ['error', 'warn'] : ['query', 'error', 'warn'],
  });

if (!isProduction) {
  global.__prisma__ = prisma;
}
