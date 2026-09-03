import crypto from 'node:crypto';

/**
 * Generación y hashing del token de refresco.
 *
 * Va en su propio módulo, separado del repositorio, porque no toca la base de
 * datos: así los tests unitarios pueden cubrirlo sin levantar PostgreSQL, que
 * es la regla de la suite unitaria del servidor.
 */

/** Longitud del token en bytes antes de codificar. */
const REFRESH_TOKEN_BYTES = 32;

/**
 * Genera un token de refresco.
 *
 * **No es un JWT, y eso es deliberado.** Un token opaco de 32 bytes aleatorios
 * no puede pasar por token de acceso bajo ningún concepto: el middleware lo
 * intentaría verificar como JWT y fallaría la firma. Con dos JWT distintos
 * habría que confiar en un claim `typ` para separarlos, y olvidar esa
 * comprobación en un solo sitio bastaría para que un refresco sirviera como
 * acceso. Aquí esa confusión es imposible por construcción.
 *
 * 32 bytes son 256 bits de entropía: adivinarlo no es una vía de ataque.
 * Se codifica en base64url porque no lleva `+`, `/` ni `=`, que obligarían a
 * escapar el valor al meterlo en una cookie.
 */
export function generarRefreshToken(): string {
  return crypto.randomBytes(REFRESH_TOKEN_BYTES).toString('base64url');
}

/**
 * Hash con el que se guarda y se busca el token.
 *
 * SHA-256 sin sal, a diferencia de las contraseñas, que van con bcrypt. El
 * motivo es que aquí hacen falta dos cosas incompatibles con bcrypt: que el
 * hash sea **determinista**, para poder buscar la fila por él en lugar de
 * recorrer la tabla comparando una a una, y que sea rápido, porque se calcula
 * en cada renovación. El endurecimiento de bcrypt existe para resistir
 * diccionarios contra contraseñas que la gente elige; 32 bytes aleatorios no
 * tienen diccionario que valga.
 */
export function hashRefreshToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex');
}
