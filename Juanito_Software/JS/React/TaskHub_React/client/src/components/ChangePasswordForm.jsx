import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  MIN_PASSWORD_LENGTH,
  MAX_PASSWORD_LENGTH,
  PASSWORD_PATTERN,
  estadoRequisitos,
  validarPasswordCliente,
} from '../passwordPolicy';

/**
 * Cambio de contraseña para quien ya ha iniciado sesión.
 *
 * Pide la contraseña **actual** además de la nueva, y eso no es burocracia: un
 * token de acceso robado permitiría quedarse con la cuenta para siempre si
 * bastara con estar dentro. Exigir la actual convierte ese robo en un problema
 * de quince minutos en lugar de definitivo.
 *
 * Al terminar, el servidor cierra todas las demás sesiones. Se avisa antes de
 * enviar, no después: una acción que expulsa dispositivos debe anunciarse
 * mientras todavía se puede cancelar.
 */
export default function ChangePasswordForm({ onDone }) {
  const { changePassword } = useAuth();

  const [actual, setActual] = useState('');
  const [nueva, setNueva] = useState('');
  const [confirmacion, setConfirmacion] = useState('');
  const [error, setError] = useState(null);
  const [hecho, setHecho] = useState(false);
  const [enviando, setEnviando] = useState(false);

  const noCoinciden = confirmacion.length > 0 && nueva !== confirmacion;
  const requisitos = estadoRequisitos(nueva);

  async function handleSubmit(e) {
    e.preventDefault();
    e.stopPropagation();
    if (enviando) return;

    setError(null);

    if (!actual || !nueva) return;

    if (nueva !== confirmacion) {
      setError('Las contraseñas no coinciden');
      return;
    }

    // Misma comprobación que en el registro, y por el mismo motivo: avisar
    // antes de gastar una petición. Quien se salte el formulario se encontrará
    // la política otra vez en el servidor, que es quien decide.
    const problema = validarPasswordCliente(nueva);
    if (problema) {
      setError(problema);
      return;
    }

    if (nueva === actual) {
      setError('La contraseña nueva debe ser distinta de la actual');
      return;
    }

    setEnviando(true);
    try {
      await changePassword(actual, nueva);
      setHecho(true);
      setActual('');
      setNueva('');
      setConfirmacion('');
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  if (hecho) {
    return (
      <div className="cambio-password">
        <p className="cambio-ok" role="status">
          Contraseña cambiada. Las demás sesiones se han cerrado.
        </p>
        {onDone && (
          <button type="button" className="btn-clear-filters" onClick={onDone}>
            Cerrar
          </button>
        )}
      </div>
    );
  }

  return (
    <form className="cambio-password" onSubmit={handleSubmit}>
      <h2>Cambiar contraseña</h2>

      {error && <div className="error">{error}</div>}

      <input
        type="password"
        value={actual}
        onChange={(e) => setActual(e.target.value)}
        placeholder="Contraseña actual"
        aria-label="Contraseña actual"
        autoComplete="current-password"
        required
        disabled={enviando}
      />

      <input
        type="password"
        value={nueva}
        onChange={(e) => setNueva(e.target.value)}
        placeholder="Contraseña nueva"
        aria-label="Contraseña nueva"
        autoComplete="new-password"
        required
        minLength={MIN_PASSWORD_LENGTH}
        maxLength={MAX_PASSWORD_LENGTH}
        pattern={PASSWORD_PATTERN}
        title="Al menos una mayúscula, un número y un símbolo"
        aria-describedby="requisitos-password-nueva"
        disabled={enviando}
      />

      <input
        type="password"
        value={confirmacion}
        onChange={(e) => setConfirmacion(e.target.value)}
        placeholder="Repite la contraseña nueva"
        aria-label="Repite la contraseña nueva"
        autoComplete="new-password"
        required
        maxLength={MAX_PASSWORD_LENGTH}
        aria-invalid={noCoinciden}
        disabled={enviando}
      />

      {noCoinciden && (
        <p className="field-hint field-hint--error" role="alert">
          Las contraseñas no coinciden
        </p>
      )}

      <ul id="requisitos-password-nueva" className="password-requirements">
        <Requisito cumplido={requisitos.longitud}>
          Al menos {MIN_PASSWORD_LENGTH} caracteres
        </Requisito>
        <Requisito cumplido={requisitos.mayuscula}>Al menos una letra mayúscula</Requisito>
        <Requisito cumplido={requisitos.digito}>Al menos un número</Requisito>
        <Requisito cumplido={requisitos.simbolo}>
          Al menos un símbolo (! ? # $ % &amp; * - _ …)
        </Requisito>
      </ul>

      {/* El aviso va ANTES del botón, no en la pantalla de confirmación: cerrar
          las sesiones de otros dispositivos es una consecuencia que conviene
          conocer mientras todavía se puede dar marcha atrás. */}
      <p className="field-hint">
        Al cambiarla se cerrarán tus sesiones en el resto de dispositivos. En este
        seguirás dentro.
      </p>

      <div className="form-actions">
        <button type="submit" disabled={enviando || noCoinciden}>
          {enviando ? 'Cambiando…' : 'Cambiar contraseña'}
        </button>
        {onDone && (
          <button type="button" onClick={onDone} disabled={enviando}>
            Cancelar
          </button>
        )}
      </div>
    </form>
  );
}

/**
 * Una línea de la lista de requisitos.
 *
 * Duplicada a propósito respecto a la de `AuthForm`: son cuatro líneas y
 * extraerlas a un módulo compartido acoplaría dos formularios que pueden
 * evolucionar por separado. Si aparece un tercero, entonces sí.
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
