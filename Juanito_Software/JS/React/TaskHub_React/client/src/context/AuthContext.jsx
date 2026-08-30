import { createContext, useContext, useState, useEffect } from 'react';
import { login as loginApi, register as registerApi } from '../services/authApi';
import { setAuthToken } from '../services/api';

const AuthContext = createContext(null);

const STORAGE_KEY = 'taskhub_auth';

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

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(loadStoredAuth);

  useEffect(() => {
    if (auth) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
      setAuthToken(auth.token);
    } else {
      localStorage.removeItem(STORAGE_KEY);
      setAuthToken(null);
    }
  }, [auth]);

  async function login(username, password) {
    const { user, token } = await loginApi(username, password);
    setAuthToken(token);
    setAuth({ user, token });
  }

  async function register(username, password) {
    const { user, token } = await registerApi(username, password);
    setAuthToken(token);
    setAuth({ user, token });
  }

  function logout() {
    setAuth(null);
  }

  const value = {
    user: auth?.user ?? null,
    token: auth?.token ?? null,
    isAuthenticated: !!auth?.token,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return ctx;
}
