import { useState } from 'react';
import {
  MIN_PASSWORD_LENGTH,
  MAX_PASSWORD_LENGTH,
  PASSWORD_PATTERN,
  estadoRequisitos,
  validarPasswordCliente,
} from '../passwordPolicy';

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

  // Qué requisitos lleva cumplidos, para ir marcándolos según escribe. Solo se
  // calcula en el registro; al entrar la política no se aplica.
  const requisitos = isLogin ? null : estadoRequisitos(password);

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

      // Longitud y composición. Es solo experiencia de uso: quien se salte el
      // formulario se encontrará la misma comprobación en el servidor.
      const problema = validarPasswordCliente(password);
      if (problema) {
        setLocalError(problema);
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
          // Longitud y composición solo se exigen en el registro. Al entrar no
          // se aplican, porque las cuentas creadas con la política anterior
          // siguen siendo válidas y deben poder iniciar sesión.
          minLength={isLogin ? undefined : MIN_PASSWORD_LENGTH}
          maxLength={MAX_PASSWORD_LENGTH}
          pattern={isLogin ? undefined : PASSWORD_PATTERN}
          title={
            isLogin
              ? undefined
              : 'Al menos una mayúscula, un número y un símbolo'
          }
          autoComplete={isLogin ? 'current-password' : 'new-password'}
          disabled={loading}
          aria-describedby={isLogin ? undefined : 'requisitos-password'}
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

            {/* Se marcan según se escriben en lugar de soltarlos todos al
                enviar: con cuatro requisitos, descubrirlos de uno en uno a
                base de intentos fallidos es lo que acaba en "Password123!". */}
            <ul id="requisitos-password" className="password-requirements">
              <Requisito cumplido={requisitos.longitud}>
                Al menos {MIN_PASSWORD_LENGTH} caracteres
              </Requisito>
              <Requisito cumplido={requisitos.mayuscula}>Al menos una letra mayúscula</Requisito>
              <Requisito cumplido={requisitos.digito}>Al menos un número</Requisito>
              <Requisito cumplido={requisitos.simbolo}>
                Al menos un símbolo (! ? # $ % &amp; * - _ …)
              </Requisito>
            </ul>

            <p className="field-hint">
              Una frase con algún retoque cumple todo sin ser difícil de recordar — por ejemplo,{' '}
              <em>Café con leche y 2 tostadas!</em>
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

/**
 * Una línea de la lista de requisitos.
 *
 * El estado no se transmite solo con el color: lleva el símbolo (✓ / ·) y un
 * texto oculto para lectores de pantalla, porque distinguir verde de gris no
 * está al alcance de todo el mundo.
 */
function Requisito({ cumplido, children }) {
  return (
    <li
      className={cumplido ? 'requirement requirement--ok' : 'requirement'}
      data-cumplido={cumplido ? 'si' : 'no'}
    >
      <span aria-hidden="true">{cumplido ? '✓' : '·'}</span>{' '}
      <span className="sr-only">{cumplido ? 'Cumplido:' : 'Pendiente:'}</span> {children}
    </li>
  );
}
