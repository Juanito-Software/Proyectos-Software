import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthForm from './components/AuthForm';
import TaskList from './components/TaskList';
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
        <div className="auth-container">
          <AuthForm
            mode={authMode}
            onSubmit={handleAuth}
            onSwitch={() => {
              setAuthMode((m) => (m === 'login' ? 'register' : 'login'));
              setAuthError(null);
            }}
            error={authError}
          />
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
