import { useState } from "react";
import { useAuth } from "./AuthContext";

export default function AuthPage() {
  const { login, register } = useAuth();
  const [tab, setTab] = useState("login");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [regForm, setRegForm] = useState({ email: "", username: "", password: "" });

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(loginForm.username, loginForm.password);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(regForm.email, regForm.username, regForm.password);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h1 className="auth-title">TaskHub</h1>
        <p className="auth-subtitle">Gestiona tus tareas</p>

        <div className="tabs">
          <button
            className={`tab ${tab === "login" ? "active" : ""}`}
            onClick={() => { setTab("login"); setError(""); }}
          >
            Iniciar sesión
          </button>
          <button
            className={`tab ${tab === "register" ? "active" : ""}`}
            onClick={() => { setTab("register"); setError(""); }}
          >
            Registrarse
          </button>
        </div>

        {error && <p className="error-msg">{error}</p>}

        {tab === "login" ? (
          <form onSubmit={handleLogin} className="form">
            <label>Usuario</label>
            <input
              type="text"
              value={loginForm.username}
              onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
              placeholder="tu_usuario"
              required
            />
            <label>Contraseña</label>
            <input
              type="password"
              value={loginForm.password}
              onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
              placeholder="••••••••"
              required
            />
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Entrando…" : "Entrar"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="form">
            <label>Email</label>
            <input
              type="email"
              value={regForm.email}
              onChange={(e) => setRegForm({ ...regForm, email: e.target.value })}
              placeholder="tu@email.com"
              required
            />
            <label>Usuario</label>
            <input
              type="text"
              value={regForm.username}
              onChange={(e) => setRegForm({ ...regForm, username: e.target.value })}
              placeholder="tu_usuario"
              required
            />
            <label>Contraseña</label>
            <input
              type="password"
              value={regForm.password}
              onChange={(e) => setRegForm({ ...regForm, password: e.target.value })}
              placeholder="••••••••"
              required
            />
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Creando cuenta…" : "Crear cuenta"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
