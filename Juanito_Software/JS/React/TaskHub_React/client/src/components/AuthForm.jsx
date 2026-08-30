import { useState } from 'react';
import { MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH } from '../constants';

export default function AuthForm({ mode, onSubmit, onSwitch, error }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [localError, setLocalError] = useState(null);
  const [loading, setLoading] = useState(false);

  const isLogin = mode === 'login';

  // Solo se avisa de que no coinciden cuando ya se ha escrito algo en el
  // segundo campo: si no, saldría un error nada más empezar a teclear.
  const mismatch = !isLogin && confirmation.length > 0 && password !== confirmation;

  async function handleSubmit(e) {
    e.preventDefault();
    e.stopPropagation();
    if (loading) return;

    setLocalError(null);

    if (!username.trim() || !password) return;

    if (!isLogin) {
      // La confirmación es asunto del formulario: se comprueba aquí y no
      // llega a viajar a la API, que sigue recibiendo solo username y
      // password.
      if (password !== confirmation) {
        setLocalError('Las contraseñas no coinciden');
        return;
      }
      if (password.length < MIN_PASSWORD_LENGTH) {
        setLocalError(`La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres`);
        return;
      }
    }

    setLoading(true);
    try {
      await onSubmit(username.trim(), password);
    } finally {
      setLoading(false);
    }
  }

  function switchMode() {
    // Al cambiar de modo se limpia la confirmación: si no, quedaría un valor
    // del registro anterior estorbando.
    setConfirmation('');
    setLocalError(null);
    onSwitch();
  }

  return (
    <div className="auth-form">
      <h2>{isLogin ? 'Iniciar sesión' : 'Crear cuenta'}</h2>

      {(error || localError) && <div className="error">{localError || error}</div>}

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Usuario"
          aria-label="Usuario"
          required
          autoFocus
          disabled={loading}
        />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Contraseña"
          aria-label="Contraseña"
          required
          // Solo se exige la longitud en el registro. Al entrar no se aplica,
          // porque las cuentas creadas con la política anterior siguen siendo
          // válidas y deben poder iniciar sesión.
          minLength={isLogin ? undefined : MIN_PASSWORD_LENGTH}
          maxLength={MAX_PASSWORD_LENGTH}
          autoComplete={isLogin ? 'current-password' : 'new-password'}
          disabled={loading}
        />

        {!isLogin && (
          <>
            <input
              type="password"
              value={confirmation}
              onChange={(e) => setConfirmation(e.target.value)}
              placeholder="Repite la contraseña"
              aria-label="Repite la contraseña"
              required
              maxLength={MAX_PASSWORD_LENGTH}
              autoComplete="new-password"
              disabled={loading}
              aria-invalid={mismatch}
            />

            {mismatch && (
              <p className="field-hint field-hint--error" role="alert">
                Las contraseñas no coinciden
              </p>
            )}

            {/* Con un mínimo de 15 caracteres, decir solo "mínimo 15" empuja a
                inventar algo difícil de recordar. Sugerir una frase es lo que
                hace la política llevadera. */}
            <p className="field-hint">
              Mínimo {MIN_PASSWORD_LENGTH} caracteres. Una frase que recuerdes funciona mejor que
              una palabra corta con símbolos — por ejemplo, <em>café con leche y dos tostadas</em>.
            </p>
          </>
        )}

        <button type="submit" disabled={loading || mismatch}>
          {loading ? 'Entrando…' : isLogin ? 'Entrar' : 'Registrarse'}
        </button>
      </form>

      <p className="auth-switch">
        {isLogin ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?'}{' '}
        <button type="button" className="link" onClick={switchMode}>
          {isLogin ? 'Regístrate' : 'Inicia sesión'}
        </button>
      </p>
    </div>
  );
}
