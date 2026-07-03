import { createContext, useContext, useState } from "react";
import { api } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));

  async function login(username, password) {
    const data = await api.login(username, password);
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
  }

  async function register(email, username, password) {
    await api.register({ email, username, password });
    await login(username, password);
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  return (
    <AuthContext.Provider value={{ token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
