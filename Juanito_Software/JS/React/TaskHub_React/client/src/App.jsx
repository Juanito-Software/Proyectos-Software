import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthForm from './components/AuthForm';
import TaskList from './components/TaskList';
import ThemeToggle from './components/ThemeToggle';
import './App.css';

function AppContent() {
  const { user, isAuthenticated, login, register, logout } = useAuth();
  const [authMode, setAuthMode] = useState('login');
  const [authError, setAuthError] = useState(null);

  /**
   * Al quedarse sin sesión, el formulario vuelve a modo «iniciar sesión».
   *
   * Sin esto conservaba el modo en que estuviera: quien acababa de registrarse
   * y pulsaba Salir se encontraba otra vez la pantalla de «Crear cuenta», con
   * su campo de confirmación y sus requisitos de contraseña, cuando lo que casi
   * siempre quiere en ese momento es entrar de nuevo. Lo mismo al caducar la
   * sesión estando dentro.
   *
   * Solo se dispara cuando cambia `isAuthenticated`, así que no estorba a quien
   * pulsa «Regístrate» estando ya en la pantalla de acceso.
   */
  useEffect(() => {
    if (!isAuthenticated) {
      setAuthMode('login');
      setAuthError(null);
    }
  }, [isAuthenticated]);

  async function handleAuth(username, password) {
    setAuthError(null);
    try {
      if (authMode === 'login') {
        await login(username, password);
      } else {
        await register(username, password);
      }
    } catch (err) {
      setAuthError(err.message);
    }
  }

  if (!isAuthenticated) {
    return (
      <main className="app app--auth">
        <ThemeToggle className="tema-flotante" />

        <div className="auth-container">
          {/*
            Marca y contexto antes del formulario.
            Antes esta pantalla era una tarjeta con dos campos y nada más: quien
            llegaba desde un enlace no sabía qué era esto ni por qué debería
            crearse una cuenta. Pedir un registro para averiguarlo es pedir
            demasiado.
          */}
          <div className="auth-brand">
            <div className="auth-logo" aria-hidden="true">
              T
            </div>
            <h1>TaskHub</h1>
            <p className="auth-tagline">
              Gestor de tareas multiusuario. Cada cuenta ve únicamente sus tareas.
            </p>
          </div>

          <AuthForm
            mode={authMode}
            onSubmit={handleAuth}
            onSwitch={() => {
              setAuthMode((m) => (m === 'login' ? 'register' : 'login'));
              setAuthError(null);
            }}
            error={authError}
          />

          <p className="auth-footer">
            <a href="/playground">Playground de la API</a>
            <span className="sep" aria-hidden="true">
              ·
            </span>
            <a
              href="https://github.com/Juanito-Software/Proyectos-Software/tree/main/Juanito_Software/JS/React/TaskHub_React"
              target="_blank"
              rel="noopener noreferrer"
            >
              Código y documentación
            </a>
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="app">
      <TaskList user={user} onLogout={logout} />
    </main>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
