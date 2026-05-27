import { useState } from 'react';

export default function AuthForm({ mode, onSubmit, onSwitch, error }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const isLogin = mode === 'login';

  async function handleSubmit(e) {
    e.preventDefault();
    e.stopPropagation();
    if (!username.trim() || !password || loading) return;
    setLoading(true);
    try {
      await onSubmit(username.trim(), password);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-form">
      <h2>{isLogin ? 'Iniciar sesión' : 'Crear cuenta'}</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Usuario"
          required
          autoFocus
          disabled={loading}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Contraseña"
          required
          minLength={6}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Entrando…' : isLogin ? 'Entrar' : 'Registrarse'}
        </button>
      </form>
      <p className="auth-switch">
        {isLogin ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?'}{' '}
        <button type="button" className="link" onClick={onSwitch}>
          {isLogin ? 'Regístrate' : 'Inicia sesión'}
        </button>
      </p>
    </div>
  );
}
