import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  login as loginApi,
  register as registerApi,
  logout as logoutApi,
  refreshSession,
  changePassword as changePasswordApi,
} from '../services/authApi';
import { setAuthToken, configurarAuth } from '../services/api';

/**
 * Estado de la sesión para toda la aplicación (contexto de React).
 *
 * Expone, a través de `useAuth()`:
 * `user`, `token`, `isAuthenticated`, `login`, `register`, `logout` y
 * `changePassword`.
 *
 * Mantiene sincronizados tres sitios: el estado de React, `localStorage` (para
 * sobrevivir a una recarga) y el token que usa `services/api.js`.
 */
const AuthContext = createContext(null);

/**
 * Qué se guarda y qué no.
 *
 * Aquí solo van el usuario y el **token de acceso**, que dura quince minutos.
 * El token de refresco no aparece: vive en una cookie HttpOnly que este código
 * no puede leer ni escribir, que es justo lo que se busca — un XSS puede
 * llevarse el token de acceso y disponer de un cuarto de hora, pero no la
 * credencial que renueva la sesión durante días.
 *
 * La clave se mantiene, porque el playground lee de ella para compartir sesión
 * con la aplicación.
 */
const STORAGE_KEY = 'taskhub_auth';

/**
 * @returns {{user: object, token: string} | null} la sesión guardada, o
 *          `null` si no hay o no se puede leer
 */
function loadStoredAuth() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) return JSON.parse(data);
  } catch (err) {
    // Un JSON corrupto o el almacenamiento bloqueado (modo privado, política
    // del navegador) no deben impedir que la aplicación cargue: simplemente
    // se empieza sin sesión y el usuario vuelve a entrar.
    console.warn('No se pudo leer la sesión guardada:', err);
  }
  return null;
}

/**
 * Proveedor de la sesión. Envuelve la aplicación entera (ver `App.jsx`).
 *
 * @param {{children: import('react').ReactNode}} props
 */
export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(loadStoredAuth);

  // Cada cambio de sesión se refleja en localStorage y en la capa de servicios.
  useEffect(() => {
    if (auth) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
      setAuthToken(auth.token);
    } else {
      localStorage.removeItem(STORAGE_KEY);
      setAuthToken(null);
    }
  }, [auth]);

  /**
   * Enlaza el contexto con la capa de servicios.
   *
   * `api.js` renueva por su cuenta cuando una petición choca con un 401; estos
   * dos avisos son los que permiten que el resultado llegue hasta React, para
   * que el token guardado no se quede desfasado y para que la interfaz vuelva
   * al formulario cuando la sesión muere de verdad.
   */
  useEffect(() => {
    configurarAuth({
      alRenovar: (datos) => {
        setAuth((actual) =>
          actual ? { user: datos.user ?? actual.user, token: datos.accessToken } : actual,
        );
      },
      alPerderSesion: () => setAuth(null),
    });
    return () => configurarAuth({});
  }, []);

  /**
   * Al arrancar con una sesión guardada, se renueva antes de nada.
   *
   * El token de acceso dura quince minutos, así que el guardado en
   * `localStorage` casi siempre estará caducado al volver. Sin esto, la primera
   * petición fallaría y el usuario vería un parpadeo hasta que la renovación
   * automática se pusiera al día. Si la cookie ya no vale, se cierra la sesión
   * sin ruido y aparece el formulario.
   */
  useEffect(() => {
    if (!auth?.token) return;

    let cancelado = false;
    refreshSession()
      .then((datos) => {
        if (!cancelado) setAuth({ user: datos.user, token: datos.accessToken });
      })
      .catch(() => {
        if (!cancelado) setAuth(null);
      });

    return () => {
      cancelado = true;
    };
    // Solo al montar: renovar en cada cambio de `auth` sería un bucle, porque
    // la propia renovación lo cambia.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Inicia sesión y guarda las credenciales.
   *
   * @throws {Error} con el mensaje del servidor si falla (lo muestra App.jsx)
   */
  async function login(username, password) {
    const { user, accessToken } = await loginApi(username, password);
    setAuthToken(accessToken);
    setAuth({ user, token: accessToken });
  }

  /**
   * Crea la cuenta y deja al usuario dentro.
   *
   * @throws {Error} con el mensaje del servidor si falla
   */
  async function register(username, password) {
    const { user, accessToken } = await registerApi(username, password);
    setAuthToken(accessToken);
    setAuth({ user, token: accessToken });
  }

  /**
   * Cierra sesión **en el servidor** antes de olvidarla aquí.
   *
   * Es la diferencia con la versión anterior, que solo vaciaba el estado local:
   * el token seguía siendo válido durante días para quien tuviera una copia.
   * Ahora se revoca la familia de refresco, y si la llamada falla se cierra
   * igualmente en local — dejar al usuario dentro porque la red falló sería
   * peor que quedarse con una sesión huérfana en la base de datos, que además
   * caduca sola.
   */
  const logout = useCallback(async () => {
    try {
      await logoutApi();
    } catch (err) {
      console.warn('No se pudo cerrar la sesión en el servidor:', err);
    } finally {
      setAuth(null);
    }
  }, []);

  /**
   * Cambia la contraseña y **se queda con las credenciales nuevas**.
   *
   * El servidor cierra todas las sesiones al cambiarla, así que el token que
   * este navegador tenía guardado deja de valer en ese mismo instante. Si no
   * se sustituyera por el que devuelve la llamada, el usuario se encontraría
   * expulsado en la siguiente petición justo después de haber hecho lo
   * correcto.
   *
   * Si algo falla no se toca el estado: la sesión anterior sigue siendo válida
   * porque el servidor no llegó a revocar nada.
   */
  async function changePassword(actual, nueva) {
    // `?? null` para coincidir con lo que el contexto expone como `token`: sin
    // él saldría `undefined`, que significa lo mismo pero obliga a quien lea
    // esto a comprobar dos formas distintas de «no hay token».
    const { user, accessToken } = await changePasswordApi(auth?.token ?? null, actual, nueva);
    setAuthToken(accessToken);
    setAuth({ user, token: accessToken });
  }

  // Lo que reciben los componentes con useAuth().
  const value = {
    user: auth?.user ?? null,
    token: auth?.token ?? null,
    isAuthenticated: !!auth?.token,
    login,
    register,
    logout,
    changePassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Acceso a la sesión desde cualquier componente.
 *
 * @returns el valor del contexto (ver arriba)
 * @throws {Error} si se usa fuera de `AuthProvider`
 */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return ctx;
}
