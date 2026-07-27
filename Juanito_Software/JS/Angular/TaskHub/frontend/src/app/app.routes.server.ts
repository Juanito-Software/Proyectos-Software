import { RenderMode, ServerRoute } from '@angular/ssr';

/**
 * Modo de renderizado por ruta.
 *
 * La regla que ordena este fichero: una ruta cuya salida depende de quien sea
 * el usuario no puede renderizarse en el servidor mientras la sesion viva solo
 * en localStorage, porque en el servidor no existe localStorage.
 *
 * Las rutas protegidas por authGuard llaman a AuthService.isAuthenticated(),
 * que lee localStorage. En el servidor eso devuelve siempre null, el guard
 * concluye que no hay sesion y responde con un redirect a /login. Resultado:
 * al pulsar F5 estando dentro, el servidor expulsaba al usuario antes de que
 * se ejecutase una sola linea de JavaScript en el navegador.
 *
 * Con RenderMode.Client esas rutas se entregan sin renderizar y el guard se
 * evalua unicamente en el navegador, que es donde esta la sesion.
 *
 * Si algun dia la sesion se deduce de la cookie httpOnly del refresh token (que
 * el servidor si puede leer), estas rutas podrian volver a renderizarse en
 * servidor.
 */
export const serverRoutes: ServerRoute[] = [
  // Rutas publicas: no dependen de la sesion, se prerenderizan sin problema.
  {
    path: 'login',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'register',
    renderMode: RenderMode.Prerender
  },
  // Rutas protegidas por authGuard: solo en el navegador.
  {
    path: 'projects/:id',
    renderMode: RenderMode.Client
  },
  {
    path: '**',
    renderMode: RenderMode.Client
  }
];
