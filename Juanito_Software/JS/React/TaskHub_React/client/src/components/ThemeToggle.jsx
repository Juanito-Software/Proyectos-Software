import { useEffect, useState } from 'react';

const CLAVE = 'taskhub-tema';

/**
 * Lee la preferencia guardada, si la hay.
 *
 * Devuelve `null` cuando el usuario nunca ha elegido, que **no** es lo mismo
 * que «claro»: sin elección explícita manda `prefers-color-scheme`, y eso lo
 * resuelve el CSS sin que este componente tenga que opinar.
 *
 * El acceso va en try/catch porque `localStorage` lanza cuando el navegador
 * bloquea el almacenamiento de terceros o se navega en modo privado con
 * ciertas configuraciones. Que no se pueda recordar el tema es un
 * inconveniente; que la aplicación no arranque por eso, no.
 */
function temaGuardado() {
  try {
    const valor = localStorage.getItem(CLAVE);
    return valor === 'claro' || valor === 'oscuro' ? valor : null;
  } catch {
    return null;
  }
}

/** Qué está pintando el navegador ahora mismo, haya o no preferencia guardada. */
function temaEfectivo(guardado) {
  if (guardado) return guardado;
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'oscuro' : 'claro';
}

/**
 * Conmutador claro / oscuro.
 *
 * El estado vive en el atributo `data-tema` del elemento raíz, no en una clase
 * de React: así el CSS es la única fuente de verdad sobre el aspecto y ningún
 * componente necesita saber qué tema hay puesto para pintarse.
 */
export default function ThemeToggle({ className = '' }) {
  const [tema, setTema] = useState(() => temaEfectivo(temaGuardado()));

  useEffect(() => {
    document.documentElement.setAttribute('data-tema', tema);
    try {
      localStorage.setItem(CLAVE, tema);
    } catch {
      // Sin persistencia, pero el tema de esta sesión sigue aplicándose.
    }
  }, [tema]);

  const esOscuro = tema === 'oscuro';

  return (
    <button
      type="button"
      className={`btn-tema ${className}`.trim()}
      onClick={() => setTema(esOscuro ? 'claro' : 'oscuro')}
      // El botón no tiene texto, solo un símbolo, así que necesita nombre
      // accesible propio. Y describe la ACCIÓN, no el estado: «activar modo
      // claro» se entiende sin ver el icono; «modo oscuro» sería ambiguo.
      aria-label={esOscuro ? 'Activar modo claro' : 'Activar modo oscuro'}
      title={esOscuro ? 'Activar modo claro' : 'Activar modo oscuro'}
    >
      <span aria-hidden="true">{esOscuro ? '☀' : '☾'}</span>
    </button>
  );
}
