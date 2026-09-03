import { sessionsRepository } from '../modules/auth/sessions.repository.js';

/**
 * Limpieza periódica de las sesiones caducadas.
 *
 * La tabla `refresh_sessions` guarda una fila por token, no por sesión: cada
 * renovación marca la vieja como rotada y añade otra. Con tokens de acceso de
 * quince minutos, un usuario que tenga la aplicación abierta ocho horas genera
 * unas treinta filas al día, y ninguna se borra sola.
 *
 * `limpiarCaducadas()` existía desde el primer día, documentada y con su
 * consulta escrita… y **no la llamaba nadie**. Era código muerto y la tabla
 * crecía sin techo. Esto es lo que faltaba para que sirviera de algo.
 *
 * ── Por qué un temporizador y no un cron externo ────────────────────────────
 *
 * Un servicio de tareas programadas —o una extensión como pg_cron— sería lo
 * habitual con varias instancias. TaskHub corre en un único proceso en Render,
 * así que un temporizador dentro del propio proceso hace exactamente lo mismo
 * sin añadir infraestructura. Si algún día hubiera más de una instancia, cada
 * una ejecutaría la limpieza por su cuenta: el `DELETE` es idempotente, así que
 * el peor caso es trabajo repetido, no datos perdidos.
 */

/** Cada cuánto se repasa la tabla. */
const INTERVALO_MS = 24 * 60 * 60 * 1000;

/**
 * Espera antes de la primera pasada.
 *
 * No se limpia nada más arrancar: en un despliegue de Render el proceso tiene
 * que empezar a responder cuanto antes, y un `DELETE` sobre una tabla grande
 * compitiendo con las primeras peticiones es justo lo que no interesa. Un
 * minuto es de sobra para que el servicio esté servido.
 */
const RETRASO_INICIAL_MS = 60 * 1000;

// `ReturnType<typeof setTimeout>` en lugar de `NodeJS.Timeout`: el espacio de
// nombres global NodeJS no lo conoce ESLint sin configuración extra, y esta
// forma es equivalente y no depende de él.
let temporizador: ReturnType<typeof setTimeout> | null = null;

async function pasada(): Promise<void> {
  try {
    const borradas = await sessionsRepository.limpiarCaducadas();
    if (borradas > 0) {
      console.log(`[sesiones] ${borradas} sesión(es) caducada(s) eliminada(s)`);
    }
  } catch (err) {
    // Un fallo aquí no debe tumbar el proceso: la limpieza es mantenimiento,
    // no parte de atender una petición. Se registra y se reintenta al día
    // siguiente.
    console.error('[sesiones] La limpieza falló, se reintentará:', err);
  }
}

export function iniciarLimpiezaDeSesiones(): void {
  if (temporizador) return;

  temporizador = setTimeout(function repetir() {
    void pasada().finally(() => {
      temporizador = setTimeout(repetir, INTERVALO_MS);
      // unref para que este temporizador no mantenga vivo el proceso: si
      // Node no tiene nada más que hacer, debe poder salir sin esperar
      // veinticuatro horas a la siguiente pasada.
      temporizador.unref();
    });
  }, RETRASO_INICIAL_MS);

  temporizador.unref();
}

export function detenerLimpiezaDeSesiones(): void {
  if (temporizador) {
    clearTimeout(temporizador);
    temporizador = null;
  }
}
