import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthForm from './components/AuthForm';
import TaskList from './components/TaskList';
import './App.css';

function AppContent() {
  const { user, isAuthenticated, login, register, logout } = useAuth();
  const [authMode, setAuthMode] = useState('login');
  const [authError, setAuthError] = useState(null);

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
