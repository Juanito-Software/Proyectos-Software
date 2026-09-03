import { Request, Response } from 'express';
import { env, isProduction } from '../../config/env.js';

/**
 * La cookie donde vive el token de refresco.
 *
 * ── Por qué una cookie y no localStorage ────────────────────────────────────
 * El token de acceso puede vivir en memoria del cliente porque dura minutos.
 * El de refresco dura días y sirve para emitir tokens de acceso nuevos, así que
 * es la credencial que de verdad importa proteger. `HttpOnly` la deja fuera del
 * alcance de `document.cookie`: un XSS ya no puede llevársela.
 *
 * ── Por qué esto no abre un agujero CSRF ────────────────────────────────────
 * Meter una cookie en una aplicación que no las usaba obliga a mirar CSRF, que
 * es el riesgo clásico de autenticar por cookie: el navegador la manda sola, así
 * que una página cualquiera podría lanzar peticiones en nombre del usuario.
 *
 * Aquí no ocurre, por tres motivos que se refuerzan entre sí:
 *
 * 1. `SameSite=Strict`. El navegador no manda la cookie en ninguna petición que
 *    nazca de otro sitio, así que la página del atacante no consigue adjuntarla.
 *    Es la defensa principal y la que hace innecesario un token anti-CSRF.
 *
 * 2. La cookie solo sirve para renovar. Ningún endpoint de datos la mira: las
 *    rutas protegidas exigen la cabecera `Authorization`, que una petición
 *    cross-site no puede fijar. Aunque la cookie llegara, no autoriza a nada.
 *
 * 3. `Path` acotado a las rutas de autenticación, así que ni siquiera se envía
 *    en el resto de la API.
 *
 * ── Por qué no rompe el CORS existente ──────────────────────────────────────
 * El delegado de CORS mantiene `credentials: false`, que es lo correcto: en
 * producción la aplicación, el playground y la API salen del mismo origen, y en
 * desarrollo Vite hace de proxy. El navegador nunca ve una petición
 * cross-origin, así que no hace falta relajar CORS para que la cookie viaje.
 */
export const REFRESH_COOKIE = 'taskhub_refresh';

/**
 * Ruta a la que se limita la cookie.
 *
 * Con esto no se envía en `/api/tasks` ni en `/api/admin`: solo donde de verdad
 * hace falta. Reduce la superficie sin coste ninguno.
 */
const COOKIE_PATH = '/api/auth';

export function setRefreshCookie(res: Response, token: string): void {
  res.cookie(REFRESH_COOKIE, token, {
    httpOnly: true,
    // Sin HTTPS el navegador rechazaría `secure`, y en desarrollo se trabaja
    // sobre HTTP. En producción es obligatorio: sin él la cookie viajaría en
    // claro ante cualquier degradación a HTTP.
    secure: isProduction,
    sameSite: 'strict',
    path: COOKIE_PATH,
    maxAge: env.refreshTokenTtlMs,
  });
}

export function clearRefreshCookie(res: Response): void {
  // Los atributos tienen que coincidir con los del `set` o el navegador no
  // identifica la cookie y se queda con la vieja.
  res.clearCookie(REFRESH_COOKIE, {
    httpOnly: true,
    secure: isProduction,
    sameSite: 'strict',
    path: COOKIE_PATH,
  });
}

/**
 * Lee la cookie de la cabecera.
 *
 * A mano en lugar de añadir `cookie-parser`: es una sola cookie con un nombre
 * conocido y un valor base64url, así que la dependencia no compensa.
 *
 * El `split` por `=` está limitado al primer separador porque el valor podría
 * contener uno; y se compara el nombre ya recortado, porque la cabecera lleva
 * un espacio detrás de cada `;`.
 */
export function readRefreshCookie(req: Request): string | undefined {
  const cabecera = req.headers.cookie;
  if (!cabecera) return undefined;

  for (const parte of cabecera.split(';')) {
    const sep = parte.indexOf('=');
    if (sep === -1) continue;
    if (parte.slice(0, sep).trim() !== REFRESH_COOKIE) continue;

    const valor = parte.slice(sep + 1).trim();
    try {
      return decodeURIComponent(valor);
    } catch {
      // Un valor mal codificado no debe tumbar la petición: se trata como si
      // no hubiera cookie y el usuario vuelve a entrar.
      return undefined;
    }
  }

  return undefined;
}
